from rest_framework import serializers
from .models import Country, Highlight, TourPackage, TourPlan, InclusionExclusion, Accommodation, TourImage, WhenToGo
from django.db import transaction
from django.conf import settings
from users.models import CustomUser, UserRoles


class HighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Highlight
        fields = "__all__"
class WhenToGoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhenToGo
        fields = '__all__'
class CountrySerializer(serializers.ModelSerializer):
    highlights = HighlightSerializer(many=True, read_only=True)
    when_to_go = WhenToGoSerializer(many=True, read_only=True)
    class Meta:
        model = Country
        fields = "__all__"



class TourPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourPlan
        fields = "__all__"

class TourImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourImage
        fields = ["image"]

class InclusionExclusionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InclusionExclusion
        fields = ["detail"]

class AccommodationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation
        fields = ["name", "description"]

class TourPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourPlan
        fields = ["title", "description", "inclusion", "accommodation","inclusion","accommodation"]




class RelatedPackageSerializer(serializers.ModelSerializer):
    """A smaller serializer to prevent infinite recursion."""
    main_image = serializers.SerializerMethodField()
    class Meta:
        model = TourPackage
        fields = ['id', 'title', 'min_people', 'max_people', 'country', 'duration_days', 'rating','main_image']
    def get_main_image(self, obj):
        """Return full URL of the first image for related tours."""
        main_image = obj.images.first()
        if main_image:
            return f"{settings.BASE_URL}{main_image.image.url}"
        return None
    


class TourPackageSerializer(serializers.ModelSerializer):
    # country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), source='country', write_only=True)
    tour_plans = TourPlanSerializer(many=True)
    main_image = serializers.SerializerMethodField()
    related_packages = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField() 
    owner = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role__in=[UserRoles.ADMIN, UserRoles.SERVICE_PROVIDER])
    )

    class Meta:
        model = TourPackage
        fields = '__all__'
        extra_kwargs = {'country': {'read_only': True}}

    
    def get_main_image(self, obj):
        """Return full URL of the first image."""
        main_image = obj.images.first()
        if main_image:
            return f"{settings.BASE_URL}{main_image.image.url}"
        return None
    

    def get_images(self, obj):
        """Return full URLs of all images only for a single packages detail view."""
        request = self.context.get("request")
        
        # Check if this is a detail view (contains car ID in URL)
        if request and request.parser_context:
            if "pk" in request.parser_context["kwargs"]:  
                return [f"{settings.BASE_URL}{image.image.url}" for image in obj.images.all()]
    
        return [] 
    

    def get_related_packages(self, obj):
        related_packages = obj.get_related_packages()
        return RelatedPackageSerializer(related_packages, many=True).data


    def get_tour_plans(self, obj):
        request = self.context.get('request')
        if request and request.parser_context['kwargs'].get('pk'):
            return TourPlanSerializer(obj.tour_plans.all(), many=True).data
        return None

    def create(self, validated_data):
        tour_plans_data = validated_data.pop("tour_plans")
        country = validated_data.pop("country")  # Retrieve country object
        validated_data["country"] = country  # Assign country object to validated data

        tour_package = TourPackage.objects.create(**validated_data)

        for plan_data in tour_plans_data:
            TourPlan.objects.create(tour_package=tour_package, **plan_data)

        return tour_package

    def update(self, instance, validated_data):
        tour_plans_data = self.context['request'].data.get('tour_plans', [])
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if tour_plans_data:
                instance.tour_plans.all().delete()
                for tour_plan_data in tour_plans_data:
                    TourPlan.objects.create(tour_package=instance, day_number=tour_plan_data.get("day_number"), **tour_plan_data)
        return instance
    def to_representation(self, instance):
        data = super().to_representation(instance)
        tour_plans = data.pop("tour_plans", [])
        data["tour_plans"] = tour_plans
        return data


