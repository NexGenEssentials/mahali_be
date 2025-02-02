from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Booking
from .serializers import BookingSerializer
class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
      
        return Booking.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Override the list method to provide a professional and structured response.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "message": "Bookings retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Override the create method to include professional response structure.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            
            serializer.save(user=request.user)
            return Response({
                "status": "success",
                "message": "Booking created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "message": "Invalid booking data",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user:
            raise PermissionError("You do not have permission to access this booking.")
        return obj

class CancelBookingView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        if booking.status == 'canceled':
            return Response({
                "status": "error",
                "message": "Booking is already canceled."
            }, status=status.HTTP_400_BAD_REQUEST)

        booking.status = 'canceled'
        booking.save()
        return Response({
            "status": "success",
            "message": "Booking canceled successfully",
            "data": BookingSerializer(booking).data
        }, status=status.HTTP_200_OK)
