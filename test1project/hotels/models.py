from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import uuid


#Hotel
class Hotel(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    address = models.TextField()

    def __str__(self):
        return self.name
    



#RoomType
class RoomType(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='room_types/')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.IntegerField(default=1)

    def __str__(self):
        return self.name
#Room
class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room_number = models.IntegerField()
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.PROTECT,
        related_name="rooms"
    )
    is_available = models.BooleanField(default=True)
    available_from = models.DateField(null=True, blank=True)
    available_to = models.DateField(null=True, blank=True)
    STATUS_CHOICES = (
        ('ON', 'Available'),
        ('OFF', 'Closed'),
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ON'
    )

    def __str__(self):
        return f"Room {self.room_number} - {self.room_type.name}"
    
#Booking
class Booking(models.Model):
    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)
    guest_country = models.CharField(max_length=100)
    # user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User , on_delete=models.SET_NULL,null=True, blank=True)
    room = models.ForeignKey(Room , on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    booking_code = models.CharField(max_length=20,unique=True,blank=True,null=True)
    review_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):

        if not self.booking_code:
            self.booking_code = (
                "NDH-" +
                str(uuid.uuid4()).split("-")[0].upper()
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.guest_name} - Room {self.room.room_number}"
    


class BookingSettings(models.Model):
    is_booking_open = models.BooleanField(default=True)
    booking_start_date = models.DateField()
    booking_end_date = models.DateField()
    min_nights = models.IntegerField(default=1)
    max_nights = models.IntegerField(default=30)

    def __str__(self):
        return "Booking Settings"
    



class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=30)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
    


#restaurant
class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='restaurants/')
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    price_info = models.TextField(blank=True)
    breakfast_time = models.CharField(max_length=100, blank=True)
    lunch_time = models.CharField(max_length=100, blank=True)
    dinner_time = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    


# Nearby Places

class NearbyPlace(models.Model):
    name_ar = models.CharField(max_length=150)
    name_en = models.CharField(max_length=150)
    image = models.ImageField(upload_to='nearby_places/')
    location = models.CharField(max_length=255)
    distance = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name_en
    


# Services
class Service(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='services/')
    price = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    

# Gallery
class Gallery(models.Model):
    title_ar = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title_en


class GalleryImage(models.Model):
    gallery = models.ForeignKey(
        Gallery,
        related_name="images",
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="gallery/")

    def __str__(self):
        return self.gallery.title_en
    


#Testimonials / Reviews

class Review(models.Model):
    booking = models.OneToOneField(Booking,on_delete=models.CASCADE,related_name="review",null=True,blank=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='reviews/')
    rating = models.IntegerField(default=5)
    comment_ar = models.TextField()
    comment_en = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    



