from rest_framework.views import APIView
from rest_framework import generics, status,filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import Booking, Car, Payment
from .serializers import CarImageSerializer, CarSerializer, PaymentSerializer
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
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return []

class CarDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a car"""
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsAdminUser()]
        return []

class PaymentCreateView(generics.CreateAPIView):
    """Process a payment"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

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

        # Convert string dates to datetime.date
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        # Check for conflicting bookings
        conflicting_bookings = Booking.objects.filter( car_id=car_id, status='Confirmed' ).filter( Q(start_date__lte=end_date) & Q(end_date__gte=start_date) )

        if conflicting_bookings.exists():
            return Response({"available": False, "message": "Car is already booked for selected dates"})

        return Response({"available": True, "message": "Car is available for booking"})
class PopularCarsView(generics.ListAPIView):
    """List top rented cars"""
    serializer_class = CarSerializer

    def get_queryset(self):
        return Car.objects.annotate(num_bookings=Count('bookings')).order_by('-num_bookings')[:10]