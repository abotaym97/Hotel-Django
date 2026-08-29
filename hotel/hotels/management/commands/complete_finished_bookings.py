from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import Booking


class Command(BaseCommand):
    help = "Mark confirmed bookings as completed after 12:00 PM on checkout day"

    def handle(self, *args, **options):
        now = timezone.localtime()
        today = now.date()

        # Before 12:00 PM:
        # Complete only bookings whose checkout date has already passed.
        if now.hour < 12:
            finished_bookings = Booking.objects.filter(
                booking_status="confirmed",
                check_out__lt=today,
            )

        # 12:00 PM or later:
        # Also complete today's checkout bookings.
        else:
            finished_bookings = Booking.objects.filter(
                booking_status="confirmed",
                check_out__lte=today,
            )

        count = finished_bookings.update(
            booking_status="completed"
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"{count} booking(s) marked as completed."
            )
        )