from urllib import request

from rest_framework.decorators import api_view, parser_classes , permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , IsAdminUser , AllowAny
from rest_framework import status
from .serializers import ActivityLogSerializer, GalleryImageSerializer, RegisterSerializer, RestaurantSerializer, ReviewSerializer, RoomTypeSerializer , UserSerializer
from .models import ActivityLog, GalleryImage, Hotel, NearbyPlace, Profile, Restaurant, Review , Room , Booking , BookingSettings, RoomType, Service , Gallery
from .serializers import HotelSerializer , RoomSerializer , BookingSerializer , BookingSettingsSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from django.db.models import ProtectedError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import NearbyPlaceSerializer ,ContactMessageSerializer,SystemSettingSerializer,ContactSettingSerializer, RestaurantSerializer , ServiceSerializer , GallerySerializer,ReviewSerializer
from django.contrib.auth.models import User, Group
from .serializers import StaffUserSerializer, HeroSlideSerializer , CurrencySerializer, HotelSettingsSerializer, NotificationSerializer ,DashboardCardSettingSerializer , MealOptionSerializer
from django.contrib.auth.models import Group, Permission
from django.utils.timezone import now
from .models import ContactSetting,Currency ,ContactMessage,DashboardCardSetting,SystemSetting
from .models import Notification ,SiteSetting
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Profile ,SocialMediaSetting,PolicySetting,Facility,AutoCloseSetting,UserTableSetting, CustomerProfile ,Amenity, CustomerRecord , MealOption ,HotelSettings , HeroSlide
from .serializers import (AdminProfileListSerializer,SocialMediaSettingSerializer,PolicySettingSerializer,FacilitySerializer,UserTableSettingSerializer,AmenitySerializer,AdminProfileDetailSerializer,CustomerRecordSerializer)
from django.utils.timezone import now
from datetime import timedelta
from decimal import Decimal
from datetime import datetime
from rest_framework.parsers import MultiPartParser, FormParser




def create_notification(title, message, notification_type):
    Notification.objects.create(
        title=title,
        message=message,
        notification_type=notification_type
    )



# Utility function to create activity logs
def create_log(user, action, target=""):

    ActivityLog.objects.create(
        user=user,
        action=action,
        target=target
    )









@api_view(["GET"])
@permission_classes([IsAdminUser])
def notifications(request):
    notifications = Notification.objects.all().order_by("-created_at")
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)

@api_view(["PUT"])
@permission_classes([IsAdminUser])
def notification_detail(request, pk):
    notification = Notification.objects.get(id=pk)
    notification.is_read = True
    notification.save()
    return Response({"message": "Notification marked as read"})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_hotels(request):
    hotels = Hotel.objects.all()
    serializer = HotelSerializer(hotels , many = True)
    return Response(serializer.data)



@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def currencies(request):
    # get
    if request.method == "GET":
        data = Currency.objects.all()
        serializer = CurrencySerializer(data, many=True)
        return Response(serializer.data)
    
    # post
    if not request.user.is_staff:
        return Response({"detail":"Unauthorized"} , status=403)
    serializer = CurrencySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        create_log(request.user, "Changed Currency", Currency.name)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(["PUT", "DELETE"])
@permission_classes([IsAdminUser])
def currency_detail(request, pk):
    try:
        currency = Currency.objects.get(id=pk)
    except Currency.DoesNotExist:
        return Response({"error": "Currency not found"}, status=404)
    if request.method == "PUT":
        if request.data.get("is_active") == True:
            Currency.objects.all().update(is_active=False)
        serializer = CurrencySerializer(currency, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    currency.delete()
    return Response(status=204)



@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def get_rooms(request):
    if request.method == 'GET':
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)
# post
    if request.method == 'POST':
        serializer = RoomSerializer(data=request.data)

        if serializer.is_valid():
            room = serializer.save()
            create_log(request.user, "Created Room", f"{room.room_type.name} - Room {room.room_number}")
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)
    


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_room(request, pk):

    try:
        room = Room.objects.get(id=pk)

    except Room.DoesNotExist:
        return Response(
            {"error": "Room not found"},
            status=404
        )
    create_log(
        request.user,
        "Deleted Room",
        f"{room.room_type.name} - Room {room.room_number}"
    )

    room.delete()

    return Response(
        {"message": "Room deleted"},
        status=200
    )




