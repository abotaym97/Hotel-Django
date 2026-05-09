from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , IsAdminUser , AllowAny
from rest_framework import status
from .serializers import RegisterSerializer, RoomTypeSerializer , UserSerializer
from .models import Hotel , Room , Booking , BookingSettings, RoomType
from .serializers import HotelSerializer , RoomSerializer , BookingSerializer , BookingSettingsSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser



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
@permission_classes([IsAuthenticated])
def bookings(request):
    if request.method == 'GET':
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

    rooms = Room.objects.filter(is_available=True)

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
    

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


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
@api_view(['POST'])
def register(request):

    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    return Response(
        {"message": "User created successfully"},
        status=status.HTTP_201_CREATED
    )




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
@permission_classes([IsAdminUser])
def dashboard_stats(request):

    total_rooms = Room.objects.count()

    available_rooms = Room.objects.filter(
        is_available=True
    ).count()

    total_bookings = Booking.objects.count()

    occupied_rooms = total_rooms - available_rooms

    occupancy_rate = 0

    if total_rooms > 0:
        occupancy_rate = round(
            (occupied_rooms / total_rooms) * 100
        )
    recent_bookings = Booking.objects.select_related(
    'user',
    'room'
    ).order_by('-created_at')[:5]
    return Response({
        "total_rooms": total_rooms,
        "available_rooms": available_rooms,
        "total_bookings": total_bookings,
        "occupancy_rate": occupancy_rate,
        "recent_bookings": [
    {
        "id": booking.id,
        "user": booking.user.username,
        "room": booking.room.room_number,
        "check_in": booking.check_in,
        "check_out": booking.check_out,
    }
    for booking in recent_bookings
        ]
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
@api_view(['DELETE'])
def room_type_detail(request, pk):

    try:
        room_type = RoomType.objects.get(id=pk)
    except RoomType.DoesNotExist:
        return Response(status=404)

    room_type.delete()
    return Response(status=204)