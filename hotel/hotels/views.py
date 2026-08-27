from urllib import request

from rest_framework.decorators import api_view, parser_classes , permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , IsAdminUser , AllowAny
from rest_framework import status

from .utils import send_booking_confirmation_email , send_reception_booking_notification
from .serializers import ActivityLogSerializer, GalleryImageSerializer, RegisterSerializer, RestaurantSerializer, ReviewSerializer, RoomTypeSerializer , UserSerializer
from .models import ActivityLog, GalleryImage, Hotel, NearbyPlace, Profile, Restaurant, Review ,Payment, Room , Booking , BookingSettings, RoomType, Service , Gallery
from .serializers import HotelSerializer , RoomSerializer , BookingSerializer , BookingSettingsSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from django.db.models import ProtectedError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import date, timezone
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
from django.utils import timezone
from .zaincash import create_payment , inquiry_payment  ,verify_zaincash_callback_token
from decimal import Decimal
from django.db import transaction
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from rest_framework.throttling import UserRateThrottle
from rest_framework.decorators import throttle_classes
from rest_framework.throttling import AnonRateThrottle
















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



@api_view(["GET"])
@permission_classes([AllowAny])
def currencies(request):
    data = Currency.objects.all()
    serializer = CurrencySerializer(data, many=True)
    return Response(serializer.data)



@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def admin_currencies(request):
    # get
    if request.method == "GET":
        data = Currency.objects.all()
        serializer = CurrencySerializer(data, many=True)
        return Response(serializer.data)
    
    # post
    serializer = CurrencySerializer(data=request.data)
    if serializer.is_valid():
        currency = serializer.save()
        create_log(request.user, "Currency Added", currency.name)
        return Response(CurrencySerializer(currency).data, status=201)
    return Response(serializer.errors, status=400)



