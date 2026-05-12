from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


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


    # def clean(self):
    #     #تحقق من وجود حجز بنفس الفترة
    #     if Booking.objects.filter(
    #         room = self.room,
    #         check_in__lt = self.check_out,
    #         check_out__gt = self.check_in
    #     ).exists():
    #         raise ValidationError("This Room is already booked for these dates")
        
    # def save(self , *args , **kwargs):
    #     self.clean()
    #     super().save(*args, **kwargs)

    
    

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