from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from users.models import CustomUser
import random
import string

def generate_booking_reference():
        while True:
            # Generate 4 numeric digits and 4 uppercase alphabetic characters
            digits = ''.join(random.choices(string.digits, k=4))
            letters = ''.join(random.choices(string.ascii_uppercase, k=4))
            booking_reference = digits + letters
            
            # Check if the generated reference already exists
            if not Booking.objects.filter(booking_reference=booking_reference).exists():
                return booking_reference
class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    # Generic Foreign Key Magic 🔥
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Which model?
    object_id = models.PositiveIntegerField()  # ID of the object
    service_object = GenericForeignKey("content_type", "object_id")  # Final Magic Link

    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    guests = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    booking_reference = models.CharField(max_length=8, unique=False,default=generate_booking_reference)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
  

    def __str__(self):
        return f"Booking by {self.user.email} for {self.content_type}"

    def get_service_object(self):
        return self.service_object  #

 
    