@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def update_room(request, pk):

    try:
        room = Room.objects.get(id=pk)

    except Room.DoesNotExist:
        return Response(
            {"error": "Room not found"},
            status=404
        )

    serializer = RoomSerializer(
        room,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        create_log(
            request.user,
            "Updated Room",
            f"{room.room_type.name} - Room {room.room_number}"
        )
        return Response(serializer.data)

    return Response(serializer.errors, status=400)



@api_view(["GET"])
@permission_classes([AllowAny])
def meal_options(request):
    options = MealOption.objects.filter(is_active=True)
    serializer = MealOptionSerializer(options, many=True)
    return Response(serializer.data)



@api_view(["PUT", "DELETE"])
@permission_classes([IsAdminUser])
def admin_meal_option_detail(request, meal_id):
    try:
        meal = MealOption.objects.get(id=meal_id)
    except MealOption.DoesNotExist:
        return Response({"error": "Meal not found"}, status=404)

    if request.method == "PUT":
        serializer = MealOptionSerializer(meal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == "DELETE":
        meal.delete()
        return Response({"message": "Deleted"}, status=204)


@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def admin_meal_options(request):
    if request.method == "GET":
        options = MealOption.objects.all()
        serializer = MealOptionSerializer(options, many=True)
        return Response(serializer.data)

    serializer = MealOptionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)

@api_view(["PUT"])
@permission_classes([IsAdminUser])
def toggle_meal_option(request, meal_id):

    meal = MealOption.objects.get(id=meal_id)

    meal.is_active = not meal.is_active

    meal.save()

    return Response({"success": True})




@api_view(['GET' , 'POST'])
@permission_classes([AllowAny])
def bookings(request):
    if request.method == 'GET':

        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=401)
        
        if request.user.is_authenticated and request.user.is_staff:
            bookings = Booking.objects.all()
        else:
            bookings = Booking.objects.filter(user=request.user)
        serializer = BookingSerializer(bookings, many = True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = BookingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            meal_id = request.data.get("meal_option")
            meal_price = 0

            if meal_id:
                meal = MealOption.objects.get(id=meal_id)
                meal_price = meal.price
            check_in = serializer.validated_data["check_in"]
            check_out = serializer.validated_data["check_out"]
            room = serializer.validated_data["room"]
            nights = (check_out - check_in).days
            room_price = room.room_type.price
            meal_price = Decimal("0.00")
            meal_id = request.data.get("meal_option")

            if meal_id:
                meal = MealOption.objects.get(id=meal_id)
                meal_price = meal.price
            total_price = (room_price * nights) + meal_price
            booking = serializer.save(
                user=request.user if request.user.is_authenticated else None,
                meal_price=meal_price,
                total_price=total_price,
            )
            if request.data.get("payment_method") == "online":
                booking.payment_status = "paid"
            else:
                booking.payment_status = "unpaid"
            booking.save()
            CustomerRecord.objects.create(
                name=booking.guest_name,
                email=booking.guest_email,
                phone=booking.guest_phone,
                country=booking.guest_country
            )
            create_notification("New Booking",f"New booking from {booking.user.email}","booking")
            create_log(request.user if request.user.is_authenticated else None, "Created Booking", booking.booking_code)
            setting = AutoCloseSetting.objects.first()
            if setting and setting.auto_close_booked_room:
                if booking.room:
                    booking.room.status = "OFF"
                    booking.room.save()
            return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def update_booking_payment(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        booking.payment_status = request.data.get(
            "payment_status",
            booking.payment_status
        )
        booking.save()
        return Response({"message": "updated successfully"})
    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"},
            status=404
        )




@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def mark_all_bookings_read(request):

    Booking.objects.filter(is_read=False).update(is_read=True)

    return Response({
        "message": "All bookings marked as read"
    })







@api_view(["PUT"])
@permission_classes([IsAdminUser])
def toggle_booking_read(request, booking_id):

    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response(status=404)

    booking.is_read = not booking.is_read
    booking.save()

    return Response({
        "is_read": booking.is_read
    })





@api_view(['GET'])
@permission_classes([IsAdminUser])
def room_bookings(request, room_id):
    today = date.today()

    bookings = Booking.objects.filter(
        room__id=room_id,
        check_out__gte=today
    ).order_by('check_in')

    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([AllowAny])
def available_rooms(request):
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    room_type = request.GET.get('room_type')

    rooms = Room.objects.filter(status='ON')

    if room_type:
        rooms = rooms.filter(room_type__name__iexact=room_type)

    booked_rooms = Booking.objects.filter(
        check_in__lt=check_out,
        check_out__gt=check_in,

    ).values_list('room_id', flat=True)

    
    rooms = rooms.filter(
        available_from__lte=check_in,
        available_to__gte=check_out
    )

    available = rooms.exclude(id__in=booked_rooms)
    serializer = RoomSerializer(available, many=True)

    return Response(serializer.data)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def booking_detail(request, id):
    try:
        booking = Booking.objects.get(id=id)
    except Booking.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    
    if booking.user != request.user and not request.user.is_staff:
        return Response({"error": "Not allowed"}, status=403)


    if request.method == 'PUT':
        serializer = BookingSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            create_log(request.user, "Updated Booking", booking.id)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors)

    if request.method == 'DELETE':
        create_log(request.user, "Deleted Booking", booking.id)
        create_notification("Booking Cancelled",f"Booking #{booking.id} was cancelled","cancel")
        booking.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            "phone": "",
            "country": ""
        }
    )

    data = {
        "first_name": request.user.first_name or request.user.username,
        "email": request.user.email,
        "phone": profile.phone,
        "country": profile.country,
        "is_staff": request.user.is_staff,
    }

    # create_log(request.user, "Viewed Profile", request.user.id)

    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def hotel_detail(request, id):
    try:
        hotel = Hotel.objects.get(id=id)
    except Hotel.DoesNotExist:
        return Response({"error": "Hotel not found"})

    serializer = HotelSerializer(hotel)

    


