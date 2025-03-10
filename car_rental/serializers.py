from rest_framework import serializers
from users.models import CustomUser, UserRoles
from .models import  Car, CarImage, Feature
from django.conf import settings

class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['image']


class RelatedCarSerializer(serializers.ModelSerializer):
    """A smaller serializer to prevent infinite recursion."""
    first_image = serializers.SerializerMethodField()
    class Meta:
        model = Car
        fields = ['id', 'name', 'category', 'transmission', 'price_per_day', 'year', 'first_image']
    def get_first_image(self, obj):
        """Return full URL of the first image for related cars."""
        first_image = obj.images.first()
        if first_image:
            return f"{settings.BASE_URL}{first_image.image.url}"
        return None


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ["id", "name"]


class CarSerializer(serializers.ModelSerializer):
    features = FeatureSerializer(many=True, read_only=True)
    feature_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    first_image = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()  
    related_cars = serializers.SerializerMethodField()
    owner = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role__in=[UserRoles.ADMIN, UserRoles.SERVICE_PROVIDER])
    )

    class Meta:
        model = Car
        fields = '__all__'

    def get_first_image(self, obj):
        """Return full URL of the first image."""
        first_image = obj.images.first()
        if first_image:
            return f"{settings.BASE_URL}{first_image.image.url}"
        return None

    def get_images(self, obj):
        """Return full URLs of all images only for a single car detail view."""
        request = self.context.get("request")
        
        # Check if this is a detail view (contains car ID in URL)
        if request and request.parser_context:
            if "pk" in request.parser_context["kwargs"]:  
                return [f"{settings.BASE_URL}{image.image.url}" for image in obj.images.all()]
    
        return []  # Return empty list for list view

    def get_related_cars(self, obj):
        related_cars = obj.get_related_cars()
        return RelatedCarSerializer(related_cars, many=True).data

    def update(self, instance, validated_data):
        feature_ids = validated_data.pop("feature_ids", [])
        instance = super().update(instance, validated_data)

        if feature_ids:
            
            existing_features = set(instance.features.values_list('id', flat=True))
            new_features = set(feature_ids)

            instance.features.filter(id__in=existing_features - new_features).delete()

           
            Feature.objects.bulk_create(
                [Feature(car=instance, feature_id=feat_id) for feat_id in new_features - existing_features]
            )

        return instance



