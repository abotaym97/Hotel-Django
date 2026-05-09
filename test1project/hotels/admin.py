from django.contrib import admin
from .models import CustomerProfile, Hotel ,  Room ,  Booking, RoomType
from .models import BookingSettings


admin.site.register(Hotel)
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(BookingSettings)
admin.site.register(RoomType)
admin.site.register(CustomerProfile)