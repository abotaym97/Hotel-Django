from rest_framework import serializers
from .models import Hotel , Room , Booking , BookingSettings, RoomType
from django.contrib.auth.models import User
from .models import BookingSettings
from datetime import timedelta
from django.contrib.auth.models import User
from .models import CustomerProfile


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    room_type_image = serializers.ImageField(source='room_type.image', read_only=True)

    class Meta:
        model = Room
        fields = [
            'id',
            'hotel',
            'room_number',
            'room_type',
            'room_type_name',
            'room_type_image',
            'Price',
            'capacity',
            'is_available',
            'available_from',
            'available_to',
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
            available_to__gte=check_out
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
            username=validated_data['username'],
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
        fields = '__all__'