from django.contrib import admin
from .models import ActivityLog,MealOption,SystemSetting,DashboardCardSetting,Notification,ContactSetting,ContactMessage, CustomerProfile, Hotel, Restaurant, Review ,  Room ,  Booking, RoomType , NearbyPlace, Service , Gallery ,BookingSettings ,Profile ,GalleryImage


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
admin.site.register(Review)
admin.site.register(ActivityLog)
admin.site.register(ContactSetting)
admin.site.register(ContactMessage)
admin.site.register(Notification)
admin.site.register(DashboardCardSetting)
admin.site.register(SystemSetting)
admin.site.register(MealOption)




from .models import Gallery, GalleryImage


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1


class GalleryAdmin(admin.ModelAdmin):
    inlines = [GalleryImageInline]


admin.site.register(Gallery, GalleryAdmin)