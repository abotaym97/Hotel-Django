from rest_framework import serializers
from .models import ActivityLog, Gallery, GalleryImage, HeroSlide, Hotel, NearbyPlace, Restaurant, Review , Room , Booking , BookingSettings, RoomType, Service
from django.contrib.auth.models import User
from .models import BookingSettings ,Facility, ContactSetting , ContactMessage
from datetime import timedelta
from django.contrib.auth.models import User
from .models import CustomerProfile,Amenity, Currency,HotelSettings,Notification,DashboardCardSetting,SystemSetting , CustomerRecord,MealOption
from django.contrib.auth.models import User, Group
from .models import PolicySetting,SocialMediaSetting







class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'


class HotelSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelSettings
        fields = "__all__"


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"




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



class MealOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealOption
        fields = "__all__"



class BookingSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    room_type_display = serializers.CharField(source='room.room_type', read_only=True)
    room_type = serializers.CharField(write_only=True)
    room = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(),
        required=False
)
    room_price = serializers.SerializerMethodField()

    def get_room_price(self, obj):
        return obj.room.room_type.price if obj.room and obj.room.room_type else 0



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
            'children',
            'created_at',
            'is_read',
            'meal_option',
            'meal_price',
            'payment_status',
            'payment_method',
            'total_price',
            "room_price",
            "notes",
        ]
        read_only_fields = ['user' , 'total_price', 'payment_status']

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
            # is_available=True,
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
    full_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    country = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'phone', 'country']

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):

        full_name = validated_data.pop('full_name')
        phone = validated_data.pop('phone')
        country = validated_data.pop('country')

        email = validated_data.get('email')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data['password'],
            first_name=full_name
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
        fields = "__all__"


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
            'is_superuser',
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
    



#Logs 
class ActivityLogSerializer(serializers.ModelSerializer):

    user_email = serializers.CharField(
        source='user.email',
        read_only=True
    )

    class Meta:
        model = ActivityLog

        fields = [
            'id',
            'user_email',
            'action',
            'target',
            'created_at',
        ]







#Contact Us
class ContactSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSetting
        fields = "__all__"


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = "__all__"



#Dashboard
class DashboardCardSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardCardSetting
        fields = "__all__"





class SystemSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSetting
        fields = "__all__"





#Customer Profiles
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile, Booking


class AdminProfileListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.first_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    joined_at = serializers.DateTimeField(source="user.date_joined", read_only=True)
    total_bookings = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "username",
            "name",
            "email",
            "phone",
            "country",
            "joined_at",
            "total_bookings",
        ]

    def get_total_bookings(self, obj):
        return Booking.objects.filter(user=obj.user).count()


class AdminProfileBookingSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source="room.room_number", read_only=True)
    room_type = serializers.CharField(source="room.room_type.name", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "room_number",
            "room_type",
            "guest_name",
            "guest_email",
            "guest_phone",
            "guest_country",
            "check_in",
            "check_out",
            "created_at",
            "booking_code",
            "adults",
            "children",
        ]


class AdminProfileDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.first_name", required=False )
    email = serializers.EmailField(source="user.email", required=False)
    username = serializers.CharField(source="user.username", read_only=True)
    joined_at = serializers.DateTimeField(source="user.date_joined", read_only=True)
    bookings = serializers.SerializerMethodField()
    total_bookings = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "username",
            "name",
            "email",
            "phone",
            "country",
            "joined_at",
            "total_bookings",
            "bookings",
        ]
        read_only_fields = ["user", "username", "joined_at", "total_bookings", "bookings"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        user = instance.user
        if "first_name" in user_data:
            user.first_name = user_data["first_name"]

        if "email" in user_data:
            user.email = user_data["email"]
            user.username = user_data["email"]

        user.save()

        instance.phone = validated_data.get("phone", instance.phone)
        instance.country = validated_data.get("country", instance.country)
        instance.save()

        return instance

    def get_bookings(self, obj):
        bookings = Booking.objects.filter(user=obj.user).order_by("-created_at")
        return AdminProfileBookingSerializer(bookings, many=True).data

    def get_total_bookings(self, obj):
        return Booking.objects.filter(user=obj.user).count()
    


class CustomerRecordSerializer(serializers.ModelSerializer):
        class Meta:
            model = CustomerRecord
            fields = "__all__"




class HeroSlideSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = HeroSlide
        fields = [
            "id",
            "image",
            "image_url",
            "order",
            "is_active",
            "created_at",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")

        if obj.image:
            return request.build_absolute_uri(obj.image.url)

        return None
    




class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = "__all__"





from .models import UserTableSetting

class UserTableSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTableSetting
        fields = ["id", "table_name", "visible_columns"]





class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = "__all__"







class PolicySettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicySetting
        fields = "__all__"



class SocialMediaSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaSetting
        fields = "__all__"