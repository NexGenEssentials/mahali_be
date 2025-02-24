from rest_framework import serializers
from users.models import CustomUser, UserRoles
from .models import Booking, Car, CarImage, Feature


class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['image']


class RelatedCarSerializer(serializers.ModelSerializer):
    """A smaller serializer to prevent infinite recursion."""
    class Meta:
        model = Car
        fields = ['id', 'name', 'category', 'transmission']


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
        """Return only the first image URL."""
        first_image = obj.images.first()
        return first_image.image.url if first_image else None

    def get_images(self, obj):
        request = self.context.get("request")
        view = request.parser_context.get('view') if request else None

        if view and hasattr(view, "action") and view.action == "retrieve":
            return [image.image.url for image in obj.images.all()]
        return [] 

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


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
