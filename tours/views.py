from rest_framework import generics, status
from rest_framework.response import Response
from .models import Country, TourPackage, TourPlan
from .serializers import CountrySerializer, TourPackageSerializer, TourPlanSerializer
from django.db import transaction
from rest_framework.views import APIView
from collections import defaultdict




def api_response(success, message, data=None, status_code=status.HTTP_200_OK):
    return Response({
        "success": success,
        "message": message,
        "data": data
    }, status=status_code)

class TourPackageListCreateView(generics.ListCreateAPIView):
    queryset = TourPackage.objects.filter(is_active=True).select_related("country")
    serializer_class = TourPackageSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        grouped_data = defaultdict(list)

        # Grouping tour packages by country
        for tour in queryset:
            country_name = tour.country.name if tour.country else "Unknown"
            grouped_data[country_name].append(TourPackageSerializer(tour).data)

        return api_response(True, "Tour packages retrieved successfully.", dict(grouped_data))
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_response(True, "Tour package created successfully.", serializer.data, status.HTTP_201_CREATED)
        return api_response(False, "Invalid data.", serializer.errors, status.HTTP_400_BAD_REQUEST)

class TourPackageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TourPackage.objects.all()
    serializer_class = TourPackageSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(True, "Tour package retrieved successfully.", serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        tour_plans_data = request.data.get("tour_plans", [])
        with transaction.atomic():
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                if tour_plans_data:
                    instance.tour_plans.all().delete()  # Remove old plans
                    for plan_data in tour_plans_data:
                        TourPlan.objects.create(tour_package=instance, **plan_data)
                return api_response(True, "Tour package updated successfully.", serializer.data)
            return api_response(False, "Invalid data.", serializer.errors, status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return api_response(True, "Tour package deleted successfully.")

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        action = request.data.get("action")
        if action == "activate":
            instance.is_active = True
        elif action == "deactivate":
            instance.is_active = False
        else:
            return api_response(False, "Invalid action.")
        instance.save()
        serializer = self.get_serializer(instance)
        return api_response(True, f"Tour package {'activated' if instance.is_active else 'deactivated'} successfully.", serializer.data)

class CountryListCreateView(generics.ListCreateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(True, "Countries retrieved successfully.", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_response(True, "Country created successfully.", serializer.data, status.HTTP_201_CREATED)
        return api_response(False, "Invalid data.", serializer.errors, status.HTTP_400_BAD_REQUEST)


class TourPlanListCreateView(generics.ListCreateAPIView):
    serializer_class = TourPlanSerializer

    def get_queryset(self):
        package_id = self.kwargs["package_id"]
        return TourPlan.objects.filter(tour_package_id=package_id)

class TourPlanDetailView(APIView):
    def get(self, request, pk):
        try:
            tour_plan = TourPlan.objects.get(pk=pk)
            serializer = TourPlanSerializer(tour_plan)
            return Response(serializer.data)
        except TourPlan.DoesNotExist:
            return Response({"message": "Tour Plan not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            tour_plan = TourPlan.objects.get(pk=pk)
            serializer = TourPlanSerializer(tour_plan, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except TourPlan.DoesNotExist:
            return Response({"message": "Tour Plan not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            tour_plan = TourPlan.objects.get(pk=pk)
            tour_plan.delete()
            return Response({"message": "Tour Plan deleted successfully"})
        except TourPlan.DoesNotExist:
            return Response({"message": "Tour Plan not found"}, status=status.HTTP_404_NOT_FOUND)
