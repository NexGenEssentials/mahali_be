from django.db import models
from django.contrib.auth import get_user_model
import django_filters

from users.models import CustomUser, UserRoles

User = get_user_model()

class Feature(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Car(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=100,default='Sedan')
    year = models.PositiveIntegerField()
    mileage = models.PositiveIntegerField()
    fuel_type = models.CharField(max_length=50, choices=[('Petrol', 'Petrol'), ('Diesel', 'Diesel'), ('Electric', 'Electric')])
    transmission = models.CharField(max_length=50, choices=[('Automatic', 'Automatic'), ('Manual', 'Manual')])
    seats = models.PositiveIntegerField()
    luggage_capacity = models.PositiveIntegerField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    features = models.ManyToManyField(Feature, related_name="cars", blank=True)
    owner = models.ForeignKey(
        CustomUser,
        null=True,  
        blank=True,
        on_delete=models.CASCADE,
        related_name="owned_cars",
        limit_choices_to={"role__in": [UserRoles.ADMIN, UserRoles.SERVICE_PROVIDER]},  
    )
    def get_related_cars(self):
        """Returns cars with similar brand, fuel type, or transmission"""
        return Car.objects.filter(
            brand=self.brand,
            fuel_type=self.fuel_type,
            transmission=self.transmission,
            category=self.category
        ).exclude(id=self.id)[:5] 

    def __str__(self):
        return f"{self.brand} {self.name} ({self.year})"



class CarImage(models.Model):
    car = models.ForeignKey(Car, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='car_images/')

    def __str__(self):
        return f"Image for {self.car.name}"

class Booking(models.Model):
    car = models.ForeignKey(Car, related_name='bookings', on_delete=models.CASCADE)
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='bookings_general'  
    )
  
    user = models.ForeignKey( 'users.CustomUser', on_delete=models.CASCADE, related_name='bookings_car_rental')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled')])

    def __str__(self):
        return f"Booking {self.id} for {self.car.name}"