@api_view(['GET'])
@permission_classes([AllowAny])
def rooms_by_hotel(request, hotel_id):
    rooms = Room.objects.filter(hotel_id=hotel_id)
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)




@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    email = request.data.get("email")

    if User.objects.filter(email=email).exists():
        return Response(
            {"email": ["This email already exists"]},
            status=400
        )

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        profile = Profile.objects.create(
            user=user,
            phone=request.data.get('phone'),
            country=request.data.get('country'))
        create_log(user, "Created Profile", user.email)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET', 'PUT'])
@permission_classes([IsAdminUser])
def booking_settings(request):

    settings = BookingSettings.objects.first()

    if request.method == 'GET':
        serializer = BookingSettingsSerializer(settings)
        return Response(serializer.data)

    serializer = BookingSettingsSerializer(
        settings,
        data=request.data
    )

    if serializer.is_valid():
        serializer.save()
        create_log(request.user, "Updated Booking Settings", settings.id)
        return Response(serializer.data)

    return Response(serializer.errors, status=400)



@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    today = date.today()

    booked_room_ids = Booking.objects.filter(
        check_out__gt=today
        ).values_list("room_id", flat=True)
    
    booked_rooms = booked_room_ids.distinct().count()

    total_room_types = RoomType.objects.count()
    total_rooms = Room.objects.count()

    available_rooms = Room.objects.filter(
        # is_available=True,
        status='ON'
    ).exclude(
    id__in=booked_room_ids
    ).count()

    unavailable_rooms = Room.objects.filter(

        status='OFF'
    ).count()

    current_bookings = Booking.objects.filter(
        check_out__gt=today
    ).count()

    current_guests = Booking.objects.filter(
        check_in__lte=today,
        check_out__gt=today
    ).count()

    departures_today = Booking.objects.filter(
        check_out=today
    ).count()

    arrivals = Booking.objects.filter(
        check_in__gt=today
    ).count()

    room_type_bookings = []

    for room_type in RoomType.objects.all():
        count = Booking.objects.filter(
            room__room_type=room_type,
            check_out__gte=today
        ).count()

        room_type_bookings.append({
            "room_type": room_type.name,
            "count": count
        })

    return Response({
        "total_room_types": total_room_types,
        "total_rooms": total_rooms,
        "available_rooms": available_rooms,
        "unavailable_rooms": unavailable_rooms,
        "current_bookings": current_bookings,
        "current_guests": current_guests,
        "departures_today": departures_today,
        "arrivals": arrivals,
        "room_type_bookings": room_type_bookings,
        "booked_rooms": booked_rooms,
    })



@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_card_settings(request):

    settings = DashboardCardSetting.objects.all()

    serializer = DashboardCardSettingSerializer(
        settings,
        many=True
    )

    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def dashboard_card_setting_detail(request, pk):

    try:
        setting = DashboardCardSetting.objects.get(id=pk)

    except DashboardCardSetting.DoesNotExist:
        return Response(
            {"error": "Setting not found"},
            status=404
        )

    serializer = DashboardCardSettingSerializer(
        setting,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)








@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_bookings(request):

    bookings = Booking.objects.select_related(
        'user',
        'room'
    ).order_by('-created_at')

    serializer = BookingSerializer(bookings, many=True)

    return Response(serializer.data)







