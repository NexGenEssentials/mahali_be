from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Country, Highlight, TourImage, TourPackage, TourPlan, WhenToGo
from .serializers import CountrySerializer, HighlightSerializer, TourImageSerializer, TourPackageSerializer, TourPlanSerializer, WhenToGoSerializer
from django.db import transaction
from rest_framework.views import APIView
from collections import defaultdict
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser


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

class TourPackageByCountryView(generics.ListAPIView):
    serializer_class = TourPackageSerializer

    def get_queryset(self):
        country_id = self.kwargs.get("country_id")
        return TourPackage.objects.filter(is_active=True, country_id=country_id).select_related("country")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return api_response(False, "No tour packages found for this country.", [], status.HTTP_404_NOT_FOUND)
        
        return api_response(True, "Tour packages retrieved successfully.", TourPackageSerializer(queryset, many=True).data)

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

class CreateHighlightView(generics.CreateAPIView):
    queryset = Highlight.objects.all()
    serializer_class = HighlightSerializer

class UpdateCountryImageView(generics.UpdateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    parser_classes = (MultiPartParser, FormParser)

    def patch(self, request, *args, **kwargs):
        country = self.get_object()
        if "image" not in request.FILES:
            return Response({"success": False, "message": "No image provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        country.image = request.FILES["image"]
        country.save()

        return Response({"success": True, "message": "Image updated successfully.", "data": CountrySerializer(country).data}, status=status.HTTP_200_OK)
    
class AssignHighlightToCountryView(APIView):
    def post(self, request, country_id):
        try:
            country = Country.objects.get(id=country_id)
            highlight_id = request.data.get("highlight_id")

            if not highlight_id:
                return Response({"success": False, "message": "Highlight ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                highlight = Highlight.objects.get(id=highlight_id)
            except Highlight.DoesNotExist:
                return Response({"success": False, "message": "Highlight not found."}, status=status.HTTP_404_NOT_FOUND)

            country.highlight = highlight
            country.save()

            return Response({"success": True, "message": "Highlight assigned successfully.", "data": CountrySerializer(country).data}, status=status.HTTP_200_OK)
        except Country.DoesNotExist:
            return Response({"success": False, "message": "Country not found."}, status=status.HTTP_404_NOT_FOUND)

class TourImageListCreateView(generics.ListCreateAPIView):
    """
    List all images of a car or upload new images.
    """
    serializer_class = TourImageSerializer
    # permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        package_id = self.kwargs.get("package_id")
        return TourImage.objects.filter(id=package_id)

    def create(self, request, *args, **kwargs):
        """Handle uploading multiple images at once."""
        package = get_object_or_404(TourPackage, id=self.kwargs.get("package_id"))
        
        images = request.FILES.getlist('image')  
        if not images:
            return Response({"error": "No images uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        image_objects = [TourImage(tour_package=package, image=image) for image in images]
        TourImage.objects.bulk_create(image_objects)

        return Response({"message": f"{len(images)} images uploaded successfully"}, status=status.HTTP_201_CREATED)

class WhenToGoListCreateView(generics.GenericAPIView):
    serializer_class = WhenToGoSerializer
    queryset = WhenToGo.objects.all()

    def get(self, request):
        items = self.get_queryset()
        serializer = self.get_serializer(items, many=True)
        return api_response(
            success=True,
            message="Seasons fetched successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_response(
                success=True,
                message="Season created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return api_response(
            success=False,
            message="Validation failed",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class WhenToGoDetailView(generics.GenericAPIView):
    serializer_class = WhenToGoSerializer
    queryset = WhenToGo.objects.all()

    def get_object(self, pk):
        try:
            return WhenToGo.objects.get(pk=pk)
        except WhenToGo.DoesNotExist:
            return None

    def get(self, request, pk):
        instance = self.get_object(pk)
        if not instance:
            return api_response(
                success=False,
                message="Season not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        return api_response(
            success=True,
            message="Season retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        instance = self.get_object(pk)
        if not instance:
            return api_response(
                success=False,
                message="Season not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_response(
                success=True,
                message="Season updated successfully",
                data=serializer.data
            )
        return api_response(
            success=False,
            message="Validation failed",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        instance = self.get_object(pk)
        if not instance:
            return api_response(
                success=False,
                message="Season not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        instance.delete()
        return api_response(
            success=True,
            message="Season deleted successfully"
        )