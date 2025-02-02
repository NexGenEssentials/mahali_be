from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    ]

    SERVICE_TYPES = [
        ('tour', 'Tour'),
        ('accommodation', 'Accommodation'),
        ('car_rental', 'Car Rental'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service_name = models.CharField(max_length=255)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service_name} - {self.status}"
