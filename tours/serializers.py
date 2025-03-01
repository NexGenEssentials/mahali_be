from rest_framework import serializers
from .models import Country, TourPackage, TourPlan, InclusionExclusion, Accommodation, TourImage
from django.db import transaction

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name"]

class TourPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourPlan
        fields = "__all__"

class TourImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourImage
        fields = ["id", "image"]

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

class TourPackageSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), source='country', write_only=True)
    tour_plans = TourPlanSerializer(many=True)

    class Meta:
        model = TourPackage
        fields = '__all__'
        extra_kwargs = {'country': {'read_only': True}}

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
