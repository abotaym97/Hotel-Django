"""Restricted diagnostic snapshots; never persist gateway payloads or credentials."""
import logging
import re
from decimal import Decimal, InvalidOperation
from functools import wraps
from .models import Payment, PaymentEvent, PaymentInspection

log = logging.getLogger(__name__)
STATUSES = {'SUCCESS','FAILED','EXPIRED','PENDING','OTP_SENT','CUSTOMER_AUTHENTICATION_REQUIRED','REFUNDED','PARTIALLY_REFUNDED'}


def safe_message(value):
    if not isinstance(value, str):
        return ''
    value = re.sub(r'https?://\S+|[\w.+-]+@[\w.-]+|\b[A-Za-z0-9_-]{20,}(?:\.[A-Za-z0-9_-]+)*\b', '[redacted]', value)
    value = re.sub(r'(?i)(token|secret|password|authorization|otp|pin)\s*[:=]\s*\S+', r'\1=[redacted]', value)
    value = re.sub(r'\d{4,}', '[redacted]', value)
    return value[:400]


def snapshot(payment, payload, http_status=None):
    payload = payload if isinstance(payload, dict) else {}
    details = payload.get('transactionDetails') or {}
    details = details if isinstance(details, dict) else {}
    state = str(payload.get('status') or details.get('status') or '').upper().strip()
    amount = details.get('amount') or {}
    try:
        matched = (str(details.get('transactionId')) == str(payment.transaction_id)
            and bool(payment.external_reference) and str(details.get('externalReferenceId')) == str(payment.external_reference)
            and str(details.get('orderId')) == str(payment.booking_id)
            and str(amount.get('currency')).upper() == payment.currency.upper()
            and Decimal(str(amount.get('value'))) == payment.amount)
    except (InvalidOperation, AttributeError, ValueError, TypeError):
        matched = False
    code = str(payload.get('errorCode') or payload.get('code') or '')
    code = code if re.fullmatch(r'[A-Z][A-Z0-9-]{0,39}', code) else ''
    message = safe_message(payload.get('errorMessage') or payload.get('message') or '')
    return {'gateway_status':state if state in STATUSES else '', 'matched':bool(matched),
            'http_status':http_status, 'error_code':code, 'error_message':message}


def record(payment, kind, data, source='gateway', inspection=False):
    try:
        if inspection:
            old = PaymentInspection.objects.filter(payment=payment).first()
            changed = old is None or any(getattr(old,key) != value for key,value in data.items())
            PaymentInspection.objects.update_or_create(payment=payment, defaults=data)
            if not changed and source != 'admin':
                return
        PaymentEvent.objects.create(payment=payment,kind=kind,source=source,**data)
    except Exception:
        # Observability must not turn successful payment initialization into a failure.
        log.warning('Unable to persist payment diagnostic for payment %s', payment.pk)


def instrument(function, kind):
    @wraps(function)
    def wrapped(*args, **kwargs):
        payment = None
        try:
            if kind == 'inquiry':
                txid = args[0] if args else kwargs.get('transaction_id')
                payment = Payment.objects.filter(transaction_id=txid).first()
            else:
                booking_id = args[0] if args else kwargs.get('booking_id')
                payment = Payment.objects.filter(booking_id=booking_id,gateway='zaincash').order_by('-created_at','-pk').first()
        except Exception:
            pass
        try:
            result = function(*args, **kwargs)
        except Exception as exc:
            if payment:
                response = getattr(exc,'response',None)
                status = getattr(response,'status_code',None)
                # Do not store arbitrary exception text or raw response bodies.
                try:
                    payload = response.json() if response is not None else {}
                except Exception:
                    payload = {}
                data = snapshot(payment, payload, status)
                data['matched'] = False
                data['error_code'] = data['error_code'] or 'GATEWAY_REQUEST_ERROR'
                data['error_message'] = data['error_message'] or 'Gateway request failed; inspect provider support logs.'
                record(payment,kind+'_error',data,inspection=kind=='inquiry')
            raise
        if payment:
            data = snapshot(payment,result,None)
            if kind == 'init':
                # SUCCESS on /init means session creation, not a successful charge.
                data['gateway_status']=''
                data['matched']=False
            record(payment,kind,data,inspection=kind=='inquiry')
        return result
    return wrapped


def audit_verification(function):
    @wraps(function)
    def wrapped(request, booking_id, *args, **kwargs):
        result = function(request, booking_id, *args, **kwargs)
        try:
            payment=Payment.objects.filter(booking_id=booking_id,gateway='zaincash').order_by('-created_at','-pk').first()
            if payment:
                # Only record the outcome of verification, never request query/token.
                record(payment,'verification_result',{'http_status':result.status_code,
                    'gateway_status':'','matched':False,'error_code':'',
                    'error_message':'Verification endpoint completed. Check local payment status.'},source='verification')
        except Exception:
            pass
        return result
    return wrapped