@api_view(["GET", "PUT" , "PATCH" , "DELETE"])
@permission_classes([IsAdminUser])
def currency_detail(request, pk):
    try:
        currency = Currency.objects.get(id=pk)
    except Currency.DoesNotExist:
        return Response({"error": "Currency not found"}, status=404)
    
    if request.method == "GET":
        serializer = CurrencySerializer(currency)
        return Response(serializer.data)


    if request.method in ["PUT" , "PATCH"]:
        if request.data.get("is_active") == True:
            Currency.objects.all().update(is_active=False)
        serializer = CurrencySerializer(currency, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            create_log(request.user, "Currency Changed", currency.name)

            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    create_log(request.user, "Currency Deleted" , currency.name)
    
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
            meal_price = Decimal("0.00")

            if meal_id:
                meal = MealOption.objects.get(id=meal_id)
                meal_price = meal.price
            check_in = serializer.validated_data["check_in"]
            check_out = serializer.validated_data["check_out"]
            room = serializer.validated_data["room"]
            nights = (check_out - check_in).days
            room_price = room.room_type.price
            room_total = room_price * nights
            meal_total = meal_price * nights
            total_price = room_total + meal_total
            booking = serializer.save(
                user=request.user if request.user.is_authenticated else None,
                nights=nights,
                meal_price=meal_price,
                total_price=total_price,
                booking_status="pending",
                payment_status="unpaid",
                expires_at=timezone.now() + timedelta(hours=24)
            )


            payment = None

            if booking.payment_method == "online":
                payment = Payment.objects.create(
                    booking=booking,
                    gateway="zaincash",
                    external_reference=booking.booking_code,
                    amount=total_price,
                    currency="IQD",
                    status="pending"
                )


                payment_url = None


                try:
                    zain_response = create_payment(
                        booking_id=booking.id,
                        amount=total_price,
                        success_url=(f"http://localhost:3000/payment-success/{booking.id}"),
                        failure_url=(f"http://localhost:3000/payment-failed/{booking.id}"),
                        
                    )

                    transaction_details = zain_response.get("transactionDetails", {})

                    payment.transaction_id = transaction_details.get("transactionId")
                    payment.external_reference = transaction_details.get(
                        "externalReferenceId",
                        booking.booking_code
                    )
                    payment.save()

                    payment_url = transaction_details.get("redirectUrl")

                except Exception as e:
                    payment.status = "failed"
                    payment.save(update_fields=["status"])

                    return Response(
                        {
                            "error": "Unable to initialize ZainCash payment",
                            "details": str(e),
                        },
                        status=502
                    )

            
            CustomerRecord.objects.create(
                name=booking.guest_name,
                email=booking.guest_email,
                phone=booking.guest_phone,
                country=booking.guest_country
            )
            
            
            create_notification("New Booking",f"New booking from {booking.guest_name}","booking")

            setting = AutoCloseSetting.objects.first()
            if booking.booking_status == "confirmed":
                if setting and setting.auto_close_booked_room:
                    if booking.room:
                        booking.room.status = "OFF"
                        booking.room.save()
            return Response({
                "booking": BookingSerializer(booking).data,
                "payment": {
                    "id": payment.id,
                    "status": payment.status,
                    "amount": str(payment.amount),
                    "currency": payment.currency,
                    "payment_url": payment_url
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def update_booking_payment(request, booking_id):

    try:
        booking = Booking.objects.get(id=booking_id)

    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"},
            status=404
        )

    payment_status = request.data.get("payment_status")

    allowed_statuses = [
        "unpaid",
        "paid",
        "failed",
        "refunded",
    ]

    if payment_status not in allowed_statuses:
        return Response(
            {
                "error": "Invalid payment status",
                "allowed_statuses": allowed_statuses
            },
            status=400
        )

    booking.payment_status = payment_status

    if payment_status == "paid":
        booking.booking_status = "confirmed"

    elif payment_status in ["failed", "unpaid"]:
        if booking.booking_status != "cancelled":
            booking.booking_status = "pending"

    elif payment_status == "refunded":
        booking.booking_status = "cancelled"

    booking.save()

    return Response({
        "message": "Booking payment updated successfully",
        "booking_status": booking.booking_status,
        "payment_status": booking.payment_status,
    })




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


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            "phone": "",
            "country": "",
            "address": "",
        }
    )

    if request.method == "GET":

        return Response({
            "id": request.user.id,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "phone": profile.phone,
            "country": profile.country,
            "address": profile.address,
            "is_staff": request.user.is_staff,
        })

    # UPDATE PROFILE

    first_name = request.data.get(
        "first_name",
        request.user.first_name
    )

    last_name = request.data.get(
        "last_name",
        request.user.last_name
    )

    email = request.data.get(
        "email",
        request.user.email
    )

    phone = request.data.get(
        "phone",
        profile.phone
    )

    country = request.data.get(
        "country",
        profile.country
    )

    address = request.data.get(
        "address",
        profile.address
    )

    # Check email uniqueness
    if (
        email != request.user.email
        and User.objects.filter(email=email).exclude(
            id=request.user.id
        ).exists()
    ):
        return Response(
            {
                "email": "This email is already in use."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    request.user.first_name = first_name
    request.user.last_name = last_name
    request.user.email = email

    # Your system uses email as username
    request.user.username = email

    request.user.save()

    profile.phone = phone
    profile.country = country
    profile.address = address

    profile.save()

    return Response({
        "message": "Profile updated successfully.",
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "email": request.user.email,
        "phone": profile.phone,
        "country": profile.country,
        "address": profile.address,
    })




@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_account(request):

    user = request.user

    # Delete user account
    user.delete()

    return Response(
        {
            "message": "Account deleted successfully."
        },
        status=status.HTTP_200_OK
    )




@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):

    current_password = request.data.get("current_password")
    new_password = request.data.get("new_password")
    confirm_password = request.data.get("confirm_password")

    if not current_password:
        return Response(
            {"error": "Current password is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not new_password:
        return Response(
            {"error": "New password is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if new_password != confirm_password:
        return Response(
            {"error": "Passwords do not match."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not request.user.check_password(current_password):
        return Response(
            {"error": "Current password is incorrect."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(new_password) < 8:
        return Response(
            {"error": "Password must contain at least 8 characters."},
            status=status.HTTP_400_BAD_REQUEST
        )

    request.user.set_password(new_password)
    request.user.save()

    return Response({
        "message": "Password updated successfully."
    })














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



#لإلغاء الحجز
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, pk):
    try:
        booking = Booking.objects.get(id=pk)
    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"},
            status=404
        )

    if booking.user != request.user and not request.user.is_staff:
        return Response(
            {"error": "Not allowed"},
            status=403
        )

    if booking.booking_status == "cancelled":
        return Response(
            {"error": "Booking is already cancelled"},
            status=400
        )

    booking.booking_status = "cancelled"
    booking.save(update_fields=["booking_status"])

    create_log(
        request.user,
        "Cancelled Booking",
        booking.id
    )

    create_notification(
        "Booking Cancelled",
        f"Booking #{booking.id} was cancelled",
        "cancel"
    )

    return Response({
        "message": "Booking cancelled successfully",
        "booking_status": booking.booking_status,
        "booking_id": booking.id
    })


# لحذف الحجز
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
    
    if not request.user.is_staff and booking.user != request.user:
        return Response({"error": "Not Allowed"} , status=403)

    create_log(
        request.user,
        "Deleted Booking",
        booking.id
    )
    booking.delete()
    return Response(
        {"message": "Booking deleted"}
    )




@api_view(["GET"])
@permission_classes([AllowAny])
def room_types(request):
    types = RoomType.objects.all()
    serializer = RoomTypeSerializer(types, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def admin_room_types(request):
    serializer = RoomTypeSerializer(data=request.data)

    if serializer.is_valid():
        room_type = serializer.save()
        create_log(request.user, "Created Room Type", room_type.id)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)



# @api_view(['GET', 'POST'])
# @permission_classes([AllowAny])
# def room_types(request):
#     if request.method == 'GET':
#         types = RoomType.objects.all()
#         serializer = RoomTypeSerializer(types, many=True)
#         return Response(serializer.data)

#     serializer = RoomTypeSerializer(data=request.data)

#     if serializer.is_valid():
#         serializer.save()
#         create_log(request.user, "Created Room Type", serializer.data['id'])
#         return Response(serializer.data, status=201)

#     return Response(serializer.errors, status=400)

# لإدارة أنواع الغرف (CRUD) - حذف نوع غرفة
# @api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
# @permission_classes([AllowAny])
# def room_type_detail(request, pk):
#     try:
#         room_type = RoomType.objects.get(id=pk)
#     except RoomType.DoesNotExist:
#         return Response(
#             {"error": "Room type not found"},
#             status=404
#         )
#     if request.method == 'GET':
#         serializer = RoomTypeSerializer(room_type)
#         return Response(serializer.data)

#     if not request.user.is_authenticated or not request.user.is_staff:
#         return Response({"detail": "Admin only"}, status=403)

#     if request.method in ['PUT', 'PATCH']:
#         serializer = RoomTypeSerializer(
#             room_type,
#             data=request.data,
#             partial=True
#         )
#         if serializer.is_valid():
#             serializer.save()
#             create_log(request.user, "Updated Room Type", room_type.id)
#             return Response(serializer.data)
#         return Response(serializer.errors, status=400)
#     if request.method == 'DELETE':
#         if room_type.rooms.exists():
#             return Response(
#                 {"error": "Cannot delete this room type because it has rooms."},
#                 status=400
#             )
#         create_log(request.user, "Deleted Room Type", room_type.name)
#         room_type.delete()
        
#         return Response(status=204)

@api_view(['GET'])
@permission_classes([AllowAny])
def room_type_detail(request, pk):
    try:
        room_type = RoomType.objects.get(id=pk)
    except RoomType.DoesNotExist:
        return Response(
            {"error": "Room type not found"},
            status=404
        )
    serializer = RoomTypeSerializer(room_type)
    return Response(serializer.data)



@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAdminUser])
def admin_room_type_detail(request, pk):
    try:
        room_type = RoomType.objects.get(id=pk)
    except RoomType.DoesNotExist:
        return Response(
            {"error": "Room type not found"},
            status=404
        )

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
@permission_classes([IsAdminUser])
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
# @api_view(['GET', 'POST'])
# @permission_classes([AllowAny])
# def restaurants(request):
#     if request.method == 'GET':
#         data = Restaurant.objects.filter(is_active=True)
#         serializer = RestaurantSerializer(data, many=True)
#         return Response(serializer.data)

#     serializer = RestaurantSerializer(data=request.data)

#     if serializer.is_valid():
#         serializer.save()
#         create_log(request.user, "Created Restaurant", serializer.data['id'])
#         return Response(serializer.data, status=201)

#     return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
def restaurants(request):
    if request.method == 'GET':
        data = Restaurant.objects.filter(is_active=True)
        serializer = RestaurantSerializer(data, many=True)
        return Response(serializer.data)



# @api_view(["GET" , "POST"])
# @permission_classes([IsAdminUser])
# def admin_restaurants(request):
#     restaurants = Restaurant.objects.all().order_by("-id")
#     serializer = RestaurantSerializer(restaurants, many=True)
#     return Response(serializer.data)

@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def admin_restaurants(request):
    if request.method == "GET":
        restaurants = Restaurant.objects.all().order_by("-id")
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)

    serializer = RestaurantSerializer(data=request.data)

    if serializer.is_valid():
        restaurant = serializer.save()
        create_log(request.user, "Created Restaurant", restaurant.id)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


# @api_view(['GET', 'PUT', 'DELETE'])
# @permission_classes([IsAdminUser])
# def restaurant_detail(request, pk):
#     try:
#         restaurant = Restaurant.objects.get(id=pk)
#     except Restaurant.DoesNotExist:
#         return Response({"error": "Restaurant not found"}, status=404)

#     if request.method == 'GET':
#         serializer = RestaurantSerializer(restaurant)
#         return Response(serializer.data)

#     if not request.user.is_authenticated or not request.user.is_staff:
#         return Response({"detail": "Admin only"}, status=403)

#     if request.method == 'PUT':
#         serializer = RestaurantSerializer(
#             restaurant,
#             data=request.data,
#             partial=True
#         )

#         if serializer.is_valid():
#             serializer.save()
#             create_log(request.user, "Updated Restaurant", f"{restaurant.name}")
#             return Response(serializer.data)

#         return Response(serializer.errors, status=400)

#     if request.method == 'DELETE':
#         create_log(request.user, "Deleted Restaurant", restaurant.name)
#         restaurant.delete()
        
#         return Response(status=204)


@api_view(['GET'])
@permission_classes([AllowAny])
def restaurant_detail(request, pk):
    try:
        restaurant = Restaurant.objects.get(id=pk)
    except Restaurant.DoesNotExist:
        return Response({"error": "Restaurant not found"}, status=404)

    if request.method == 'GET':
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def admin_restaurant_detail(request, pk):
    try:
        restaurant = Restaurant.objects.get(id=pk)
    except Restaurant.DoesNotExist:
        return Response({"error": "Restaurant not found"}, status=404)

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
# @api_view(['GET', 'POST'])
# @permission_classes([AllowAny])
# def nearby_places(request):

#     if request.method == 'GET':
#         places = NearbyPlace.objects.filter(is_active=True).order_by("order" , "id")
#         serializer = NearbyPlaceSerializer(places, many=True , context={"request": request})
#         return Response(serializer.data)

#     serializer = NearbyPlaceSerializer(data=request.data)

#     if serializer.is_valid():
#         serializer.save()
#         create_log(request.user, "Created Nearby Place", serializer.data['id'])
#         return Response(serializer.data, status=201)

#     return Response(serializer.errors, status=400)



@api_view(['GET'])
@permission_classes([AllowAny])
def nearby_places(request):
    places = NearbyPlace.objects.filter(is_active=True).order_by("order" , "id")
    serializer = NearbyPlaceSerializer(places, many=True , context={"request": request})
    return Response(serializer.data)



# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def admin_nearby_places(request):
#     nearby_places = NearbyPlace.objects.all().order_by("-id")
#     serializer = NearbyPlaceSerializer(nearby_places, many=True)
#     return Response(serializer.data)

@api_view(["GET", "POST" , 'PUT'])
@permission_classes([IsAdminUser])
def admin_nearby_places(request):
    if request.method == "GET":
        nearby_places = NearbyPlace.objects.all().order_by("-id")
        serializer = NearbyPlaceSerializer(nearby_places, many=True)
        return Response(serializer.data)
    serializer = NearbyPlaceSerializer(data=request.data)
    if serializer.is_valid():
        place = serializer.save()
        create_log(request.user, "Created Nearby Place", place.name_en)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)







# @api_view(['GET', 'PUT', 'DELETE'])
# @permission_classes([AllowAny])
# def nearby_place_detail(request, pk):
#     try:
#         place = NearbyPlace.objects.get(id=pk)
#     except NearbyPlace.DoesNotExist:
#         return Response({"error": "Place not found"}, status=404)

#     if request.method == 'GET':
#         serializer = NearbyPlaceSerializer(place)
#         return Response(serializer.data)
    
#     if not request.user.is_authenticated or not request.user.is_staff:
#         return Response({"detail": "Admin only"}, status=403)

#     if request.method == 'PUT':
#         serializer = NearbyPlaceSerializer(
#             place,
#             data=request.data,
#             partial=True
#         )

#         if serializer.is_valid():
#             serializer.save()
#             create_log(request.user, "Updated Nearby Place", place.id)
#             return Response(serializer.data)

#         return Response(serializer.errors, status=400)

#     if request.method == 'DELETE':
#         create_log(request.user, "Deleted Nearby Place", place.name_en)
#         place.delete()
        
#         return Response(status=204)
    


@api_view(['GET'])
@permission_classes([AllowAny])
def nearby_place_detail(request, pk):
    try:
        place = NearbyPlace.objects.get(id=pk)
    except NearbyPlace.DoesNotExist:
        return Response({"error": "Place not found"}, status=404)
    serializer = NearbyPlaceSerializer(place)
    return Response(serializer.data)



@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def admin_nearby_place_detail(request, pk):
    try:
        place = NearbyPlace.objects.get(id=pk)
    except NearbyPlace.DoesNotExist:
        return Response({"error": "Place not found"}, status=404)

    if request.method == 'PUT':
        serializer = NearbyPlaceSerializer(
            place,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            create_log(request.user, "Updated Nearby Place", place.name_en)
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        create_log(request.user, "Deleted Nearby Place", place.name_en)
        place.delete()
        
        return Response(status=204)







# Services
# @api_view(['GET', 'POST'])
# @permission_classes([AllowAny])
# def services(request):
#     if request.method == 'GET':
#         data = Service.objects.filter(is_active=True)
#         serializer = ServiceSerializer(data, many=True)
#         return Response(serializer.data)
#     serializer = ServiceSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         create_log(request.user, "Created Service", serializer.data['id'])
#         return Response(serializer.data, status=201)
#     return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def services(request):
    data = Service.objects.filter(is_active=True)
    serializer = ServiceSerializer(data, many=True)
    return Response(serializer.data)
    








# @api_view(["GET"])
# @permission_classes([IsAdminUser])
# def admin_services(request):
#     services = Service.objects.all().order_by("-id")
#     serializer = ServiceSerializer(services, many=True)
#     return Response(serializer.data)

@api_view(["GET",'POST'])
@permission_classes([IsAdminUser])
def admin_services(request):
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



# @api_view(['GET', 'PUT', 'DELETE'])
# @permission_classes([AllowAny])
# def service_detail(request, pk):
#     try:
#         service = Service.objects.get(id=pk)
#     except Service.DoesNotExist:
#         return Response({"error": "Service not found"}, status=404)
#     if request.method == 'GET':
#         serializer = ServiceSerializer(service)
#         return Response(serializer.data)
    

#     if request.method == 'PUT':
#         serializer = ServiceSerializer(service, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             create_log(request.user, "Updated Service", service.id)
#             return Response(serializer.data)
#         return Response(serializer.errors, status=400)

#     if request.method == 'DELETE':
#         create_log(request.user, "Deleted Service", service.title)
#         service.delete()
#         return Response(status=204)
    



@api_view(['GET'])
@permission_classes([AllowAny])
def service_detail(request, pk):
    try:
        service = Service.objects.get(id=pk)
    except Service.DoesNotExist:
        return Response({"error": "Service not found"}, status=404)
    serializer = ServiceSerializer(service)
    return Response(serializer.data)



@api_view(['PUT',"PATCH", 'DELETE'])
@permission_classes([IsAdminUser])
def admin_service_detail(request, pk):
    try:
        service = Service.objects.get(id=pk)
    except Service.DoesNotExist:
        return Response({"error": "Service not found"}, status=404)
    

    if request.method in ['PUT',"PATCH"]:
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
# @api_view(['GET', 'POST'])
# @permission_classes([AllowAny])
# def galleries(request):

#     if request.method == 'GET':
#         data = Gallery.objects.filter(is_active=True)
#         serializer = GallerySerializer(data, many=True)
#         return Response(serializer.data)
#     serializer = GallerySerializer(data=request.data)
#     if serializer.is_valid():
#         gallery = serializer.save()
#         create_log(request.user if request.user.is_authenticated else None, "Created Gallery", f" Gallery {gallery.title_en}")
#         return Response(serializer.data, status=201)
#     return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def galleries(request):
    data = Gallery.objects.filter(is_active=True)
    serializer = GallerySerializer(data, many=True)
    return Response(serializer.data)
    

# Gallery List/Create
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def admin_galleries(request):

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
# @api_view(['GET', 'PUT', 'DELETE'])
# @permission_classes([IsAdminUser])
# def gallery_detail(request, pk):
#     try:
#         gallery = Gallery.objects.get(id=pk)
#     except Gallery.DoesNotExist:
#         return Response(
#             {"error": "Gallery not found"},
#             status=status.HTTP_404_NOT_FOUND
#         )
#     # GET
#     if request.method == 'GET':
#         serializer = GallerySerializer(gallery)
#         return Response(serializer.data)
#     # PUT
#     if request.method == 'PUT':
#         serializer = GallerySerializer(
#             gallery,
#             data=request.data,
#             partial=True
#         )
#         if serializer.is_valid():
#             serializer.save()
#             create_log(request.user if request.user.is_authenticated else None, "Updated Gallery", f" Gallery {gallery.title_en}")
#             return Response(serializer.data)
#         return Response(serializer.errors, status=400)
#     # DELETE
#     create_log(request.user if request.user.is_authenticated else None, "Deleted Gallery", f" Gallery {gallery.title_en}")
#     gallery.delete()
#     return Response(status=204)




@api_view(['GET'])
@permission_classes([AllowAny])
def gallery_detail(request, pk):
    try:
        gallery = Gallery.objects.get(id=pk)
    except Gallery.DoesNotExist:
        return Response(
            {"error": "Gallery not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = GallerySerializer(gallery)
    return Response(serializer.data)


@api_view(['PUT','PATCH', 'DELETE'])
@permission_classes([IsAdminUser])
def admin_gallery_detail(request, pk):
    try:
        gallery = Gallery.objects.get(id=pk)
    except Gallery.DoesNotExist:
        return Response(
            {"error": "Gallery not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # PUT
    if request.method in ['PUT','PATCH']:
        serializer = GallerySerializer(
            gallery,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            updated_gallery = serializer.save()
            create_log(request.user if request.user.is_authenticated else None, "Updated Gallery", updated_gallery.title_en)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    # DELETE
    create_log(request.user if request.user.is_authenticated else None, "Deleted Gallery", gallery.title_en)
    gallery.delete()
    return Response(status=204)









# Gallery Images
@api_view(['POST'])
@permission_classes([IsAdminUser])
def gallery_images(request):

    serializer = GalleryImageSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        create_log(request.user, "Created Gallery Image", serializer.data['id'])
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdminUser])
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

# @api_view(['GET', 'POST'])
# @permission_classes([AllowAny])
# def reviews(request):
#     if request.method == 'GET':
#         if request.user.is_authenticated and request.user.is_staff:
#             data = Review.objects.all().order_by('-created_at')
#         else:
#             data = Review.objects.filter(
#                 is_active=True
#             ).order_by('-created_at')
#         serializer = ReviewSerializer(data, many=True)
#         return Response(serializer.data)
#     serializer = ReviewSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=201)
#     return Response(serializer.errors, status=400)
@api_view(['GET'])
@permission_classes([AllowAny])
def reviews(request):
    data = Review.objects.filter(
            is_active=True
        ).order_by('-created_at')
    serializer = ReviewSerializer(data, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_reviews(request):
    reviews = Review.objects.all().order_by("-created_at")
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)



@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
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
# @api_view(['GET', 'PUT'])
# @permission_classes([AllowAny])
# def contact_settings(request):
#     setting = ContactSetting.objects.first()

#     if not setting:
#         setting = ContactSetting.objects.create(
#             phone="",
#             email="",
#             address=""
#         )

#     if request.method == 'GET':
#         serializer = ContactSettingSerializer(setting)
#         return Response(serializer.data)

#     serializer = ContactSettingSerializer(
#         setting,
#         data=request.data,
#         partial=True
#     )

#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data)

#     return Response(serializer.errors, status=400)




@api_view(['GET'])
@permission_classes([AllowAny])
def public_contact_settings(request):
    setting = ContactSetting.objects.first()
    if not setting:
        setting = ContactSetting.objects.create(
            phone="",
            email="",
            address=""
        )
        serializer = ContactSettingSerializer(setting)
        return Response(serializer.data)
    

@api_view(['GET', 'PUT' , 'PATCH'])
@permission_classes([IsAdminUser])
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





# @api_view(['GET', 'POST'])
# @permission_classes([IsAdminUser])
# def contact_messages(request):

#     if request.method == 'GET':
#         messages = ContactMessage.objects.all().order_by('-created_at')
#         serializer = ContactMessageSerializer(messages, many=True)
#         return Response(serializer.data)

#     serializer = ContactMessageSerializer(data=request.data)

#     if serializer.is_valid():
#         message = serializer.save()
#         create_notification("New Contact Message",f"Message from {message.name}","contact")
#         return Response(serializer.data, status=201)

#     return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_contact_messages(request):
    serializer = ContactMessageSerializer(data=request.data)

    if serializer.is_valid():
        message = serializer.save()
        create_notification("New Contact Message",f"Message from {message.name}","contact")
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def contact_messages(request):
    messages = ContactMessage.objects.all().order_by('-created_at')
    serializer = ContactMessageSerializer(messages, many=True)
    return Response(serializer.data)







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




@api_view(["GET"])
@permission_classes([AllowAny])
def system_settings(request):
    setting, created = SystemSetting.objects.get_or_create(id=1)
    serializer = SystemSettingSerializer(setting)
    return Response(serializer.data)

    


@api_view(["GET", "PUT" , 'PATCH'])
@permission_classes([IsAdminUser])
def admin_system_settings(request):
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


@api_view(["GET", "PUT",'PATCH', "DELETE"])
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

    # لا تسمح بالدفع إذا كان الحجز ملغى
    if booking.booking_status == "cancelled":
        return Response(
            {"error": "This booking has been cancelled"},
            status=400
        )

    # لا تسمح بالدفع إذا انتهت مدة الـ 24 ساعة
    if booking.expires_at and booking.expires_at <= timezone.now():
        booking.booking_status = "cancelled"
        booking.save(update_fields=["booking_status"])

        return Response(
            {"error": "This booking has expired"},
            status=400
        )

    # إذا كان الحجز مؤكد ومدفوع مسبقاً
    if booking.booking_status == "confirmed":
        return Response(
            {"error": "This booking is already confirmed"},
            status=400
        )

    card_number = request.data.get(
        "card_number",
        ""
    ).replace(" ", "")

    # نجاح الدفع التجريبي
    if card_number == "4242424242424242":

        payment = Payment.objects.filter(
            booking=booking,
            status="pending"
        ).order_by("-created_at").first()

        booking.payment_status = "paid"
        booking.payment_method = "online"
        booking.booking_status = "confirmed"
        booking.confirmed_by = "Online"
        booking.save()

        if payment:
            payment.status = "paid"
            payment.paid_at = timezone.now()
            payment.transaction_id = f"TEST-{booking.booking_code}"
            payment.save(
                update_fields=[
                    "status",
                    "paid_at",
                    "transaction_id",
                ]
            )

        try:
            send_booking_confirmation_email(booking)
        except Exception as e:
            print(f"Confirmation email failed for booking {booking.id}: {e}")


        try:
            send_reception_booking_notification(booking)
        except Exception as e:
            print(
                f"Reception notification email failed "
                f"for booking {booking.id}: {e}"
            )
    
        setting = AutoCloseSetting.objects.first()

        if setting and setting.auto_close_booked_room:
            if booking.room:
                booking.room.status = "OFF"
                booking.room.save()

        return Response({
            "message": "Payment successful",
            "booking_status": booking.booking_status,
            "payment_status": booking.payment_status,
            "booking_id": booking.id,
        })

    # فشل الدفع
    booking.payment_status = "failed"
    booking.payment_method = "online"

    booking.save()

    return Response(
        {
            "error": "Payment failed",
            "booking_status": booking.booking_status,
            "payment_status": booking.payment_status,
        },
        status=400
    )





@api_view(["GET"])
@permission_classes([IsAdminUser])
def booking_detail(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response({"error" : "booking not found"} , status=404)
    serializer = BookingSerializer(booking)
    return Response(serializer.data)





# @api_view(["PATCH"])
# @permission_classes([IsAdminUser])
# def update_booking_notes(request, booking_id):
#     booking = Booking.objects.get(id=booking_id)
#     booking.notes = request.data.get("notes", "")
#     booking.save()
#     return Response({"message": "Notes updated", "notes": booking.notes})

@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def update_booking_notes(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"},
            status=404
        )

    booking.notes = request.data.get("notes", "")
    booking.save()

    return Response({
        "message": "Notes updated",
        "notes": booking.notes
    })





@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def update_booking_status(request, booking_id):

    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"},
            status=404
        )

    new_status = request.data.get("booking_status")

    allowed_statuses = [
        "pending",
        "confirmed",
        "cancelled",
    ]

    if new_status not in allowed_statuses:
        return Response(
            {
                "error": "Invalid booking status"
            },
            status=400
        )

    booking.booking_status = new_status
    booking.save()

    if new_status == "confirmed":

        booking.confirmed_by = request.user.username
        booking.save()

        try:
            send_booking_confirmation_email(booking)
        except Exception as e:
            print(
                f"Confirmation email failed for booking "
                f"{booking.id}: {e}"
            )
        try:
            send_reception_booking_notification(booking)
        except Exception as e:
            print(
                f"Reception notification email failed "
                f"for booking {booking.id}: {e}"
            )
    

    return Response({
        "message": "Booking status updated successfully",
        "booking_status": booking.booking_status,
    })




@api_view(["GET"])
@permission_classes([AllowAny])
def active_hero_slides(request):
    slides = HeroSlide.objects.filter(is_active=True).order_by("order", "id")
    serializer = HeroSlideSerializer(slides, many=True, context={"request": request})
    return Response(serializer.data)



@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
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
@permission_classes([IsAdminUser])
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
@permission_classes([AllowAny])
def amenities(request):
    items = Amenity.objects.all()
    serializer = AmenitySerializer(items, many=True)
    return Response(serializer.data)



@api_view(["GET"])
@permission_classes([IsAdminUser])
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
@permission_classes([IsAdminUser])
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
@permission_classes([IsAdminUser])
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
@permission_classes([IsAdminUser])
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
@permission_classes([IsAdminUser])
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
@permission_classes([IsAdminUser])
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
@permission_classes([IsAdminUser])
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








@api_view(["POST"])
@permission_classes([AllowAny])
def zaincash_payment(request, booking_id):

    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"},
            status=404
        )

    # لا تسمح بالدفع إذا الحجز ملغي
    if booking.booking_status == "cancelled":
        return Response(
            {"error": "This booking has been cancelled"},
            status=400
        )

    # لا تسمح بالدفع إذا انتهت مدة الحجز
    if booking.expires_at and booking.expires_at <= timezone.now():
        booking.booking_status = "cancelled"
        booking.save(update_fields=["booking_status"])

        return Response(
            {"error": "This booking has expired"},
            status=400
        )

    # إذا مدفوع مسبقاً
    if booking.payment_status == "paid":
        return Response(
            {"error": "This booking is already paid"},
            status=400
        )

    # Payment الموجود أصلاً عند إنشاء الحجز
    payment = Payment.objects.filter(
        booking=booking,
        status="pending"
    ).order_by("-created_at").first()

    if not payment:
        return Response(
            {"error": "Pending payment not found"},
            status=400
        )
    signer = TimestampSigner()

    payment_access_token = signer.sign_object({
        "booking_id": booking.id,
        "payment_id": payment.id,
    })
    # روابط الرجوع بعد الدفع
    success_url = (
        f"http://localhost:3000/payment-success/"
        f"{booking.id}?access_token={payment_access_token}"
    )

    failure_url = (
        f"http://localhost:3000/payment-failed/{booking.id}"
    )

    try:

        result = create_payment(
            booking_id=booking.id,
            amount=booking.total_price,
            success_url=success_url,
            failure_url=failure_url,
            
        )

        transaction_details = result.get(
            "transactionDetails",
            {}
        )

        transaction_id = transaction_details.get(
            "transactionId"
        )

        external_reference = transaction_details.get(
            "externalReferenceId"
        )

        redirect_url = result.get("redirectUrl")

        if not redirect_url:
            return Response(
                {
                    "error": "ZainCash did not return redirect URL",
                    "zaincash_response": result,
                },
                status=400
            )

        # تحديث Payment الموجود
        payment.gateway = "zaincash"
        payment.transaction_id = transaction_id
        payment.external_reference = external_reference
        payment.status = "pending"
        payment.save()

        return Response({
            "success": True,
            "redirect_url": redirect_url,
            "transaction_id": transaction_id,
            "external_reference": external_reference,
            "booking_id": booking.id,
        })

    except Exception as e:

        print("ZainCash payment error:", e)

        return Response(
            {
                "success": False,
                "error": str(e),
            },
            status=400
        )






# @api_view(["GET"])
# @permission_classes([AllowAny])
# def public_payment_booking(request, booking_id):
#     try:
#         booking = Booking.objects.get(id=booking_id)
#     except Booking.DoesNotExist:
#         return Response(
#             {"error": "Booking not found"},
#             status=404
#         )

#     # لا نعرض الحجز إلا إذا كان الدفع ناجحاً
#     if booking.payment_status != "paid":
#         return Response(
#             {"error": "Payment has not been confirmed"},
#             status=400
#         )

#     serializer = BookingSerializer(booking)
#     return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def public_payment_booking(request, booking_id):

    access_token = request.query_params.get("access_token")

    if not access_token:
        return Response(
            {"error": "Payment access token is required"},
            status=401
        )

    signer = TimestampSigner()

    try:
        data = signer.unsign_object(
            access_token,
            max_age=60 * 60 * 24
        )

    except SignatureExpired:
        return Response(
            {"error": "Payment access token has expired"},
            status=401
        )

    except BadSignature:
        return Response(
            {"error": "Invalid payment access token"},
            status=401
        )

    # تأكد أن التوكن خاص بهذا الحجز
    if str(data.get("booking_id")) != str(booking_id):
        return Response(
            {"error": "Invalid payment access token"},
            status=401
        )

    try:
        booking = Booking.objects.get(id=booking_id)

    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"},
            status=404
        )

    # لا نعرض الحجز قبل نجاح الدفع
    if booking.payment_status != "paid":
        return Response(
            {"error": "Payment has not been confirmed"},
            status=400
        )

    serializer = BookingSerializer(booking)

    return Response(serializer.data)





# @api_view(["GET"])
# @permission_classes([AllowAny])
# def zaincash_verify_payment(request, booking_id):
#     """
#     Verify a ZainCash payment using the transaction inquiry API.
#     This endpoint is public because ZainCash redirects the customer
#     back without the customer's Django authentication session.
#     """

#     try:
#         booking = Booking.objects.get(id=booking_id)
#     except Booking.DoesNotExist:
#         return Response(
#             {"error": "Booking not found"},
#             status=404
#         )

#     # Get the latest pending ZainCash payment
#     payment = (
#         Payment.objects
#         .filter(
#             booking=booking,
#             gateway="zaincash"
#         )
#         .order_by("-created_at")
#         .first()
#     )

#     if not payment:
#         return Response(
#             {"error": "ZainCash payment not found"},
#             status=404
#         )

#     if not payment.transaction_id:
#         return Response(
#             {"error": "ZainCash transaction ID is missing"},
#             status=400
#         )

#     # If already paid, don't call ZainCash again
#     if payment.status == "paid" and booking.payment_status == "paid":
#         return Response({
#             "success": True,
#             "payment_status": "paid",
#             "booking_status": booking.booking_status,
#             "booking": BookingSerializer(booking).data,
#         })

#     try:
#         zain_response = inquiry_payment(
#             payment.transaction_id
#         )

#     except Exception as e:
#         print(
#             f"ZainCash inquiry failed for booking "
#             f"{booking.id}: {e}"
#         )

#         return Response(
#             {
#                 "success": False,
#                 "error": "Unable to verify payment with ZainCash",
#                 "details": str(e),
#             },
#             status=502
#         )

#     print("ZainCash final inquiry:", zain_response)

#     # ZainCash returns the transaction status
#     transaction_status = str(
#         zain_response.get("status", "")
#     ).upper()

#     transaction_details = zain_response.get(
#         "transactionDetails",
#         {}
#     )

#     # Sometimes status/details can be nested differently
#     if not transaction_status:
#         transaction_status = str(
#             transaction_details.get("status", "")
#         ).upper()

#     # =====================================================
#     # SUCCESS
#     # =====================================================

#     if transaction_status == "SUCCESS":

#         payment.status = "paid"
#         payment.paid_at = timezone.now()

#         # Keep the transaction ID if ZainCash returned one
#         returned_transaction_id = (
#             transaction_details.get("transactionId")
#         )

#         if returned_transaction_id:
#             payment.transaction_id = returned_transaction_id

#         payment.save()

#         booking.payment_status = "paid"
#         booking.payment_method = "online"
#         booking.booking_status = "confirmed"
#         booking.confirmed_by = "ZainCash"

#         booking.save()

#         # Send confirmation emails
#         try:
#             send_booking_confirmation_email(booking)
#         except Exception as e:
#             print(
#                 f"Confirmation email failed for booking "
#                 f"{booking.id}: {e}"
#             )

#         try:
#             send_reception_booking_notification(booking)
#         except Exception as e:
#             print(
#                 f"Reception notification email failed "
#                 f"for booking {booking.id}: {e}"
#             )

#         # Automatically close the room if enabled
#         setting = AutoCloseSetting.objects.first()

#         if setting and setting.auto_close_booked_room:
#             if booking.room:
#                 booking.room.status = "OFF"
#                 booking.room.is_available = False
#                 booking.room.save()

#         return Response({
#             "success": True,
#             "payment_status": "paid",
#             "booking_status": "confirmed",
#             "booking": BookingSerializer(booking).data,
#             "transaction": zain_response,
#         })

#     # =====================================================
#     # FAILED
#     # =====================================================

#     if transaction_status in [
#         "FAILED",
#         "EXPIRED",
#         "REFUNDED",
#     ]:

#         payment.status = "failed"
#         payment.save(update_fields=["status"])

#         booking.payment_status = "failed"

#         if booking.booking_status != "cancelled":
#             booking.booking_status = "pending"

#         booking.save(
#             update_fields=[
#                 "payment_status",
#                 "booking_status",
#             ]
#         )

#         return Response({
#             "success": False,
#             "payment_status": "failed",
#             "booking_status": booking.booking_status,
#             "message": "ZainCash payment was not successful",
#             "transaction": zain_response,
#         })

#     # =====================================================
#     # STILL PENDING
#     # =====================================================

#     return Response({
#         "success": False,
#         "payment_status": "pending",
#         "booking_status": booking.booking_status,
#         "message": "ZainCash payment is still pending",
#         "transaction": zain_response,
#     })


# @api_view(["GET"])
# @permission_classes([AllowAny])
# def zaincash_verify_payment(request, booking_id):
#     """
#     Securely verify a ZainCash payment.

#     The booking is confirmed ONLY if the ZainCash inquiry confirms:
#     - transaction status = SUCCESS
#     - transaction ID matches our Payment
#     - external reference matches our Payment
#     - order ID matches our booking ID
#     - amount matches our Payment amount
#     - currency matches our Payment currency
#     """

#     token = request.query_params.get("token")

#     if not token:
#         return Response(
#             {
#                 "success": False,
#                 "error": "Missing ZainCash payment token"
#             },
#             status=400
#         )

#     # =====================================================
#     # VERIFY ZAINCASH JWT
#     # =====================================================

#     try:

#         token_payload = verify_zaincash_callback_token(
#             token
#         )

#     except ValueError as e:

#         print(
#             "SECURITY ALERT: Invalid ZainCash callback token"
#         )

#         return Response(
#             {
#                 "success": False,
#                 "error": "Invalid or expired payment token"
#             },
#             status=401
#         )

#     # =====================================================
#     # 1. Get booking
#     # =====================================================

#     try:
#         booking = Booking.objects.get(id=booking_id)

#     except Booking.DoesNotExist:
#         return Response(
#             {
#                 "success": False,
#                 "error": "Booking not found"
#             },
#             status=404
#         )

#         # =====================================================
#     # VERIFY TOKEN DATA AGAINST BOOKING
#     # =====================================================

#     token_data = token_payload.get("data", token_payload)

#     token_transaction_id = str(
#         token_data.get(
#             "transactionId",
#             ""
#         )
#     ).strip()

#     token_order_id = str(
#         token_data.get(
#             "orderId",
#             ""
#         )
#     ).strip()

#     token_external_reference = str(
#         token_data.get(
#             "merchantReferenceId",
#             token_data.get(
#                 "externalReferenceId",
#                 ""
#             )
#         )
#     ).strip()

#     token_status = str(
#         token_data.get(
#             "currentStatus",
#             token_data.get(
#                 "status",
#                 ""
#             )
#         )
#     ).upper()

#     token_amount_data = token_data.get(
#         "amount",
#         {}
#     )

#     token_amount = token_amount_data.get(
#         "value"
#     )

#     token_currency = str(
#         token_amount_data.get(
#             "currency",
#             ""
#         )
#     ).upper()



#     # =====================================================
#     # 2. Get ZainCash payment for this booking
#     # =====================================================

#     payment = (
#         Payment.objects
#         .filter(
#             booking=booking,
#             gateway="zaincash"
#         )
#         .order_by("-created_at")
#         .first()
#     )

#     if not payment:
#         return Response(
#             {
#                 "success": False,
#                 "error": "ZainCash payment not found"
#             },
#             status=404
#         )




#         # =====================================================
#     # TOKEN ↔ DATABASE VERIFICATION
#     # =====================================================

#     if token_order_id != str(booking.id):

#         return Response(
#             {
#                 "success": False,
#                 "error": "Payment order verification failed"
#             },
#             status=400
#         )

#     if token_transaction_id != str(
#         payment.transaction_id
#     ).strip():

#         return Response(
#             {
#                 "success": False,
#                 "error": "Payment transaction verification failed"
#             },
#             status=400
#         )

#     stored_external_reference = str(
#         payment.external_reference or ""
#     ).strip()

#     if not token_external_reference:
#         return Response(
#             {
#                 "success": False,
#                 "error": "Payment reference missing from token"
#             },
#             status=400
#         )

#     if (
#         not stored_external_reference
#         or token_external_reference != stored_external_reference
#     ):
#         print(
#             "SECURITY ALERT: External reference mismatch",
#             {
#                 "booking_id": booking.id,
#                 "stored": stored_external_reference,
#                 "returned": token_external_reference,
#             }
#         )

#         return Response(
#             {
#                 "success": False,
#                 "error": "Payment reference verification failed"
#             },
#             status=400
#         )

        

    

#     try:

#         if token_amount is None:
#             raise ValueError()

#         if Decimal(str(token_amount)) != Decimal(
#             str(payment.amount)
#         ):
#             return Response(
#                 {
#                     "success": False,
#                     "error": "Payment amount verification failed"
#                 },
#                 status=400
#             )

#     except Exception:

#         return Response(
#             {
#                 "success": False,
#                 "error": "Invalid payment amount"
#             },
#             status=400
#         )


#     if token_currency != str(
#         payment.currency
#     ).upper():

#         return Response(
#             {
#                 "success": False,
#                 "error": "Payment currency verification failed"
#             },
#             status=400
#         )





#     # =====================================================
#     # 3. Make sure we have our original transaction ID
#     # =====================================================

#     if not payment.transaction_id:
#         return Response(
#             {
#                 "success": False,
#                 "error": "ZainCash transaction ID is missing"
#             },
#             status=400
#         )

#     # =====================================================
#     # 4. If already successfully paid
#     # =====================================================

#     if (
#         payment.status == "paid"
#         and booking.payment_status == "paid"
#         and booking.booking_status == "confirmed"
#     ):
#         return Response(
#             {
#                 "success": True,
#                 "payment_status": "paid",
#                 "booking_status": "confirmed",
#                 "booking": BookingSerializer(booking).data,
#             }
#         )

#     # =====================================================
#     # 5. Ask ZainCash directly
#     # =====================================================

#     try:

#         zain_response = inquiry_payment(
#             payment.transaction_id
#         )

#     except Exception as e:

#         print(
#             f"ZainCash inquiry failed for booking "
#             f"{booking.id}: {e}"
#         )

#         return Response(
#             {
#                 "success": False,
#                 "error": "Unable to verify payment with ZainCash",
#             },
#             status=502
#         )

#     print("ZainCash final inquiry:", zain_response)

#     # =====================================================
#     # 6. Extract ZainCash response
#     # =====================================================

#     transaction_status = str(
#         zain_response.get("status", "")
#     ).upper()

#     transaction_details = zain_response.get(
#         "transactionDetails",
#         {}
#     )

#     # Some responses may contain status inside transactionDetails
#     if not transaction_status:

#         transaction_status = str(
#             transaction_details.get("status", "")
#         ).upper()

#     # =====================================================
#     # 7. If transaction is not SUCCESS
#     # =====================================================

#     if transaction_status != "SUCCESS":

#         if transaction_status in [
#             "FAILED",
#             "EXPIRED",
#             "REFUNDED"
#         ]:

#             payment.status = "failed"
#             payment.save(
#                 update_fields=["status"]
#             )

#             booking.payment_status = "failed"

#             if booking.booking_status != "cancelled":
#                 booking.booking_status = "pending"

#             booking.save(
#                 update_fields=[
#                     "payment_status",
#                     "booking_status"
#                 ]
#             )

#             return Response(
#                 {
#                     "success": False,
#                     "payment_status": "failed",
#                     "booking_status": booking.booking_status,
#                     "message": "ZainCash payment was not successful"
#                 }
#             )

#         # Still pending / unknown status

#         return Response(
#             {
#                 "success": False,
#                 "payment_status": "pending",
#                 "booking_status": booking.booking_status,
#                 "message": "ZainCash payment is still pending"
#             }
#         )

#     # =====================================================
#     # 8. SUCCESS
#     # Now verify EVERYTHING
#     # =====================================================

#     # -----------------------------------------------------
#     # 8.1 Transaction ID
#     # -----------------------------------------------------

#     returned_transaction_id = str(
#         transaction_details.get(
#             "transactionId",
#             ""
#         )
#     ).strip()

#     stored_transaction_id = str(
#         payment.transaction_id
#     ).strip()

#     if not returned_transaction_id:
#         return Response(
#             {
#                 "success": False,
#                 "error": "ZainCash did not return transaction ID"
#             },
#             status=400
#         )

#     if returned_transaction_id != stored_transaction_id:

#         print(
#             "SECURITY ALERT: Transaction ID mismatch",
#             {
#                 "booking_id": booking.id,
#                 "stored": stored_transaction_id,
#                 "returned": returned_transaction_id,
#             }
#         )

#         return Response(
#             {
#                 "success": False,
#                 "error": "Transaction verification failed"
#             },
#             status=400
#         )

#     # -----------------------------------------------------
#     # 8.2 External Reference
#     # -----------------------------------------------------

#     returned_external_reference = str(
#         transaction_details.get(
#             "externalReferenceId",
#             ""
#         )
#     ).strip()

#     stored_external_reference = str(
#         payment.external_reference or ""
#     ).strip()

#     if not returned_external_reference:
#         return Response(
#             {
#                 "success": False,
#                 "error": "ZainCash did not return external reference"
#             },
#             status=400
#         )

#     if (
#         not stored_external_reference
#         or
#         returned_external_reference != stored_external_reference
#     ):

#         print(
#             "SECURITY ALERT: External reference mismatch",
#             {
#                 "booking_id": booking.id,
#                 "stored": stored_external_reference,
#                 "returned": returned_external_reference,
#             }
#         )

#         return Response(
#             {
#                 "success": False,
#                 "error": "Payment reference verification failed"
#             },
#             status=400
#         )

#     # -----------------------------------------------------
#     # 8.3 Order ID
#     # -----------------------------------------------------

#     returned_order_id = str(
#         transaction_details.get(
#             "orderId",
#             ""
#         )
#     ).strip()

#     expected_order_id = str(
#         booking.id
#     ).strip()

#     if not returned_order_id:
#         return Response(
#             {
#                 "success": False,
#                 "error": "ZainCash did not return order ID"
#             },
#             status=400
#         )

#     if returned_order_id != expected_order_id:

#         print(
#             "SECURITY ALERT: Order ID mismatch",
#             {
#                 "booking_id": booking.id,
#                 "expected": expected_order_id,
#                 "returned": returned_order_id,
#             }
#         )

#         return Response(
#             {
#                 "success": False,
#                 "error": "Order verification failed"
#             },
#             status=400
#         )

#     # -----------------------------------------------------
#     # 8.4 Amount
#     # -----------------------------------------------------

#     zain_amount_data = transaction_details.get(
#         "amount",
#         {}
#     )

#     zain_amount_value = zain_amount_data.get(
#         "value"
#     )

#     if zain_amount_value is None:
#         return Response(
#             {
#                 "success": False,
#                 "error": "ZainCash did not return payment amount"
#             },
#             status=400
#         )

#     try:

#         zain_amount = Decimal(
#             str(zain_amount_value)
#         )

#         expected_amount = Decimal(
#             str(payment.amount)
#         )

#     except Exception:

#         return Response(
#             {
#                 "success": False,
#                 "error": "Invalid payment amount returned by ZainCash"
#             },
#             status=400
#         )

#     if zain_amount != expected_amount:

#         print(
#             "SECURITY ALERT: Amount mismatch",
#             {
#                 "booking_id": booking.id,
#                 "expected": str(expected_amount),
#                 "returned": str(zain_amount),
#             }
#         )

#         return Response(
#             {
#                 "success": False,
#                 "error": "Payment amount verification failed"
#             },
#             status=400
#         )

#     # -----------------------------------------------------
#     # 8.5 Currency
#     # -----------------------------------------------------

#     zain_currency = str(
#         zain_amount_data.get(
#             "currency",
#             ""
#         )
#     ).upper().strip()

#     expected_currency = str(
#         payment.currency
#     ).upper().strip()

#     if zain_currency != expected_currency:

#         print(
#             "SECURITY ALERT: Currency mismatch",
#             {
#                 "booking_id": booking.id,
#                 "expected": expected_currency,
#                 "returned": zain_currency,
#             }
#         )

#         return Response(
#             {
#                 "success": False,
#                 "error": "Payment currency verification failed"
#             },
#             status=400
#         )

#     # =====================================================
#     # 9. EVERYTHING MATCHED
#     # Now and ONLY now confirm payment
#     # =====================================================

#     payment.status = "paid"
#     payment.paid_at = timezone.now()

#     # Keep original transaction ID
#     payment.transaction_id = stored_transaction_id

#     payment.save()

#     # -----------------------------------------------------
#     # Confirm booking
#     # -----------------------------------------------------

#     booking.payment_status = "paid"
#     booking.payment_method = "online"
#     booking.booking_status = "confirmed"
#     booking.confirmed_by = "ZainCash"

#     booking.save()

#     # =====================================================
#     # 10. Send confirmation email
#     # =====================================================

#     try:

#         send_booking_confirmation_email(
#             booking
#         )

#     except Exception as e:

#         print(
#             f"Confirmation email failed for booking "
#             f"{booking.id}: {e}"
#         )

#     # =====================================================
#     # 11. Send reception notification
#     # =====================================================

#     try:

#         send_reception_booking_notification(
#             booking
#         )

#     except Exception as e:

#         print(
#             f"Reception notification email failed "
#             f"for booking {booking.id}: {e}"
#         )

#     # =====================================================
#     # 12. Close room automatically
#     # =====================================================

#     setting = AutoCloseSetting.objects.first()

#     if (
#         setting
#         and setting.auto_close_booked_room
#         and booking.room
#     ):

#         booking.room.status = "OFF"
#         booking.room.is_available = False

#         booking.room.save()

#     # =====================================================
#     # 13. Final response
#     # =====================================================

#     return Response(
#         {
#             "success": True,
#             "payment_status": "paid",
#             "booking_status": "confirmed",
#             "booking": BookingSerializer(
#                 booking
#             ).data,
#             "transaction": zain_response,
#         }
#     )



# @api_view(["GET"])
# @permission_classes([AllowAny])
# def zaincash_verify_payment(request, booking_id):
#     """
#     Securely verify a ZainCash payment.

#     Booking is confirmed ONLY when:
#     - JWT is valid and signed by ZainCash
#     - JWT is not expired / not-before valid
#     - JWT status indicates SUCCESS
#     - token orderId matches booking ID
#     - token transactionId matches our Payment
#     - token externalReferenceId matches our Payment
#     - token amount matches our Payment amount
#     - token currency matches our Payment currency
#     - ZainCash inquiry confirms SUCCESS
#     - inquiry transactionId matches our Payment
#     - inquiry externalReferenceId matches our Payment
#     - inquiry orderId matches our Booking
#     - inquiry amount matches our Payment
#     - inquiry currency matches our Payment

#     Replay protection:
#     - Each callback token is hashed before storage
#     - A used token can never be used again
#     - select_for_update() prevents concurrent confirmation
#     """

#     import hashlib
#     from decimal import Decimal

#     token = request.query_params.get("token")

#     if not token:
#         return Response(
#             {
#                 "success": False,
#                 "error": "Missing ZainCash payment token"
#             },
#             status=400
#         )

#     # =========================================================
#     # 1. VERIFY ZAINCASH JWT
#     # =========================================================

#     try:
#         token_payload = verify_zaincash_callback_token(token)

#     except ValueError as e:
#         print("SECURITY ALERT: Invalid ZainCash callback token")
#         print("ZainCash token verification error:", str(e))

#         return Response(
#             {
#                 "success": False,
#                 "error": "Invalid or expired payment token"
#             },
#             status=401
#         )

#     # =========================================================
#     # 2. CREATE TOKEN HASH
#     # =========================================================

#     token_hash = hashlib.sha256(
#         token.encode("utf-8")
#     ).hexdigest()

#     # =========================================================
#     # 3. EXTRACT TOKEN DATA
#     # =========================================================

#     token_data = token_payload.get(
#         "data",
#         token_payload
#     )

#     token_transaction_id = str(
#         token_data.get(
#             "transactionId",
#             ""
#         )
#     ).strip()

#     token_order_id = str(
#         token_data.get(
#             "orderId",
#             ""
#         )
#     ).strip()

#     token_external_reference = str(
#         token_data.get(
#             "merchantReferenceId",
#             token_data.get(
#                 "externalReferenceId",
#                 ""
#             )
#         )
#     ).strip()

#     token_status = str(
#         token_data.get(
#             "currentStatus",
#             token_data.get(
#                 "status",
#                 ""
#             )
#         )
#     ).upper().strip()

#     token_amount_data = token_data.get(
#         "amount",
#         {}
#     )

#     token_amount = token_amount_data.get(
#         "value"
#     )

#     token_currency = str(
#         token_amount_data.get(
#             "currency",
#             ""
#         )
#     ).upper().strip()

#     # =========================================================
#     # 4. VERIFY TOKEN STATUS
#     # =========================================================

#     if token_status != "SUCCESS":

#         print(
#             "SECURITY ALERT: Invalid ZainCash token status",
#             {
#                 "booking_id": booking_id,
#                 "token_status": token_status,
#             }
#         )

#         return Response(
#             {
#                 "success": False,
#                 "error": "Payment token is not successful"
#             },
#             status=400
#         )

#     # =========================================================
#     # 5. ATOMIC DATABASE TRANSACTION
#     #
#     # select_for_update() prevents two requests from
#     # processing the same booking/payment simultaneously.
#     # =========================================================

#     with transaction.atomic():

#         # -----------------------------------------------------
#         # Lock booking row
#         # -----------------------------------------------------

#         try:
#             booking = (
#                 Booking.objects
#                 .select_for_update()
#                 .get(id=booking_id)
#             )

#         except Booking.DoesNotExist:

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Booking not found"
#                 },
#                 status=404
#             )

#         # -----------------------------------------------------
#         # Get and lock ZainCash payment
#         # -----------------------------------------------------

#         payment = (
#             Payment.objects
#             .select_for_update()
#             .filter(
#                 booking=booking,
#                 gateway="zaincash"
#             )
#             .order_by("-created_at")
#             .first()
#         )

#         if not payment:

#             return Response(
#                 {
#                     "success": False,
#                     "error": "ZainCash payment not found"
#                 },
#                 status=404
#             )

#         # =====================================================
#         # 6. REPLAY PROTECTION
#         # =====================================================

#         # If this exact token was already consumed,
#         # NEVER process it again.

#         if payment.zaincash_token_used:

#             print(
#                 "SECURITY ALERT: ZainCash token replay detected",
#                 {
#                     "booking_id": booking.id,
#                     "payment_id": payment.id,
#                     "transaction_id": payment.transaction_id,
#                 }
#             )

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Payment token has already been used"
#                 },
#                 status=409
#             )

#         # -----------------------------------------------------
#         # Check whether this token was already used
#         # by another payment.
#         # -----------------------------------------------------

#         existing_token_payment = (
#             Payment.objects
#             .filter(
#                 zaincash_token_hash=token_hash,
#                 zaincash_token_used=True
#             )
#             .exclude(id=payment.id)
#             .first()
#         )

#         if existing_token_payment:

#             print(
#                 "SECURITY ALERT: ZainCash token reused on another payment",
#                 {
#                     "booking_id": booking.id,
#                     "payment_id": payment.id,
#                     "previous_payment_id": existing_token_payment.id,
#                 }
#             )

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Payment token has already been used"
#                 },
#                 status=409
#             )

#         # -----------------------------------------------------
#         # If this payment already has a DIFFERENT token hash,
#         # do not allow replacing the original token.
#         # -----------------------------------------------------

#         if (
#             payment.zaincash_token_hash
#             and payment.zaincash_token_hash != token_hash
#         ):

#             print(
#                 "SECURITY ALERT: Different ZainCash token submitted",
#                 {
#                     "booking_id": booking.id,
#                     "payment_id": payment.id,
#                 }
#             )

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Invalid payment token"
#                 },
#                 status=400
#             )

#         # =====================================================
#         # 7. BASIC PAYMENT VALIDATION
#         # =====================================================

#         if not payment.transaction_id:

#             return Response(
#                 {
#                     "success": False,
#                     "error": "ZainCash transaction ID is missing"
#                 },
#                 status=400
#             )

#         stored_external_reference = str(
#             payment.external_reference or ""
#         ).strip()

#         if not stored_external_reference:

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Payment reference missing"
#                 },
#                 status=400
#             )

#         # =====================================================
#         # 8. TOKEN ↔ DATABASE VERIFICATION
#         # =====================================================

#         # -----------------------------------------------------
#         # Order ID
#         # -----------------------------------------------------

#         if token_order_id != str(booking.id):

#             print(
#                 "SECURITY ALERT: Order ID mismatch",
#                 {
#                     "booking_id": booking.id,
#                     "expected": str(booking.id),
#                     "returned": token_order_id,
#                 }
#             )

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Payment order verification failed"
#                 },
#                 status=400
#             )

#         # -----------------------------------------------------
#         # Transaction ID
#         # -----------------------------------------------------

#         stored_transaction_id = str(
#             payment.transaction_id
#         ).strip()

#         if token_transaction_id != stored_transaction_id:

#             print(
#                 "SECURITY ALERT: Token transaction ID mismatch",
#                 {
#                     "booking_id": booking.id,
#                     "expected": stored_transaction_id,
#                     "returned": token_transaction_id,
#                 }
#             )

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Payment transaction verification failed"
#                 },
#                 status=400
#             )

#         # -----------------------------------------------------
#         # External Reference
#         # -----------------------------------------------------

#         if not token_external_reference:

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Payment reference missing from token"
#                 },
#                 status=400
#             )

#         if token_external_reference != stored_external_reference:

#             print(
#                 "SECURITY ALERT: External reference mismatch",
#                 {
#                     "booking_id": booking.id,
#                     "stored": stored_external_reference,
#                     "returned": token_external_reference,
#                 }
#             )

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Payment reference verification failed"
#                 },
#                 status=400
#             )

#         # -----------------------------------------------------
#         # Amount
#         # -----------------------------------------------------

#         if token_amount is None:

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Payment amount missing from token"
#                 },
#                 status=400
#             )

#         try:

#             token_amount_decimal = Decimal(
#                 str(token_amount)
#             )

#             expected_amount = Decimal(
#                 str(payment.amount)
#             )

#         except Exception:

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Invalid payment amount"
#                 },
#                 status=400
#             )

#         if token_amount_decimal != expected_amount:

#             print(
#                 "SECURITY ALERT: Token amount mismatch",
#                 {
#                     "booking_id": booking.id,
#                     "expected": str(expected_amount),
#                     "returned": str(token_amount_decimal),
#                 }
#             )

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Payment amount verification failed"
#                 },
#                 status=400
#             )

#         # -----------------------------------------------------
#         # Currency
#         # -----------------------------------------------------

#         expected_currency = str(
#             payment.currency
#         ).upper().strip()

#         if token_currency != expected_currency:

#             print(
#                 "SECURITY ALERT: Token currency mismatch",
#                 {
#                     "booking_id": booking.id,
#                     "expected": expected_currency,
#                     "returned": token_currency,
#                 }
#             )

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Payment currency verification failed"
#                 },
#                 status=400
#             )

#         # =====================================================
#         # 9. ASK ZAINCASH DIRECTLY
#         # =====================================================

#         try:

#             zain_response = inquiry_payment(
#                 payment.transaction_id
#             )

#         except Exception as e:

#             print(
#                 f"ZainCash inquiry failed for booking "
#                 f"{booking.id}: {e}"
#             )

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Unable to verify payment with ZainCash"
#                 },
#                 status=502
#             )

#         print(
#             "ZainCash final inquiry:",
#             zain_response
#         )

#         # =====================================================
#         # 10. EXTRACT ZAINCASH RESPONSE
#         # =====================================================

#         transaction_status = str(
#             zain_response.get(
#                 "status",
#                 ""
#             )
#         ).upper().strip()

#         transaction_details = zain_response.get(
#             "transactionDetails",
#             {}
#         )

#         if not transaction_status:

#             transaction_status = str(
#                 transaction_details.get(
#                     "status",
#                     ""
#                 )
#             ).upper().strip()

#         # =====================================================
#         # 11. ZAINCASH MUST CONFIRM SUCCESS
#         # =====================================================

#         if transaction_status != "SUCCESS":

#             if transaction_status in [
#                 "FAILED",
#                 "EXPIRED",
#                 "REFUNDED"
#             ]:

#                 payment.status = "failed"

#                 payment.save(
#                     update_fields=["status"]
#                 )

#                 booking.payment_status = "failed"

#                 if booking.booking_status != "cancelled":
#                     booking.booking_status = "pending"

#                 booking.save(
#                     update_fields=[
#                         "payment_status",
#                         "booking_status"
#                     ]
#                 )

#                 return Response(
#                     {
#                         "success": False,
#                         "payment_status": "failed",
#                         "booking_status": booking.booking_status,
#                         "message": "ZainCash payment was not successful"
#                     }
#                 )

#             return Response(
#                 {
#                     "success": False,
#                     "payment_status": "pending",
#                     "booking_status": booking.booking_status,
#                     "message": "ZainCash payment is still pending"
#                 }
#             )

#         # =====================================================
#         # 12. VERIFY ZAINCASH TRANSACTION ID
#         # =====================================================

#         returned_transaction_id = str(
#             transaction_details.get(
#                 "transactionId",
#                 ""
#             )
#         ).strip()

#         if not returned_transaction_id:

#             return Response(
#                 {
#                     "success": False,
#                     "error": "ZainCash did not return transaction ID"
#                 },
#                 status=400
#             )

#         if returned_transaction_id != stored_transaction_id:

#             print(
#                 "SECURITY ALERT: Inquiry transaction ID mismatch",
#                 {
#                     "booking_id": booking.id,
#                     "expected": stored_transaction_id,
#                     "returned": returned_transaction_id,
#                 }
#             )

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Transaction verification failed"
#                 },
#                 status=400
#             )

#         # =====================================================
#         # 13. VERIFY EXTERNAL REFERENCE
#         # =====================================================

#         returned_external_reference = str(
#             transaction_details.get(
#                 "externalReferenceId",
#                 ""
#             )
#         ).strip()

#         if not returned_external_reference:

#             return Response(
#                 {
#                     "success": False,
#                     "error": "ZainCash did not return external reference"
#                 },
#                 status=400
#             )

#         if returned_external_reference != stored_external_reference:

#             print(
#                 "SECURITY ALERT: Inquiry external reference mismatch",
#                 {
#                     "booking_id": booking.id,
#                     "expected": stored_external_reference,
#                     "returned": returned_external_reference,
#                 }
#             )

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Payment reference verification failed"
#                 },
#                 status=400
#             )

#         # =====================================================
#         # 14. VERIFY ORDER ID
#         # =====================================================

#         returned_order_id = str(
#             transaction_details.get(
#                 "orderId",
#                 ""
#             )
#         ).strip()

#         expected_order_id = str(
#             booking.id
#         ).strip()

#         if not returned_order_id:

#             return Response(
#                 {
#                     "success": False,
#                     "error": "ZainCash did not return order ID"
#                 },
#                 status=400
#             )

#         if returned_order_id != expected_order_id:

#             print(
#                 "SECURITY ALERT: Inquiry order ID mismatch",
#                 {
#                     "booking_id": booking.id,
#                     "expected": expected_order_id,
#                     "returned": returned_order_id,
#                 }
#             )

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Order verification failed"
#                 },
#                 status=400
#             )

#         # =====================================================
#         # 15. VERIFY AMOUNT
#         # =====================================================

#         zain_amount_data = transaction_details.get(
#             "amount",
#             {}
#         )

#         zain_amount_value = zain_amount_data.get(
#             "value"
#         )

#         if zain_amount_value is None:

#             return Response(
#                 {
#                     "success": False,
#                     "error": "ZainCash did not return payment amount"
#                 },
#                 status=400
#             )

#         try:

#             zain_amount = Decimal(
#                 str(zain_amount_value)
#             )

#         except Exception:

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Invalid payment amount returned by ZainCash"
#                 },
#                 status=400
#             )

#         if zain_amount != expected_amount:

#             print(
#                 "SECURITY ALERT: Inquiry amount mismatch",
#                 {
#                     "booking_id": booking.id,
#                     "expected": str(expected_amount),
#                     "returned": str(zain_amount),
#                 }
#             )

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Payment amount verification failed"
#                 },
#                 status=400
#             )

#         # =====================================================
#         # 16. VERIFY CURRENCY
#         # =====================================================

#         zain_currency = str(
#             zain_amount_data.get(
#                 "currency",
#                 ""
#             )
#         ).upper().strip()

#         if zain_currency != expected_currency:

#             print(
#                 "SECURITY ALERT: Inquiry currency mismatch",
#                 {
#                     "booking_id": booking.id,
#                     "expected": expected_currency,
#                     "returned": zain_currency,
#                 }
#             )

#             return Response(
#                 {
#                     "success": False,
#                     "error": "Payment currency verification failed"
#                 },
#                 status=400
#             )

#         # =====================================================
#         # 17. EVERYTHING MATCHED
#         #
#         # NOW AND ONLY NOW consume the token.
#         # =====================================================

#         payment.status = "paid"
#         payment.paid_at = timezone.now()

#         payment.transaction_id = stored_transaction_id

#         # Save SHA-256 hash of the callback token.
#         # Never store the raw token.
#         payment.zaincash_token_hash = token_hash
#         payment.zaincash_token_used = True
#         payment.zaincash_token_used_at = timezone.now()

#         payment.save(
#             update_fields=[
#                 "status",
#                 "paid_at",
#                 "transaction_id",
#                 "zaincash_token_hash",
#                 "zaincash_token_used",
#                 "zaincash_token_used_at",
#             ]
#         )

#         # =====================================================
#         # 18. CONFIRM BOOKING
#         # =====================================================

#         booking.payment_status = "paid"
#         booking.payment_method = "online"
#         booking.booking_status = "confirmed"
#         booking.confirmed_by = "ZainCash"

#         booking.save(
#             update_fields=[
#                 "payment_status",
#                 "payment_method",
#                 "booking_status",
#                 "confirmed_by",
#             ]
#         )

#         # =====================================================
#         # 19. SEND CONFIRMATION EMAIL
#         # =====================================================

#         try:

#             send_booking_confirmation_email(
#                 booking
#             )

#         except Exception as e:

#             print(
#                 f"Confirmation email failed for booking "
#                 f"{booking.id}: {e}"
#             )

#         # =====================================================
#         # 20. SEND RECEPTION NOTIFICATION
#         # =====================================================

#         try:

#             send_reception_booking_notification(
#                 booking
#             )

#         except Exception as e:

#             print(
#                 f"Reception notification email failed "
#                 f"for booking {booking.id}: {e}"
#             )

#         # =====================================================
#         # 21. CLOSE ROOM AUTOMATICALLY
#         # =====================================================

#         setting = AutoCloseSetting.objects.first()

#         if (
#             setting
#             and setting.auto_close_booked_room
#             and booking.room
#         ):

#             booking.room.status = "OFF"
#             booking.room.is_available = False

#             booking.room.save()

#         # =====================================================
#         # 22. FINAL RESPONSE
#         # =====================================================

#         return Response(
#             {
#                 "success": True,
#                 "payment_status": "paid",
#                 "booking_status": "confirmed",
#                 "booking": BookingSerializer(
#                     booking
#                 ).data,
#                 "transaction": zain_response,
#             }
#         )






@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def zaincash_verify_payment(request, booking_id):
    """
    Securely verify a ZainCash payment.

    IMPORTANT:
    The callback JWT is NOT trusted for payment confirmation.
    We only decode it to obtain reference information.

    Final payment confirmation is done ONLY through
    ZainCash Inquiry API.

    Checks:
    - Token exists
    - Token can be decoded
    - Token status = SUCCESS
    - Token orderId matches booking
    - Token transactionId matches Payment
    - Token externalReferenceId matches Payment
    - Token amount matches Payment
    - Token currency matches Payment
    - ZainCash Inquiry status = SUCCESS
    - Inquiry transactionId matches Payment
    - Inquiry externalReferenceId matches Payment
    - Inquiry orderId matches booking
    - Inquiry amount matches Payment
    - Inquiry currency matches Payment
    - Replay protection
    - select_for_update() prevents concurrent processing
    """

    import hashlib
    from decimal import Decimal
    import jwt

    # =========================================================
    # 1. GET CALLBACK TOKEN
    # =========================================================

    token = request.query_params.get("token")

    if not token:
        return Response(
            {
                "success": False,
                "error": "Missing ZainCash payment token"
            },
            status=400
        )

    # =========================================================
    # 2. DECODE TOKEN WITHOUT TRUSTING ITS SIGNATURE
    #
    # IMPORTANT:
    # We do NOT use this token as proof of payment.
    # ZainCash Inquiry API will be the final authority.
    # =========================================================

    try:
        token_payload = jwt.decode(
            token,
            options={
                "verify_signature": False,
                "verify_exp": False,
                "verify_nbf": False,
            }
        )

    except Exception as e:
        print(
            "SECURITY ALERT: Invalid ZainCash callback token format:",
            str(e)
        )

        return Response(
            {
                "success": False,
                "error": "Invalid payment token"
            },
            status=401
        )

    # =========================================================
    # 3. CREATE SHA-256 TOKEN HASH
    #
    # Never store the real token.
    # =========================================================

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    # =========================================================
    # 4. EXTRACT TOKEN DATA
    # =========================================================

    token_data = token_payload.get(
        "data",
        token_payload
    )

    token_transaction_id = str(
        token_data.get(
            "transactionId",
            ""
        )
    ).strip()

    token_order_id = str(
        token_data.get(
            "orderId",
            ""
        )
    ).strip()

    token_external_reference = str(
        token_data.get(
            "merchantReferenceId",
            token_data.get(
                "externalReferenceId",
                ""
            )
        )
    ).strip()

    token_status = str(
        token_data.get(
            "currentStatus",
            token_data.get(
                "status",
                ""
            )
        )
    ).upper().strip()

    token_amount_data = token_data.get(
        "amount",
        {}
    )

    if not isinstance(token_amount_data, dict):
        token_amount_data = {}

    token_amount = token_amount_data.get(
        "value"
    )

    token_currency = str(
        token_amount_data.get(
            "currency",
            ""
        )
    ).upper().strip()

    # =========================================================
    # 5. TOKEN MUST INDICATE SUCCESS
    # =========================================================

    if token_status != "SUCCESS":
        print(
            "SECURITY ALERT: Invalid ZainCash token status",
            {
                "booking_id": booking_id,
                "token_status": token_status,
            }
        )

        return Response(
            {
                "success": False,
                "error": "Payment token is not successful"
            },
            status=400
        )

    # =========================================================
    # 6. ATOMIC DATABASE TRANSACTION
    #
    # Lock booking + payment.
    # This prevents two simultaneous requests from
    # confirming the same payment.
    # =========================================================

    with transaction.atomic():

        # -----------------------------------------------------
        # Lock booking
        # -----------------------------------------------------

        try:
            booking = (
                Booking.objects
                .select_for_update()
                .get(id=booking_id)
            )

        except Booking.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "error": "Booking not found"
                },
                status=404
            )

        # -----------------------------------------------------
        # If booking is already paid
        # -----------------------------------------------------

        if booking.payment_status == "paid":
            print(
                "SECURITY ALERT: Replay attempt on already paid booking",
                {
                    "booking_id": booking.id,
                }
            )

            return Response(
                {
                    "success": False,
                    "error": "Payment has already been confirmed"
                },
                status=409
            )

        # -----------------------------------------------------
        # Lock ZainCash payment
        # -----------------------------------------------------

        payment = (
            Payment.objects
            .select_for_update()
            .filter(
                booking=booking,
                gateway="zaincash"
            )
            .order_by("-created_at")
            .first()
        )

        if not payment:
            return Response(
                {
                    "success": False,
                    "error": "ZainCash payment not found"
                },
                status=404
            )

        # =====================================================
        # 7. REPLAY PROTECTION
        # =====================================================

        if payment.zaincash_token_used:
            print(
                "SECURITY ALERT: ZainCash token replay detected",
                {
                    "booking_id": booking.id,
                    "payment_id": payment.id,
                    "transaction_id": payment.transaction_id,
                }
            )

            return Response(
                {
                    "success": False,
                    "error": "Payment token has already been used"
                },
                status=409
            )

        # -----------------------------------------------------
        # Check whether this token was used by another payment
        # -----------------------------------------------------

        existing_token_payment = (
            Payment.objects
            .filter(
                zaincash_token_hash=token_hash,
                zaincash_token_used=True
            )
            .exclude(id=payment.id)
            .first()
        )

        if existing_token_payment:
            print(
                "SECURITY ALERT: ZainCash token reused",
                {
                    "booking_id": booking.id,
                    "payment_id": payment.id,
                    "previous_payment_id": (
                        existing_token_payment.id
                    ),
                }
            )

            return Response(
                {
                    "success": False,
                    "error": "Payment token has already been used"
                },
                status=409
            )

        # -----------------------------------------------------
        # If payment already has a different token
        # don't allow token replacement
        # -----------------------------------------------------

        if (
            payment.zaincash_token_hash
            and payment.zaincash_token_hash != token_hash
        ):
            print(
                "SECURITY ALERT: Different ZainCash token submitted",
                {
                    "booking_id": booking.id,
                    "payment_id": payment.id,
                }
            )

            return Response(
                {
                    "success": False,
                    "error": "Invalid payment token"
                },
                status=400
            )

        # =====================================================
        # 8. BASIC PAYMENT VALIDATION
        # =====================================================

        if not payment.transaction_id:
            return Response(
                {
                    "success": False,
                    "error": "ZainCash transaction ID is missing"
                },
                status=400
            )

        stored_transaction_id = str(
            payment.transaction_id
        ).strip()

        stored_external_reference = str(
            payment.external_reference or ""
        ).strip()

        if not stored_external_reference:
            return Response(
                {
                    "success": False,
                    "error": "Payment reference missing"
                },
                status=400
            )

        # =====================================================
        # 9. TOKEN ↔ DATABASE VALIDATION
        # =====================================================

        # -----------------------------------------------------
        # Order ID
        # -----------------------------------------------------

        if token_order_id != str(booking.id):
            print(
                "SECURITY ALERT: Token order ID mismatch",
                {
                    "booking_id": booking.id,
                    "expected": str(booking.id),
                    "returned": token_order_id,
                }
            )

            return Response(
                {
                    "success": False,
                    "error": "Payment order verification failed"
                },
                status=400
            )

        # -----------------------------------------------------
        # Transaction ID
        # -----------------------------------------------------

        if token_transaction_id != stored_transaction_id:
            print(
                "SECURITY ALERT: Token transaction ID mismatch",
                {
                    "booking_id": booking.id,
                    "expected": stored_transaction_id,
                    "returned": token_transaction_id,
                }
            )

            return Response(
                {
                    "success": False,
                    "error": "Payment transaction verification failed"
                },
                status=400
            )

        # -----------------------------------------------------
        # External Reference
        # -----------------------------------------------------

        if not token_external_reference:
            return Response(
                {
                    "success": False,
                    "error": "Payment reference missing from token"
                },
                status=400
            )

        if token_external_reference != stored_external_reference:
            print(
                "SECURITY ALERT: Token external reference mismatch",
                {
                    "booking_id": booking.id,
                    "stored": stored_external_reference,
                    "returned": token_external_reference,
                }
            )

            return Response(
                {
                    "success": False,
                    "error": "Payment reference verification failed"
                },
                status=400
            )

        # -----------------------------------------------------
        # Amount
        # -----------------------------------------------------

        if token_amount is None:
            return Response(
                {
                    "success": False,
                    "error": "Payment amount missing from token"
                },
                status=400
            )

        try:
            token_amount_decimal = Decimal(
                str(token_amount)
            )

            expected_amount = Decimal(
                str(payment.amount)
            )

        except Exception:
            return Response(
                {
                    "success": False,
                    "error": "Invalid payment amount"
                },
                status=400
            )

        if token_amount_decimal != expected_amount:
            print(
                "SECURITY ALERT: Token amount mismatch",
                {
                    "booking_id": booking.id,
                    "expected": str(expected_amount),
                    "returned": str(token_amount_decimal),
                }
            )

            return Response(
                {
                    "success": False,
                    "error": "Payment amount verification failed"
                },
                status=400
            )

        # -----------------------------------------------------
        # Currency
        # -----------------------------------------------------

        expected_currency = str(
            payment.currency
        ).upper().strip()

        if token_currency != expected_currency:
            print(
                "SECURITY ALERT: Token currency mismatch",
                {
                    "booking_id": booking.id,
                    "expected": expected_currency,
                    "returned": token_currency,
                }
            )

            return Response(
                {
                    "success": False,
                    "error": "Payment currency verification failed"
                },
                status=400
            )

        # =====================================================
        # 10. ASK ZAINCASH DIRECTLY
        #
        # THIS IS THE FINAL PAYMENT VERIFICATION.
        # =====================================================

        try:
            zain_response = inquiry_payment(
                stored_transaction_id
            )

        except Exception as e:
            print(
                f"ZainCash inquiry failed for booking "
                f"{booking.id}: {e}"
            )

            return Response(
                {
                    "success": False,
                    "error": "Unable to verify payment with ZainCash"
                },
                status=502
            )

        print(
            "ZainCash inquiry status:",
            zain_response.get("status")
        )

        # =====================================================
        # 11. EXTRACT INQUIRY RESPONSE
        # =====================================================

        transaction_status = str(
            zain_response.get(
                "status",
                ""
            )
        ).upper().strip()

        transaction_details = zain_response.get(
            "transactionDetails",
            {}
        )

        if not isinstance(transaction_details, dict):
            transaction_details = {}

        if not transaction_status:
            transaction_status = str(
                transaction_details.get(
                    "status",
                    ""
                )
            ).upper().strip()

        # =====================================================
        # 12. ZAINCASH MUST CONFIRM SUCCESS
        # =====================================================

        if transaction_status != "SUCCESS":

            if transaction_status in [
                "FAILED",
                "EXPIRED",
                "REFUNDED"
            ]:

                payment.status = "failed"

                payment.save(
                    update_fields=["status"]
                )

                booking.payment_status = "failed"

                if booking.booking_status != "cancelled":
                    booking.booking_status = "pending"

                booking.save(
                    update_fields=[
                        "payment_status",
                        "booking_status"
                    ]
                )

                return Response(
                    {
                        "success": False,
                        "payment_status": "failed",
                        "booking_status": booking.booking_status,
                        "message": (
                            "ZainCash payment was not successful"
                        )
                    }
                )

            return Response(
                {
                    "success": False,
                    "payment_status": "pending",
                    "booking_status": booking.booking_status,
                    "message": (
                        "ZainCash payment is still pending"
                    )
                }
            )

        # =====================================================
        # 13. VERIFY INQUIRY TRANSACTION ID
        # =====================================================

        returned_transaction_id = str(
            transaction_details.get(
                "transactionId",
                ""
            )
        ).strip()

        if not returned_transaction_id:
            return Response(
                {
                    "success": False,
                    "error": (
                        "ZainCash did not return transaction ID"
                    )
                },
                status=400
            )

        if returned_transaction_id != stored_transaction_id:
            print(
                "SECURITY ALERT: Inquiry transaction ID mismatch",
                {
                    "booking_id": booking.id,
                    "expected": stored_transaction_id,
                    "returned": returned_transaction_id,
                }
            )

            return Response(
                {
                    "success": False,
                    "error": "Transaction verification failed"
                },
                status=400
            )

        # =====================================================
        # 14. VERIFY INQUIRY EXTERNAL REFERENCE
        # =====================================================

        returned_external_reference = str(
            transaction_details.get(
                "externalReferenceId",
                ""
            )
        ).strip()

        if not returned_external_reference:
            return Response(
                {
                    "success": False,
                    "error": (
                        "ZainCash did not return external reference"
                    )
                },
                status=400
            )

        if returned_external_reference != stored_external_reference:
            print(
                "SECURITY ALERT: Inquiry external reference mismatch",
                {
                    "booking_id": booking.id,
                    "expected": stored_external_reference,
                    "returned": returned_external_reference,
                }
            )

            return Response(
                {
                    "success": False,
                    "error": (
                        "Payment reference verification failed"
                    )
                },
                status=400
            )

        # =====================================================
        # 15. VERIFY INQUIRY ORDER ID
        # =====================================================

        returned_order_id = str(
            transaction_details.get(
                "orderId",
                ""
            )
        ).strip()

        expected_order_id = str(
            booking.id
        ).strip()

        if not returned_order_id:
            return Response(
                {
                    "success": False,
                    "error": "ZainCash did not return order ID"
                },
                status=400
            )

        if returned_order_id != expected_order_id:
            print(
                "SECURITY ALERT: Inquiry order ID mismatch",
                {
                    "booking_id": booking.id,
                    "expected": expected_order_id,
                    "returned": returned_order_id,
                }
            )

            return Response(
                {
                    "success": False,
                    "error": "Order verification failed"
                },
                status=400
            )

        # =====================================================
        # 16. VERIFY INQUIRY AMOUNT
        # =====================================================

        zain_amount_data = transaction_details.get(
            "amount",
            {}
        )

        if not isinstance(zain_amount_data, dict):
            zain_amount_data = {}

        zain_amount_value = zain_amount_data.get(
            "value"
        )

        if zain_amount_value is None:
            return Response(
                {
                    "success": False,
                    "error": (
                        "ZainCash did not return payment amount"
                    )
                },
                status=400
            )

        try:
            zain_amount = Decimal(
                str(zain_amount_value)
            )

        except Exception:
            return Response(
                {
                    "success": False,
                    "error": (
                        "Invalid payment amount returned by ZainCash"
                    )
                },
                status=400
            )

        if zain_amount != expected_amount:
            print(
                "SECURITY ALERT: Inquiry amount mismatch",
                {
                    "booking_id": booking.id,
                    "expected": str(expected_amount),
                    "returned": str(zain_amount),
                }
            )

            return Response(
                {
                    "success": False,
                    "error": (
                        "Payment amount verification failed"
                    )
                },
                status=400
            )

        # =====================================================
        # 17. VERIFY INQUIRY CURRENCY
        # =====================================================

        zain_currency = str(
            zain_amount_data.get(
                "currency",
                ""
            )
        ).upper().strip()

        if zain_currency != expected_currency:
            print(
                "SECURITY ALERT: Inquiry currency mismatch",
                {
                    "booking_id": booking.id,
                    "expected": expected_currency,
                    "returned": zain_currency,
                }
            )

            return Response(
                {
                    "success": False,
                    "error": (
                        "Payment currency verification failed"
                    )
                },
                status=400
            )

        # =====================================================
        # 18. EVERYTHING MATCHED
        #
        # NOW AND ONLY NOW:
        # - mark token as used
        # - mark payment as paid
        # - confirm booking
        # =====================================================

        payment.status = "paid"
        payment.paid_at = timezone.now()
        payment.transaction_id = stored_transaction_id

        # Never store the real JWT token
        payment.zaincash_token_hash = token_hash
        payment.zaincash_token_used = True
        payment.zaincash_token_used_at = timezone.now()

        payment.save(
            update_fields=[
                "status",
                "paid_at",
                "transaction_id",
                "zaincash_token_hash",
                "zaincash_token_used",
                "zaincash_token_used_at",
            ]
        )

        # =====================================================
        # 19. CONFIRM BOOKING
        # =====================================================

        booking.payment_status = "paid"
        booking.payment_method = "online"
        booking.booking_status = "confirmed"
        booking.confirmed_by = "ZainCash"

        booking.save(
            update_fields=[
                "payment_status",
                "payment_method",
                "booking_status",
                "confirmed_by",
            ]
        )

        # =====================================================
        # 20. SEND CONFIRMATION EMAIL
        # =====================================================

        try:
            send_booking_confirmation_email(
                booking
            )

        except Exception as e:
            print(
                f"Confirmation email failed for booking "
                f"{booking.id}: {e}"
            )

        # =====================================================
        # 21. SEND RECEPTION NOTIFICATION
        # =====================================================

        try:
            send_reception_booking_notification(
                booking
            )

        except Exception as e:
            print(
                f"Reception notification email failed "
                f"for booking {booking.id}: {e}"
            )

        # =====================================================
        # 22. CLOSE ROOM AUTOMATICALLY
        # =====================================================

        setting = AutoCloseSetting.objects.first()

        if (
            setting
            and setting.auto_close_booked_room
            and booking.room
        ):
            booking.room.status = "OFF"
            booking.room.is_available = False

            booking.room.save()

        # =====================================================
        # 23. FINAL RESPONSE
        # =====================================================

        return Response(
            {
                "success": True,
                "payment_status": "paid",
                "booking_status": "confirmed",
                "booking": BookingSerializer(
                    booking
                ).data,
                "transaction": {
                    "status": transaction_status
                }
            }
        )