from django.contrib import admin
from .models import CustomerProfile, Hotel, Restaurant ,  Room ,  Booking, RoomType , NearbyPlace, Service , Gallery ,BookingSettings ,Profile ,GalleryImage


admin.site.register(Hotel)
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(BookingSettings)
admin.site.register(RoomType)
admin.site.register(CustomerProfile)
admin.site.register(Profile)
admin.site.register(Restaurant)
admin.site.register(NearbyPlace)
admin.site.register(Service)


from django.contrib import admin
from .models import Gallery, GalleryImage


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1


class GalleryAdmin(admin.ModelAdmin):
    inlines = [GalleryImageInline]


admin.site.register(Gallery, GalleryAdmin)