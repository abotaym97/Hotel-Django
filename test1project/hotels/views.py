from urllib import request

from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , IsAdminUser , AllowAny
from rest_framework import status
from .serializers import GalleryImageSerializer, RegisterSerializer, RestaurantSerializer, ReviewSerializer, RoomTypeSerializer , UserSerializer
from .models import GalleryImage, Hotel, NearbyPlace, Profile, Restaurant, Review , Room , Booking , BookingSettings, RoomType, Service , Gallery
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
from .serializers import NearbyPlaceSerializer , RestaurantSerializer , ServiceSerializer , GallerySerializer




@api_view(['GET'])
def get_hotels(request):
    hotels = Hotel.objects.all()
    serializer = HotelSerializer(hotels , many = True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
def get_rooms(request):
    if request.method == 'GET':
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = RoomSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


@api_view(['GET' , 'POST'])
@permission_classes([AllowAny])
def bookings(request):
    if request.method == 'GET':
        if request.user.is_authenticated and request.user.is_staff:
            bookings = Booking.objects.all()
        else:
            bookings = Booking.objects.filter(user=request.user)




        serializer = BookingSerializer(bookings, many = True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = BookingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([AllowAny])
def available_rooms(request):
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    room_type = request.GET.get('room_type')

    rooms = Room.objects.filter(is_available=True, status='ON')

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

    # 🔐 هذا أهم سطر
    if booking.user != request.user:
        return Response({"error": "Not allowed"}, status=403)


    if request.method == 'PUT':
        serializer = BookingSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors)

    if request.method == 'DELETE':
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

    return Response(data)


@api_view(['GET'])
def hotel_detail(request, id):
    try:
        hotel = Hotel.objects.get(id=id)
    except Hotel.DoesNotExist:
        return Response({"error": "Hotel not found"})

    serializer = HotelSerializer(hotel)
    return Response(serializer.data)


@api_view(['GET'])
def rooms_by_hotel(request, hotel_id):
    rooms = Room.objects.filter(hotel_id=hotel_id)
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)




# للتسجيل
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def register(request):

#     username = request.data.get('username')
#     email = request.data.get('email')
#     password = request.data.get('password')

#     if User.objects.filter(username=username).exists():
#         return Response(
#             {"error": "Username already exists"},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     user = User.objects.create_user(
#         username=username,
#         email=email,
#         password=password
#     )

#     return Response(
#         {"message": "User created successfully"},
#         status=status.HTTP_201_CREATED
#     )
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        Profile.objects.create(
            user=user,
            phone=request.data.get('phone'),
            country=request.data.get('country'))
        
        
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
        return Response(serializer.data)

    return Response(serializer.errors, status=400)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    today = date.today()

    total_room_types = RoomType.objects.count()
    total_rooms = Room.objects.count()

    available_rooms = Room.objects.filter(
        is_available=True,
        status='ON'
    ).count()

    unavailable_rooms = Room.objects.filter(
        status='OFF'
    ).count()

    current_bookings = Booking.objects.filter(
        check_in__lte=today,
        check_out__gt=today
    ).count()

    current_guests = current_bookings

    departures_today = Booking.objects.filter(
        check_out=today
    ).count()

    arrivals = Booking.objects.filter(
        check_in__gt=today
    ).count()

    return Response({
        "total_room_types": total_room_types,
        "total_rooms": total_rooms,
        "available_rooms": available_rooms,
        "unavailable_rooms": unavailable_rooms,
        "current_bookings": current_bookings,
        "current_guests": current_guests,
        "departures_today": departures_today,
        "arrivals": arrivals,
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_bookings(request):

    bookings = Booking.objects.select_related(
        'user',
        'room'
    ).order_by('-created_at')

    serializer = BookingSerializer(bookings, many=True)

    return Response(serializer.data)



@api_view(['DELETE'])
def delete_room(request, pk):

    try:
        room = Room.objects.get(id=pk)

    except Room.DoesNotExist:
        return Response(
            {"error": "Room not found"},
            status=404
        )

    room.delete()

    return Response(
        {"message": "Room deleted"},
        status=200
    )




@api_view(['PUT', 'PATCH'])
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
        return Response(serializer.data)

    return Response(serializer.errors, status=400)



# لإلغاء الحجز
@api_view(['DELETE'])
def delete_booking(request, pk):

    try:
        booking = Booking.objects.get(id=pk)

    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"},
            status=404
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
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':

        if room_type.rooms.exists():
            return Response(
                {"error": "Cannot delete this room type because it has rooms."},
                status=400
            )

        room_type.delete()
        return Response(status=204)



# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def profile(request):
#     profile, created = Profile.objects.get_or_create(
#         user=request.user,
#         defaults={
#             "phone": "",
#             "country": ""
#         }
#     )

#     data = {
#         "first_name": request.user.first_name or request.user.username,
#         "email": request.user.email,
#         "phone": profile.phone,
#         "country": profile.country,
#     }

#     return Response(data)



@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_bookings(request):
    bookings = Booking.objects.all().order_by('-id')
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)


from django.utils.timezone import now

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

    return Response({
        "message": f"{len(rooms)} rooms updated successfully"
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
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)





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
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        restaurant.delete()
        return Response(status=204)





# Nearby Places
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def nearby_places(request):

    if request.method == 'GET':
        places = NearbyPlace.objects.filter(is_active=True)
        serializer = NearbyPlaceSerializer(places, many=True)
        return Response(serializer.data)

    serializer = NearbyPlaceSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)

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
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
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
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


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
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
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
        serializer.save()
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
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    # DELETE
    gallery.delete()
    return Response(status=204)


# Gallery Images
@api_view(['POST'])
@permission_classes([AllowAny])
def gallery_images(request):

    serializer = GalleryImageSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
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
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    # DELETE
    image.delete()
    return Response(status=204)




# Review List/Create
# Reviews

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def reviews(request):

    if request.method == 'GET':
        data = Review.objects.filter(is_active=True)
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
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    # DELETE
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

    serializer = ReviewSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(
            booking=booking,
            is_active=False
        )

        booking.review_used = True
        booking.save()

        return Response(
            {"message": "Review submitted and waiting for approval"},
            status=201
        )

    return Response(serializer.errors, status=400)