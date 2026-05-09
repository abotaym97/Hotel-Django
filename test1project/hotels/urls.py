from . import views
from django.urls import path
from .views import booking_settings,all_bookings,dashboard_stats, delete_booking, delete_room, get_hotels , get_rooms , bookings , available_rooms , booking_detail , register , my_bookings , profile, hotel_detail, room_types, rooms_by_hotel, update_room


urlpatterns = [
    path('hotels/' , get_hotels),
    path('rooms/' , get_rooms),
    path('bookings/' , bookings),
    path('available_rooms/',available_rooms),
    path('bookings/<int:id>/', booking_detail),
    path('register/', register),
    path('my-bookings/', my_bookings),
    path('profile/', profile),
    path('hotels/<int:id>/', hotel_detail),
    path('hotels/<int:hotel_id>/rooms/', rooms_by_hotel),
    path('register/', register),
    path('booking-settings/', booking_settings),
    path('dashboard-stats/', dashboard_stats),
    path('all-bookings/', all_bookings),
    path('rooms/<int:pk>/', delete_room),
    path('rooms/<int:pk>/update/', update_room),
    path('bookings/<int:pk>/', delete_booking),
    path('room-types/', room_types),
    path("room-types/<int:pk>/", views.room_type_detail),
]