from django.contrib import admin
from .models import Hotel ,  Room ,  Booking
from .models import BookingSettings


admin.site.register(Hotel)
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(BookingSettings)