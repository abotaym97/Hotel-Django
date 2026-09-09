"""Validate provider inquiry before authorizing a new payment attempt."""
from decimal import Decimal, InvalidOperation


class RetryBlocked(Exception):
    pass


def require_terminal_failure(payment, booking, inquiry):
    if not payment.transaction_id or str(payment.transaction_id).startswith("checkout-starting-"):
        raise RetryBlocked("The previous payment initialization is unresolved. Contact the hotel before retrying.")
    try:
        result = inquiry(payment.transaction_id)
    except Exception as exc:
        raise RetryBlocked("Unable to check the previous payment with ZainCash. Please try again later.") from exc
    try:
        details = result["transactionDetails"]
        amount = details["amount"]
        matches = (
            str(details["transactionId"]) == str(payment.transaction_id)
            and bool(payment.external_reference)
            and str(details["externalReferenceId"]) == str(payment.external_reference)
            and str(details["orderId"]) == str(booking.id)
            and str(amount["currency"]).upper() == str(payment.currency).upper()
            and Decimal(str(amount["value"])) == Decimal(str(payment.amount))
        )
        status = str(result.get("status") or details.get("status") or "").upper().strip()
    except (KeyError, TypeError, AttributeError, ValueError, InvalidOperation) as exc:
        raise RetryBlocked("ZainCash returned incomplete payment information. No new payment was started.") from exc
    if not matches:
        raise RetryBlocked("The payment inquiry does not match this booking. Contact the hotel.")
    if status in {"FAILED", "EXPIRED"}:
        return status
    if status == "SUCCESS":
        raise RetryBlocked("ZainCash reports a successful payment. Do not pay again; contact the hotel to confirm your booking.")
    if status in {"REFUNDED", "PARTIALLY_REFUNDED"}:
        raise RetryBlocked("This payment has a refund status. Contact the hotel before making another payment.")
    if status in {"PENDING", "OTP_SENT", "CUSTOMER_AUTHENTICATION_REQUIRED"}:
        raise RetryBlocked("The previous ZainCash attempt is still active. Wait until ZainCash marks it failed or expired, then try again. No new payment was started.")
    raise RetryBlocked("The previous payment status is unknown. No new payment was started.")
