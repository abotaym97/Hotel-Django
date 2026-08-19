from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import Booking


class Command(BaseCommand):
    help = "Cancel pending bookings that have expired"

    def handle(self, *args, **options):

        expired_bookings = Booking.objects.filter(
            booking_status="pending",
            expires_at__lte=timezone.now()
        )

        count = expired_bookings.update(
            booking_status="cancelled"
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"{count} expired booking(s) cancelled."
            )
        )