"""Guest checkout mail, using the original booking deadline and mail backend."""
import logging
from urllib.parse import urlencode, urlsplit
from zoneinfo import ZoneInfo
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction, OperationalError
from .guest_email_lock import email_delivery_lock
import time
from django.utils import timezone
from django.utils.html import format_html
from .models import Booking, Payment
from .guest_access import issue_guest_access
from .payment_retry import require_terminal_failure, RetryBlocked

logger = logging.getLogger(__name__)


def eligible(booking):
    return (booking.user_id is None and booking.payment_method == 'online'
            and booking.booking_status == 'pending' and booking.payment_status not in {'paid', 'refunded'}
            and bool(booking.guest_email) and booking.expires_at is not None
            and booking.expires_at > timezone.now())


def send_checkout_email(booking_id, failed=False):
    """Retryable delivery. One initial email and one failure email per booking.

    SMTP acknowledgement followed by a process crash can still cause a duplicate;
    no SMTP-based implementation can promise exactly-once delivery.
    """
    field = 'guest_failure_email_sent_at' if failed else 'guest_checkout_email_sent_at'
    try:
        with email_delivery_lock(booking_id, field) as acquired:
            if not acquired:
                return False
            booking = Booking.objects.filter(pk=booking_id).first()
            if booking is None or not eligible(booking) or getattr(booking, field):
                return False
            if Payment.objects.filter(booking=booking, status__in=['paid', 'refunded']).exists():
                return False
            if failed:
                latest = Payment.objects.filter(booking=booking, gateway='zaincash').order_by('-created_at', '-pk').first()
                if latest is None or latest.status != 'failed':
                    return False
            frontend = getattr(settings, 'FRONTEND_URL', '').rstrip('/')
            parsed = urlsplit(frontend)
            if parsed.scheme not in {'http', 'https'} or not parsed.netloc or parsed.query or parsed.fragment:
                raise ValueError('Set FRONTEND_URL to the public frontend origin')
            token = issue_guest_access(booking)
            if not token:
                return False
            # Fragment is consumed locally by React, not sent in the page request.
            url = f"{frontend}/payment/{booking.pk}#{urlencode({'access_token': token})}"
            deadline = timezone.localtime(booking.expires_at, ZoneInfo('Asia/Baghdad')).strftime('%Y-%m-%d %H:%M')
            title = 'لم تكتمل عملية الدفع' if failed else 'رابط متابعة حجزك'
            message = ('أكدت بوابة الدفع فشل المحاولة السابقة أو انتهاء صلاحيتها. يمكنك إعادة المحاولة من الرابط أدناه.'
                       if failed else 'تم إنشاء طلب حجزك وهو بانتظار الدفع. احتفظ بهذا الرابط للعودة إلى الحجز حتى إذا أغلقت الصفحة.')
            text = (f'{title} — Najaf Do Hotel\n\n{message}\n'
                    f'رقم الحجز: {booking.booking_code}\n'
                    f'الحجز معلّق لمدة 24 ساعة من إنشائه، حتى {deadline} بتوقيت بغداد.\n'
                    'إعادة المحاولة لا تمدد هذه المهلة. الحجز غير مؤكد قبل نجاح الدفع.\n\n'
                    f'إكمال دفع الحجز:\n{url}\n\n'
                    'الرابط خاص بحجزك؛ لا تشاركه مع الآخرين. إذا لم تطلب هذا الحجز، تجاهل الرسالة.')
            html = format_html('''<div dir="rtl" style="font-family:Tahoma,Arial,sans-serif;background:#11110f;color:#eee;padding:32px;line-height:1.9;max-width:600px;margin:auto">
              <p style="color:#d4ad55;letter-spacing:2px" dir="ltr">NAJAF DO HOTEL</p>
              <h2>{}</h2><p>{}</p><p>رقم الحجز: <b dir="ltr">{}</b></p>
              <p>الحجز معلّق لمدة 24 ساعة من إنشائه، حتى <b dir="ltr">{}</b> بتوقيت بغداد.</p>
              <p>إعادة المحاولة لا تمدد المهلة. الحجز غير مؤكد قبل نجاح الدفع.</p>
              <p style="margin:28px 0"><a href="{}" style="background:#cfaa55;color:#15130c;padding:14px 24px;text-decoration:none;border-radius:6px">إكمال دفع الحجز</a></p>
              <p style="font-size:12px;color:#bbb">الرابط خاص بحجزك؛ لا تشاركه مع الآخرين. إذا لم تطلب هذا الحجز، تجاهل الرسالة.</p></div>''', title, message, booking.booking_code, deadline, url)
            from django.core.mail import get_connection
            connection = get_connection(timeout=30)
            mail = EmailMultiAlternatives(f'{title} — {booking.booking_code}', text,
                                          settings.DEFAULT_FROM_EMAIL, [booking.guest_email], connection=connection)
            mail.attach_alternative(str(html), 'text/html')
            if mail.send(fail_silently=False) != 1:
                return False
            # Retry only the database acknowledgement, never the SMTP send.
            for attempt in range(5):
                try:
                    Booking.objects.filter(pk=booking.pk).update(**{field: timezone.now()})
                    break
                except OperationalError as exc:
                    if "locked" not in str(exc).lower() or attempt == 4:
                        raise
                    time.sleep(0.25 * (2 ** attempt))
            return True
    except Exception:
        # Avoid recording email addresses, checkout tokens or SMTP credentials.
        logger.warning('Guest checkout email delivery deferred for booking %s', booking_id)
        return False


def inspect_failure(booking_id):
    from .zaincash import inquiry_payment
    booking = Booking.objects.filter(pk=booking_id).first()
    if booking is None or not eligible(booking):
        return False
    latest = Payment.objects.filter(booking=booking, gateway='zaincash').order_by('-created_at', '-pk').first()
    if latest is None or not latest.transaction_id:
        return False
    if latest.status in {'paid', 'refunded'}:
        return False
    if latest.status == 'failed' and booking.guest_failure_email_sent_at:
        return False
    # The return URL and browser error are never proof of failure.
    try:
        require_terminal_failure(latest, booking, inquiry_payment)
    except RetryBlocked:
        return False
    with transaction.atomic():
        locked = Booking.objects.select_for_update().get(pk=booking_id)
        current = Payment.objects.filter(booking=locked, gateway='zaincash').order_by('-created_at', '-pk').first()
        if not eligible(locked) or current is None or current.pk != latest.pk or current.transaction_id != latest.transaction_id:
            return False
        if current.status in {'paid', 'refunded'}:
            return False
        current.status = 'failed'
        current.save(update_fields=['status'])
    return send_checkout_email(booking_id, failed=True)
