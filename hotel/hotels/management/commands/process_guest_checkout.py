import time
from django.core.management.base import BaseCommand
from django.db import OperationalError, close_old_connections
from django.utils import timezone
from ...models import Booking, Payment
from ...guest_booking_email import send_checkout_email, inspect_failure
from ...guest_email_lock import email_delivery_lock


class Command(BaseCommand):
    help = 'Process guest emails without keeping SQLite cursors open during network requests.'

    def add_arguments(self, parser):
        parser.add_argument('--loop', action='store_true')
        parser.add_argument('--interval', type=int, default=60)

    def run_cycle(self):
        paid = Payment.objects.filter(status__in=['paid', 'refunded']).values('booking_id')
        count = Booking.objects.filter(payment_method='online', booking_status='pending',
            expires_at__lte=timezone.now()).exclude(payment_status__in=['paid', 'refunded']).exclude(pk__in=paid).update(booking_status='cancelled')
        initial = failure = 0
        last_pk = 0
        while True:
            # Materialize a bounded batch: never retain a streaming SQLite read
            # cursor while sending mail, calling ZainCash, or writing updates.
            ids = list(Booking.objects.filter(user__isnull=True, payment_method='online',
                booking_status='pending', expires_at__gt=timezone.now(), pk__gt=last_pk)
                .exclude(payment_status__in=['paid', 'refunded']).order_by('pk').values_list('pk', flat=True)[:100])
            if not ids:
                break
            for booking_id in ids:
                initial += int(send_checkout_email(booking_id))
                try:
                    failure += int(inspect_failure(booking_id))
                except Exception:
                    self.stderr.write(f'Booking {booking_id}: check deferred until the next cycle.')
            last_pk = ids[-1]
        self.stdout.write(f'Initial emails: {initial}; failure emails: {failure}; expired bookings: {count}')

    def handle(self, *args, **options):
        interval = max(30, options['interval'])
        # Prevent accidentally starting this worker twice on the same host.
        with email_delivery_lock('worker', 'process_guest_checkout') as acquired:
            if not acquired:
                self.stderr.write('A guest checkout worker is already running. Keep only one worker open.')
                return
            try:
                while True:
                    close_old_connections()
                    try:
                        self.run_cycle()
                    except OperationalError as exc:
                        if 'locked' not in str(exc).lower():
                            raise
                        self.stderr.write('SQLite is busy. No database reset is needed; retrying next cycle.')
                    finally:
                        close_old_connections()
                    if not options['loop']:
                        return
                    time.sleep(interval)
            except KeyboardInterrupt:
                self.stdout.write('Guest checkout worker stopped.')
