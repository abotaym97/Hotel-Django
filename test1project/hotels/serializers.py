from rest_framework import serializers
from .models import Gallery, GalleryImage, Hotel, NearbyPlace, Restaurant, Review , Room , Booking , BookingSettings, RoomType, Service
from django.contrib.auth.models import User
from .models import BookingSettings
from datetime import timedelta
from django.contrib.auth.models import User
from .models import CustomerProfile
from django.contrib.auth.models import User, Group


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    room_type_name = serializers.CharField(
        source='room_type.name',
        read_only=True
    )

    room_type_image = serializers.ImageField(
        source='room_type.image',
        read_only=True
    )

    price = serializers.DecimalField(
        source='room_type.price',
        max_digits=8,
        decimal_places=2,
        read_only=True
    )

    capacity = serializers.IntegerField(
        source='room_type.capacity',
        read_only=True
    )

    class Meta:
        model = Room
        fields = [
            'id',
            'hotel',
            'room_number',
            'room_type',
            'room_type_name',
            'room_type_image',
            'price',
            'capacity',
            'is_available',
            'available_from',
            'available_to',
            'status',
        ]


class BookingSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    room_type_display = serializers.CharField(source='room.room_type', read_only=True)
    room_type = serializers.CharField(write_only=True)
    room = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(),
        required=False
)
    class Meta:
        model = Booking
        fields = [
            'id',
            'room',
            'room_type',
            'room_number',
            'room_type_display',
            'check_in',
            'check_out',
            'user',
            'guest_name',
            'guest_email',
            'guest_phone',
            'guest_country',
            'booking_code',
            'review_used',
            'adults',
            'children'
        ]
        read_only_fields = ['user']

    def validate(self, data):
        room_type = data.get('room_type')
        check_in = data.get('check_in')
        check_out = data.get('check_out')

        if check_in >= check_out:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date"
            )

        settings = BookingSettings.objects.first()

        if settings:
            if not settings.is_booking_open:
                raise serializers.ValidationError(
                    "Booking is currently closed"
                )

            if check_in < settings.booking_start_date:
                raise serializers.ValidationError(
                    "Booking is not available before this date"
                )

            if check_out > settings.booking_end_date:
                raise serializers.ValidationError(
                    "Booking is not available after this date"
                )

            nights = (check_out - check_in).days

            if nights < settings.min_nights:
                raise serializers.ValidationError(
                    f"Minimum stay is {settings.min_nights} nights"
                )

            if nights > settings.max_nights:
                raise serializers.ValidationError(
                    f"Maximum stay is {settings.max_nights} nights"
                )
        booked_rooms = Booking.objects.filter(
            room__room_type__name__iexact=room_type,
            check_in__lt=check_out,
            check_out__gt=check_in
        ).values_list('room_id', flat=True)

        available_room = Room.objects.filter(
            room_type__name__iexact=room_type,
            is_available=True,
            available_from__lte=check_in,
            available_to__gte=check_out,
            status='ON'
        ).exclude(
            id__in=booked_rooms
        ).first()

        if not available_room:
            raise serializers.ValidationError(
                "No available rooms for this type and dates"
            )

        data['room'] = available_room

        return data

    def create(self, validated_data):

        request = self.context.get('request')

        if request and request.user.is_authenticated:
            validated_data['user'] = request.user

        validated_data.pop('room_type', None)

        return Booking.objects.create(**validated_data)

    # def validate(self, data):
    #     room = data['room']
    #     check_in = data['check_in']
    #     check_out = data['check_out']

    #     if check_in >= check_out:
    #         raise serializers.ValidationError("check out date must be after check in date")
        
    #     if Booking.objects.filter(
    #         room = room,
    #         check_in__lt = check_out,
    #         check_out__gt = check_in
    #     ).exists():
    #         raise serializers.ValidationError("This room is already booked for these dates")
    #     return data


class RegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True)
    country = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone', 'country']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        phone = validated_data.pop('phone')
        country = validated_data.pop('country')

        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        CustomerProfile.objects.create(
            user=user,
            phone=phone,
            country=country
        )

        return user
    



class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['id', 'username', 'email', 'phone', 'country']







class BookingSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingSettings
        fields = '__all__'




class RoomTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoomType
        fields = [
            'id',
            'name',
            'image',
            'description',
            'price',
            'capacity',
        ]


#restaurant
class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'


# Nearby Places
class NearbyPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NearbyPlace
        fields = '__all__'


# Services
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"

#Gallery Serializer

class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = "__all__"


class GallerySerializer(serializers.ModelSerializer):
    images = GalleryImageSerializer(many=True, read_only=True)

    class Meta:
        model = Gallery
        fields = "__all__"


## Review Serializer

class ReviewSerializer(serializers.ModelSerializer):
    booking_code = serializers.CharField(
        source="booking.booking_code",
        read_only=True
    )

    class Meta:
        model = Review
        fields = [
            'id',
            'booking',
            'booking_code',
            'name',
            'rating',
            'comment_en',
            'created_at',
            'is_active'
            
        ]




#User Serializer
class StaffUserSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        required=False
    )

    password = serializers.CharField(
        write_only=True,
        required=False
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'is_active',
            'groups',
            'password',
        ]

    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password')

        user = User.objects.create_user(
            username=validated_data.get('email'),
            email=validated_data.get('email'),
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_staff=True,
            is_active=validated_data.get('is_active', True),
        )

        user.groups.set(groups)
        return user