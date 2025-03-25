from django.db import models

from users.models import CustomUser, UserRoles

from django.conf import settings

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='country_images/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    

    def __str__(self):
        return self.name

class Highlight(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    icon = models.ImageField(upload_to='highlight_icons/', null=True, blank=True)
    country = models.ForeignKey(
        Country,
        related_name="highlights",
        on_delete=models.CASCADE,
        default=6 
    )
    def __str__(self):
        return self.title


class WhenToGo(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="when_to_go")
    season = models.CharField(max_length=100)  
    start_month = models.CharField(max_length=20)  
    end_month = models.CharField(max_length=20)  
    description = models.TextField(null=True, blank=True) 

    def __str__(self):
        return f"{self.season} ({self.start_month} - {self.end_month})"
class TourPackage(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="tour_packages")  # Change related_name
    best_time_to_visit = models.CharField(max_length=50)
    duration_days = models.PositiveIntegerField()
    duration_nights = models.PositiveIntegerField()
    min_people = models.PositiveIntegerField(default=1)
    max_people = models.PositiveIntegerField(default=20)
    rating = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True,blank=True, null=True)  # Add this line
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    owner = models.ForeignKey(
        CustomUser,
        null=True,  
        blank=True,
        on_delete=models.CASCADE,
        related_name="owned_packages",
        limit_choices_to={"role__in": [UserRoles.ADMIN, UserRoles.SERVICE_PROVIDER]},  
    )
    def get_related_packages(self):
        related = TourPackage.objects.filter(
            country=self.country,
            is_active=True
        ).exclude(id=self.id).filter(
            duration_days__gte=self.duration_days - 2,
            duration_days__lte=self.duration_days + 2,
            min_people__lte=self.max_people,
            max_people__gte=self.min_people
        )
        if related.count() < 3:
            fallback = TourPackage.objects.filter(
                country=self.country,
                is_active=True
            ).exclude(id=self.id)[:3 - related.count()]
            related = list(related) + list(fallback)
        
        return related[:3]  
    def __str__(self):
        return self.title

 

class TourPlan(models.Model):
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name="tour_plans")
    title = models.CharField(max_length=255)
    description = models.TextField()
    inclusion=models.TextField(null=True)
    accommodation=models.CharField(max_length=255,null=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)

    def __str__(self):
        return f"Day {self.day_number}: {self.title}"

class InclusionExclusion(models.Model):
    INCLUSION = "INCLUSION"
    EXCLUSION = "EXCLUSION"
    TYPE_CHOICES = [(INCLUSION, "Inclusion"), (EXCLUSION, "Exclusion")]

    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name="inclusions_exclusions")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    detail = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.type}: {self.detail}"

class Accommodation(models.Model):
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name="accommodations")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class TourImage(models.Model):
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="tours_images/")

    def __str__(self):
        return f"Image for {self.tour_package.title}"

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Activity(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True,default="kigali")
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='activities')

    def __str__(self):
        return f"{self.name} (${self.price_per_day}/day)"


class CustomPackage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='custom_packages')
    name = models.CharField(max_length=255)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ${self.total_price}"
class CustomPackageActivity(models.Model):
    custom_package = models.ForeignKey(CustomPackage, on_delete=models.CASCADE, related_name='package_activities')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    number_of_days = models.PositiveIntegerField()
    sub_total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        # Auto calculate subtotal
        self.sub_total_price = self.activity.price_per_day * self.number_of_days
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.activity.name} - {self.number_of_days} day(s)"
    






# tour_plan = TourPlanSerializer(many=True)