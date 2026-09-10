from django.core import signing
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Booking
from .serializers import BookingSerializer

SALT = "najafdo.guest-checkout.v1"
MAX_AGE = 24 * 60 * 60


def issue_guest_access(booking):
    if booking.user_id is not None:
        return None
    return signing.dumps({"booking_id": booking.pk, "scope": "guest-checkout"}, salt=SALT)


def can_access_checkout(request, booking):
    user = request.user
    if user.is_authenticated and (user.is_staff or booking.user_id == user.pk):
        return True
    # A guest capability must never grant access to an account-owned booking.
    if booking.user_id is not None:
        return False
    token = request.query_params.get("access_token") or request.data.get("access_token")
    if not isinstance(token, str) or not token:
        return False
    try:
        payload = signing.loads(token, salt=SALT, max_age=MAX_AGE)
    except (signing.BadSignature, ValueError, TypeError):
        return False
    return (
        isinstance(payload, dict)
        and payload.get("scope") == "guest-checkout"
        and str(payload.get("booking_id")) == str(booking.pk)
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def checkout_booking(request, booking_id):
    booking = Booking.objects.filter(pk=booking_id).first()
    if booking is None or not can_access_checkout(request, booking):
        return Response({"error": "Booking access is missing, invalid or expired."}, status=403)
    if booking.payment_status != "paid" and booking.expires_at and booking.expires_at <= timezone.now():
        return Response({"error": "This booking has expired."}, status=410)
    # Preserve the response shape expected by PaymentPage.
    response = Response(BookingSerializer(booking, context={"request": request}).data)
    response["Cache-Control"] = "private, no-store"
    response["Referrer-Policy"] = "no-referrer"
    return response