# لإلغاء الحجز
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_booking(request, pk):

    try:
        booking = Booking.objects.get(id=pk)
    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"},
            status=404
        )
    create_log(
        request.user,
        "Deleted Booking",
        booking.id
    )
    booking.delete()
    return Response(
        {"message": "Booking deleted"}
    )


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def room_types(request):
    if request.method == 'GET':
        types = RoomType.objects.all()
        serializer = RoomTypeSerializer(types, many=True)
        return Response(serializer.data)

    serializer = RoomTypeSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        create_log(request.user, "Created Room Type", serializer.data['id'])
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)

# لإدارة أنواع الغرف (CRUD) - حذف نوع غرفة
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def room_type_detail(request, pk):
    try:
        room_type = RoomType.objects.get(id=pk)
    except RoomType.DoesNotExist:
        return Response(
            {"error": "Room type not found"},
            status=404
        )

    if request.method == 'GET':
        serializer = RoomTypeSerializer(room_type)
        return Response(serializer.data)

    if request.method in ['PUT', 'PATCH']:
        serializer = RoomTypeSerializer(
            room_type,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            create_log(request.user, "Updated Room Type", room_type.id)
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':

        if room_type.rooms.exists():
            return Response(
                {"error": "Cannot delete this room type because it has rooms."},
                status=400
            )
        create_log(request.user, "Deleted Room Type", room_type.name)
        room_type.delete()
        
        return Response(status=204)






@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_bookings(request):
    bookings = Booking.objects.all().order_by('-id')
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)




@api_view(['GET'])
@permission_classes([IsAdminUser])
def current_bookings(request):
    bookings = Booking.objects.filter(
        check_out__gte=now().date()
    ).order_by('check_in')

    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([AllowAny])
def room_detail(request, pk):
    try:
        room = Room.objects.get(id=pk)
    except Room.DoesNotExist:
        return Response(
            {"error": "Room not found"},
            status=404
        )

    serializer = RoomSerializer(room)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def rooms_by_type(request, pk):
    rooms = Room.objects.filter(room_type_id=pk)
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)



#bulk availability add
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_room_availability(request):
    room_type_id = request.data.get("room_type")
    count = int(request.data.get("count", 0))
    available_from = request.data.get("available_from")
    available_to = request.data.get("available_to")
    status_value = request.data.get("status", "ON")

    rooms = Room.objects.filter(
        room_type_id=room_type_id
    ).order_by("room_number")[:count]

    for room in rooms:
        room.is_available = True
        room.available_from = available_from
        room.available_to = available_to
        room.status = status_value
        room.save()
        create_log(request.user, "Updated Room Availability", room.room_type)

    return Response({
        "message": f"{len(rooms)} rooms updated successfully"
    })


