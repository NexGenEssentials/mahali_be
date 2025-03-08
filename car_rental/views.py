from rest_framework.views import APIView
from rest_framework import generics, status,filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import  Car, Feature,CarImage
from .serializers import CarImageSerializer, CarSerializer, FeatureSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from datetime import datetime
from django.db.models import Count






class CarListCreateView(generics.ListCreateAPIView):
    """List all cars or create a new car (Admin only)"""
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]


    filterset_fields = ['brand', 'fuel_type', 'transmission', 'seats', 'is_available']
    search_fields = ['name', 'brand']
    ordering_fields = ['price_per_day', 'year', 'mileage']
    
  
    
    def get_queryset(self):
        """Allow dynamic filtering based on query params"""
        queryset = super().get_queryset()
        query_params = self.request.query_params

        # Example: Custom filtering logic (optional)
        min_price = query_params.get("min_price")
        max_price = query_params.get("max_price")
        if min_price and max_price:
            queryset = queryset.filter(price_per_day__gte=min_price, price_per_day__lte=max_price)

        return queryset

    def list(self, request, *args, **kwargs):
        """Custom response for GET requests"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "message": "Cars retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)



    def create(self, request, *args, **kwargs):
        """Custom response for POST requests (Admin & Service Provider Only)"""
        
    
        if not request.user.is_authenticated:
            return Response({
                "status": "error",
                "message": "Authentication required."
            }, status=status.HTTP_401_UNAUTHORIZED)

        
        if request.user.role not in ["admin", "service_provider"]:
            return Response({
                "status": "error",
                "message": "Permission denied. Only Admins and Service Providers can add cars."
            }, status=status.HTTP_403_FORBIDDEN)

       
        request.data["owner"] = request.user.id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "status": "success",
            "message": "Car created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class CarDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a car"""
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsAdminUser()]
        return []



    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "status": "success",
                "message": "Payment processed successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": "Invalid payment data",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
class CarImageUploadView(generics.CreateAPIView):
    """Upload an image for a car"""
    serializer_class = CarImageSerializer
    parser_classes = (MultiPartParser, FormParser)

class CheckAvailabilityView(APIView):
    """Check car availability for a given date range"""

    def get(self, request):
        car_id = request.query_params.get('car_id')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if not all([car_id, start_date_str, end_date_str]):
            return Response({"error": "Missing parameters"}, status=400)

     
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        conflicting_bookings = Booking.objects.filter( car_id=car_id, status='Confirmed' ).filter( Q(start_date__lte=end_date) & Q(end_date__gte=start_date) )

        if conflicting_bookings.exists():
            return Response({"available": False, "message": "Car is already booked for selected dates"})

        return Response({"available": True, "message": "Car is available for booking"})
class PopularCarsView(generics.ListAPIView):
    """List top rented cars"""
    serializer_class = CarSerializer

    def get_queryset(self):
        return Car.objects.annotate(num_bookings=Count('bookings')).order_by('-num_bookings')[:10]
    
class AddFeatureToCarView(APIView):
    def post(self, request, car_id):
        try:
            car = Car.objects.get(id=car_id)
        except Car.DoesNotExist:
            return Response({"error": "Car not found"}, status=status.HTTP_404_NOT_FOUND)

        feature_ids = request.data.get("feature_ids", [])
        features = Feature.objects.filter(id__in=feature_ids)

        if not features.exists():
            return Response({"error": "No valid features provided"}, status=status.HTTP_400_BAD_REQUEST)

        car.features.add(*features)
        return Response({"message": "Features added successfully"}, status=status.HTTP_200_OK)
    
class FeatureCreateListView(generics.ListCreateAPIView):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer




class CarImageListCreateView(generics.ListCreateAPIView):
    """
    List all images of a car or upload new images.
    """
    serializer_class = CarImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        car_id = self.kwargs.get("car_id")
        return CarImage.objects.filter(car_id=car_id)

    def create(self, request, *args, **kwargs):
        """Handle uploading multiple images at once."""
        car = get_object_or_404(Car, id=self.kwargs.get("car_id"))
        
        images = request.FILES.getlist('image')  
        if not images:
            return Response({"error": "No images uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        image_objects = [CarImage(car=car, image=image) for image in images]
        CarImage.objects.bulk_create(image_objects)

        return Response({"message": f"{len(images)} images uploaded successfully"}, status=status.HTTP_201_CREATED)


class CarImageRetrieveDeleteView(generics.RetrieveDestroyAPIView):
    """
    Retrieve a single car image or delete it.
    """
    serializer_class = CarImageSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(CarImage, id=self.kwargs.get("image_id"), car_id=self.kwargs.get("car_id"))
