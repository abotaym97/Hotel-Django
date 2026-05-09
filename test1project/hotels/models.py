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
    




class RoomType(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='room_types/')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
#Room
class Room(models.Model):

    ROOM_TYPES = [
        ('deluxe king' , 'Deluxe King'),
        ('deluxe twin' , 'Deluxe Twin'),
        ('junior king' , 'Junior King'),
        ('junior twin' , 'Junior Twin'),
        ('executive suite' , 'Executive Suite'),
    ]


    hotel = models.ForeignKey(Hotel,on_delete=models.CASCADE)
    room_number = models.IntegerField()
    room_type = models.ForeignKey(RoomType,on_delete=models.CASCADE,related_name="rooms")
    # room_type = models.CharField(max_length=50, choices=ROOM_TYPES , default='deluxe king')
    Price = models.DecimalField(max_digits=8,decimal_places=2)
    capacity = models.IntegerField(default=1)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.room_number} - {self.hotel.name}"
    
#Booking
class Booking(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
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
        return f"{self.user.username} - {self.room}"
    


class BookingSettings(models.Model):
    is_booking_open = models.BooleanField(default=True)
    booking_start_date = models.DateField()
    booking_end_date = models.DateField()
    min_nights = models.IntegerField(default=1)
    max_nights = models.IntegerField(default=30)

    def __str__(self):
        return "Booking Settings"
    


