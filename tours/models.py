from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

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
    main_image = models.ImageField(upload_to="tours/main_images/", blank=True, null=True)
    is_active = models.BooleanField(default=True,blank=True, null=True)  # Add this line
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)

    def __str__(self):
        return self.title

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
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to="tours/gallery/")

    def __str__(self):
        return f"Image for {self.tour_package.title}"


# tour_plan = TourPlanSerializer(many=True)