@api_view(["PUT"])
@permission_classes([IsAdminUser])
def rooms_bulk_off(request):
    Room.objects.all().update(
        status="OFF",
        is_available=False
    )

    return Response({
        "message": "All rooms are now not available"
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def room_availability(request, room_id):
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return Response({"error": "Room not found"}, status=404)

    return Response({
        "available_from": room.available_from,
        "available_to": room.available_to,
    })



#restaurant
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def restaurants(request):
    if request.method == 'GET':
        data = Restaurant.objects.filter(is_active=True)
        serializer = RestaurantSerializer(data, many=True)
        return Response(serializer.data)

    serializer = RestaurantSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        create_log(request.user, "Created Restaurant", serializer.data['id'])
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_restaurants(request):
    restaurants = Restaurant.objects.all().order_by("-id")
    serializer = RestaurantSerializer(restaurants, many=True)
    return Response(serializer.data)




@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def restaurant_detail(request, pk):
    try:
        restaurant = Restaurant.objects.get(id=pk)
    except Restaurant.DoesNotExist:
        return Response({"error": "Restaurant not found"}, status=404)

    if request.method == 'GET':
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = RestaurantSerializer(
            restaurant,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            create_log(request.user, "Updated Restaurant", f"{restaurant.name}")
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        create_log(request.user, "Deleted Restaurant", restaurant.name)
        restaurant.delete()
        
        return Response(status=204)





# Nearby Places
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def nearby_places(request):

    if request.method == 'GET':
        places = NearbyPlace.objects.filter(is_active=True).order_by("order" , "id")
        serializer = NearbyPlaceSerializer(places, many=True , context={"request": request})
        return Response(serializer.data)

    serializer = NearbyPlaceSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        create_log(request.user, "Created Nearby Place", serializer.data['id'])
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_nearby_places(request):
    nearby_places = NearbyPlace.objects.all().order_by("-id")
    serializer = NearbyPlaceSerializer(nearby_places, many=True)
    return Response(serializer.data)







@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def nearby_place_detail(request, pk):
    try:
        place = NearbyPlace.objects.get(id=pk)
    except NearbyPlace.DoesNotExist:
        return Response({"error": "Place not found"}, status=404)

    if request.method == 'GET':
        serializer = NearbyPlaceSerializer(place)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = NearbyPlaceSerializer(
            place,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            create_log(request.user, "Updated Nearby Place", place.id)
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        create_log(request.user, "Deleted Nearby Place", place.name_en)
        place.delete()
        
        return Response(status=204)
    


# Services
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def services(request):
    if request.method == 'GET':
        data = Service.objects.filter(is_active=True)
        serializer = ServiceSerializer(data, many=True)
        return Response(serializer.data)

    serializer = ServiceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        create_log(request.user, "Created Service", serializer.data['id'])
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_services(request):
    services = Service.objects.all().order_by("-id")
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data)




@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def service_detail(request, pk):
    try:
        service = Service.objects.get(id=pk)
    except Service.DoesNotExist:
        return Response({"error": "Service not found"}, status=404)

    if request.method == 'GET':
        serializer = ServiceSerializer(service)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = ServiceSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            create_log(request.user, "Updated Service", service.id)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        create_log(request.user, "Deleted Service", service.title)
        service.delete()
        return Response(status=204)
    
# End Services



# Gallery List/Create
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def galleries(request):

    if request.method == 'GET':
        data = Gallery.objects.filter(is_active=True)
        serializer = GallerySerializer(data, many=True)
        return Response(serializer.data)
    serializer = GallerySerializer(data=request.data)
    if serializer.is_valid():
        gallery = serializer.save()
        create_log(request.user if request.user.is_authenticated else None, "Created Gallery", f" Gallery {gallery.title_en}")
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

# Gallery Detail
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def gallery_detail(request, pk):

    try:
        gallery = Gallery.objects.get(id=pk)
    except Gallery.DoesNotExist:
        return Response(
            {"error": "Gallery not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # GET
    if request.method == 'GET':
        serializer = GallerySerializer(gallery)
        return Response(serializer.data)

    # PUT
    if request.method == 'PUT':
        serializer = GallerySerializer(
            gallery,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            create_log(request.user if request.user.is_authenticated else None, "Updated Gallery", f" Gallery {gallery.title_en}")
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    # DELETE
    create_log(request.user if request.user.is_authenticated else None, "Deleted Gallery", f" Gallery {gallery.title_en}")
    gallery.delete()
    return Response(status=204)


# Gallery Images
@api_view(['POST'])
@permission_classes([AllowAny])
def gallery_images(request):

    serializer = GalleryImageSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        create_log(request.user, "Created Gallery Image", serializer.data['id'])
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(['PUT', 'DELETE'])
@permission_classes([AllowAny])
def gallery_image_detail(request, pk):

    try:
        image = GalleryImage.objects.get(id=pk)
    except GalleryImage.DoesNotExist:
        return Response(
            {"error": "Image not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # PUT
    if request.method == 'PUT':

        serializer = GalleryImageSerializer(
            image,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            create_log(request.user if request.user.is_authenticated else None, "Updated Gallery Image", f"Image {image.id} in Gallery {image.gallery.name}")
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    # DELETE
    create_log(request.user if request.user.is_authenticated else None, "Deleted Gallery Image",
                f"Image {image.id} from Gallery {image.gallery.title_en}")

    image.delete()
    return Response(status=204)




# Review List/Create
# Reviews

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def reviews(request):

    if request.method == 'GET':

        if request.user.is_authenticated and request.user.is_staff:
            data = Review.objects.all().order_by('-created_at')

        else:
            data = Review.objects.filter(
                is_active=True
            ).order_by('-created_at')

        serializer = ReviewSerializer(data, many=True)
        return Response(serializer.data)

    serializer = ReviewSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def review_detail(request, pk):

    try:
        review = Review.objects.get(id=pk)

    except Review.DoesNotExist:
        return Response(
            {"error": "Review not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # GET
    if request.method == 'GET':
        serializer = ReviewSerializer(review)
        create_log(request.user if request.user.is_authenticated else None, "Viewed Review", f"{review.name} - {review.rating}/5")
        return Response(serializer.data)

    # PUT
    if request.method == 'PUT':

        serializer = ReviewSerializer(
            review,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            create_log(request.user, "Updated Review", f"{review.name} - {review.rating}/5")
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    # DELETE
    create_log(request.user, "Deleted Review", review.id)
    review.delete()
    return Response(status=204)



@api_view(['POST'])
@permission_classes([AllowAny])
def submit_review(request):
    booking_code = request.data.get("booking_code")
    if not booking_code:
        return Response(
            {"error": "Booking code is required"},
            status=400
        )
    try:
        booking = Booking.objects.get(booking_code=booking_code)
    except Booking.DoesNotExist:
        return Response(
            {"error": "Invalid booking code"},
            status=404
        )
    if booking.review_used:
        return Response(
            {"error": "This booking code has already been used for a review"},
            status=400
        )
    

    if Review.objects.filter(booking=booking).exists():
        return Response(
            {"error": "This booking code has already been used for a review"},
            status=400
        )
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        review = serializer.save(
            booking=booking,
            is_active=False
        )
        create_notification("New Review",f"{review.name} added a review","review")
        create_log(request.user if request.user.is_authenticated else None,"Created Review",f"{review.name} - {review.rating}/5")
        booking.review_used = True
        booking.save()
        return Response(
            {"message": "Review submitted and waiting for approval"},
            status=201
        )

    return Response(serializer.errors, status=400)





#users
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def staff_users(request):

    if request.method == 'GET':

        users = User.objects.filter(is_staff=True)

        serializer = StaffUserSerializer(users, many=True)

        return Response(serializer.data)

    serializer = StaffUserSerializer(data=request.data)

    if serializer.is_valid():

        user = serializer.save()
        create_log(request.user, "Created Staff User", user.email)

        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)






@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def staff_user_detail(request, pk):

    try:
        user = User.objects.get(id=pk, is_staff=True)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=404
        )
    
    if user.is_superuser and not request.user.is_superuser:
        return Response(
            {"error": "Only superuser can modify another superuser"},
            status=403
        )
    if request.method == 'GET':
        serializer = StaffUserSerializer(user)
        return Response(serializer.data)
    
    if request.method == 'PUT':

        password = request.data.get('password')
        groups = request.data.get('groups')

        data = request.data.copy()

        if not password:
            data.pop('password', None)

        serializer = StaffUserSerializer(
            user,
            data=data,
            partial=True
        )

        if serializer.is_valid():

            user = serializer.save()

            if password:
                user.set_password(password)
                user.save()
                create_log(request.user, "Updated Staff User", user.email)

            if groups is not None:
                user.groups.set(groups)

            return Response(serializer.data)

        return Response(serializer.errors, status=400)
    create_log(request.user, "Deleted Staff User", user.email)
    user.delete()
    return Response(status=204)




# Groups and Permissions


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def groups(request):

    if request.method == 'GET':
        result = []

        for group in Group.objects.all():
            result.append({
                "id": group.id,
                "name": group.name,
                "permissions": [
                    p.codename for p in group.permissions.all()
                ]
            })

        return Response(result)
    name = request.data.get("name")
    permissions = request.data.get("permissions", [])
    group = Group.objects.create(name=name)
    perms = Permission.objects.filter(
        codename__in=permissions
    )

    group.permissions.set(perms)

    return Response({
        "id": group.id,
        "name": group.name,
        "permissions": [
            p.codename for p in group.permissions.all()
        ]
    }, status=201)



@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def group_detail(request, pk):

    try:
        group = Group.objects.get(id=pk)

    except Group.DoesNotExist:
        return Response(
            {"error": "Group not found"},
            status=404
        )

    if request.method == 'GET':

        data = {
            "id": group.id,
            "name": group.name,
            "permissions": [
                p.codename for p in group.permissions.all()
            ]
        }

        return Response(data)

    if request.method == 'PUT':

        name = request.data.get("name")
        permissions = request.data.get("permissions", [])

        if name:
            group.name = name
            group.save()

        perms = Permission.objects.filter(
            codename__in=permissions
        )

        group.permissions.set(perms)

        return Response({
            "id": group.id,
            "name": group.name,
            "permissions": [
                p.codename for p in group.permissions.all()
            ]
        })

    group.delete()

    return Response(status=204)




#list all permissions
@api_view(['GET'])
@permission_classes([IsAdminUser])
def permissions_list(request):
    permissions = Permission.objects.all()

    data = [
        {
            "id": permission.id,
            "name": permission.name,
            "codename": permission.codename,
        }
        for permission in permissions
    ]

    return Response(data)













#Logs 
@api_view(['GET'])
@permission_classes([IsAdminUser])
def logs(request):

    data = ActivityLog.objects.all().order_by(
        '-created_at'
    )

    serializer = ActivityLogSerializer(
        data,
        many=True
    )

    return Response(serializer.data)




#Contact Us
@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def contact_settings(request):
    setting = ContactSetting.objects.first()

    if not setting:
        setting = ContactSetting.objects.create(
            phone="",
            email="",
            address=""
        )

    if request.method == 'GET':
        serializer = ContactSettingSerializer(setting)
        return Response(serializer.data)

    serializer = ContactSettingSerializer(
        setting,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)





@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def contact_messages(request):

    if request.method == 'GET':
        messages = ContactMessage.objects.all().order_by('-created_at')
        serializer = ContactMessageSerializer(messages, many=True)
        return Response(serializer.data)

    serializer = ContactMessageSerializer(data=request.data)

    if serializer.is_valid():
        message = serializer.save()
        create_notification("New Contact Message",f"Message from {message.name}","contact")
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)









@api_view(['PUT'])
@permission_classes([IsAdminUser])
def contact_message_detail(request, pk):
    try:
        message = ContactMessage.objects.get(id=pk)
    except ContactMessage.DoesNotExist:
        return Response({"error": "Message not found"}, status=404)

    message.is_read = request.data.get("is_read", message.is_read)
    message.save()

    return Response({"message": "Updated successfully"})




@api_view(["GET", "PUT"])
@permission_classes([AllowAny])
def system_settings(request):
    setting, created = SystemSetting.objects.get_or_create(id=1)

    if request.method == "GET":
        serializer = SystemSettingSerializer(setting)
        return Response(serializer.data)

    serializer = SystemSettingSerializer(
        setting,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)




#Customer Profiles


@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_profiles(request):
    profiles = Profile.objects.filter(
        user__is_staff=False,
        user__is_superuser=False
    ).select_related("user").order_by("-user__date_joined")

    serializer = AdminProfileListSerializer(profiles, many=True)
    return Response(serializer.data)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAdminUser])
def admin_profile_detail(request, pk):
    try:
        profile = Profile.objects.select_related("user").get(id=pk)

        if profile.user.is_staff or profile.user.is_superuser:
            return Response({"error": "This is not a customer profile"}, status=403)

    except Profile.DoesNotExist:
        return Response({"error": "Profile not found"}, status=404)

    if request.method == "GET":
        serializer = AdminProfileDetailSerializer(profile)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = AdminProfileDetailSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    if request.method == "DELETE":
        user = profile.user
        profile.delete()
        user.delete()
        return Response({"message": "Profile deleted successfully"}, status=204)
    






@api_view(["GET"])
@permission_classes([IsAdminUser])
def customer_records(request):
    records = CustomerRecord.objects.all().order_by("-created_at")
    serializer = CustomerRecordSerializer(records, many=True)
    return Response(serializer.data)









@api_view(["POST"])
@permission_classes([AllowAny])
def fake_payment(request, booking_id):

    try:
        booking = Booking.objects.get(id=booking_id)

    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"},
            status=404
        )

    card_number = request.data.get("card_number", "").replace(" ", "")

    if card_number == "4242424242424242":

        booking.payment_status = "paid"
        booking.payment_method = "online"
        booking.save()

        return Response({
            "message": "Payment successful",
            "payment_status": booking.payment_status
        })

    booking.payment_status = "failed"
    booking.payment_method = "online"
    booking.save()

    return Response(
        {
            "error": "Payment failed",
            "payment_status": booking.payment_status
        },
        status=400
    )





@api_view(["GET"])
@permission_classes([IsAdminUser])
def booking_detail(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    serializer = BookingSerializer(booking)
    return Response(serializer.data)



@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def update_booking_notes(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    booking.notes = request.data.get("notes", "")
    booking.save()
    return Response({"message": "Notes updated", "notes": booking.notes})





@api_view(["GET"])
@permission_classes([AllowAny])
def active_hero_slides(request):
    slides = HeroSlide.objects.filter(is_active=True).order_by("order", "id")
    serializer = HeroSlideSerializer(slides, many=True, context={"request": request})
    return Response(serializer.data)



@api_view(["GET", "POST"])
@parser_classes([MultiPartParser, FormParser])
def admin_hero_slides(request):
    if request.method == "GET":
        slides = HeroSlide.objects.all().order_by("order", "id")
        serializer = HeroSlideSerializer(slides, many=True, context={"request": request})
        return Response(serializer.data)

    print("FILES:", request.FILES)
    print("DATA:", request.data)

    serializer = HeroSlideSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    print(serializer.errors)
    return Response(serializer.errors, status=400)


@api_view(["PUT", "PATCH", "DELETE"])
@parser_classes([MultiPartParser, FormParser])
def admin_hero_slide_detail(request, pk):
    slide = get_object_or_404(HeroSlide, pk=pk)

    if request.method == "DELETE":
        slide.delete()
        return Response(status=204)

    serializer = HeroSlideSerializer(
        slide,
        data=request.data,
        partial=True,
        context={"request": request}
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)





@api_view(["GET"])
def amenities(request):
    items = Amenity.objects.all()
    serializer = AmenitySerializer(items, many=True)
    return Response(serializer.data)



@api_view(["GET"])
def dashboard_occupancy(request):
    start_date = request.GET.get("start_date")
    days = int(request.GET.get("days", 8))
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    total_rooms = Room.objects.count()
    result = []

    for i in range(days):
        day = start + timedelta(days=i)

        occupied = Booking.objects.filter(
            check_in__lte=day,
            check_out__gt=day
        ).values("room").distinct().count()

        result.append({
            "date": day,
            "occupied": occupied,
            "available": total_rooms - occupied,
        })

    return Response({
        "total_rooms": total_rooms,
        "days": result,
    })





@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def user_table_setting(request, table_name):
    setting, created = UserTableSetting.objects.get_or_create(
        user=request.user,
        table_name=table_name,
        defaults={"visible_columns": {}}
    )

    if request.method == "GET":
        serializer = UserTableSettingSerializer(setting)
        return Response(serializer.data)

    if request.method == "PATCH":
        visible_columns = request.data.get("visible_columns", {})
        setting.visible_columns = visible_columns
        setting.save()

        serializer = UserTableSettingSerializer(setting)
        return Response(serializer.data)
    




# اعداد التغيير التلقائي لحالة الغرفة
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def auto_close_setting(request):
    setting, created = AutoCloseSetting.objects.get_or_create(id=1)

    if request.method == "GET":
        return Response({
            "auto_close_booked_room": setting.auto_close_booked_room
        })

    setting.auto_close_booked_room = request.data.get(
        "auto_close_booked_room",
        setting.auto_close_booked_room
    )
    setting.save()

    return Response({
        "auto_close_booked_room": setting.auto_close_booked_room
    })




@api_view(["GET"])
@permission_classes([AllowAny])
def site_status(request):
    setting, created = SiteSetting.objects.get_or_create(id=1)

    return Response({
        "maintenance_mode": setting.maintenance_mode
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_maintenance(request):
    setting, created = SiteSetting.objects.get_or_create(id=1)

    setting.maintenance_mode = not setting.maintenance_mode
    setting.save()

    return Response({
        "maintenance_mode": setting.maintenance_mode
    })










@api_view(["GET"])
@permission_classes([AllowAny])
def facilities(request):
    items = Facility.objects.filter(is_active=True).order_by("order", "id")
    serializer = FacilitySerializer(items, many=True)
    return Response(serializer.data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def admin_facilities(request):
    if request.method == "GET":
        items = Facility.objects.all().order_by("order", "id")
        serializer = FacilitySerializer(items, many=True)
        return Response(serializer.data)

    serializer = FacilitySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def admin_facility_detail(request, pk):
    facility = get_object_or_404(Facility, pk=pk)

    if request.method == "GET":
        serializer = FacilitySerializer(facility)
        return Response(serializer.data)

    if request.method == "DELETE":
        facility.delete()
        return Response({"message": "Deleted successfully"})

    serializer = FacilitySerializer(
        facility,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)









@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def policy_settings(request):
    setting, created = PolicySetting.objects.get_or_create(id=1)

    if request.method == "GET":
        serializer = PolicySettingSerializer(setting)
        return Response(serializer.data)

    serializer = PolicySettingSerializer(setting, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([AllowAny])
def public_policy_settings(request):
    setting, created = PolicySetting.objects.get_or_create(id=1)
    serializer = PolicySettingSerializer(setting)
    return Response(serializer.data)




@api_view(["GET"])
@permission_classes([AllowAny])
def public_social_settings(request):
    setting, created = SocialMediaSetting.objects.get_or_create(id=1)
    serializer = SocialMediaSettingSerializer(setting)
    return Response(serializer.data)


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def social_settings(request):
    setting, created = SocialMediaSetting.objects.get_or_create(id=1)

    if request.method == "GET":
        serializer = SocialMediaSettingSerializer(setting)
        return Response(serializer.data)

    serializer = SocialMediaSettingSerializer(
        setting,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)