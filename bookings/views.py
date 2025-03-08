from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Booking
from .serializers import BookingSerializer
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "message": "Bookings retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save(user=request.user)
    #         return Response({
    #             "status": "success",
    #             "message": "Booking created successfully",
    #             "data": serializer.data
    #         }, status=status.HTTP_201_CREATED)

    #     return Response({
    #         "status": "error",
    #         "message": "Invalid booking data",
    #         "errors": serializer.errors
    #     }, status=status.HTTP_400_BAD_REQUEST)
    def create_booking(self, request, *args, **kwargs):
        content_type_id = request.data.get("content_type")
        object_id = request.data.get("object_id")

        try:
            content_type = ContentType.objects.get(id=content_type_id)
            model_class = content_type.model_class()
            obj = model_class.objects.get(id=object_id)
        except ContentType.DoesNotExist:
            return Response({"error": "Invalid content type"}, status=status.HTTP_400_BAD_REQUEST)
        except model_class.DoesNotExist:
            return Response({"error": "Invalid object_id"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Valid object!"}, status=status.HTTP_200_OK)

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

def send_booking_confirmation_email(user,booking):
    message = Mail(
        from_email='mahaliafricaadvt@gmail.com',
        to_emails='ngabojck@gmail.com',
        subject='Mahali Africa Booking Confirmation',
        html_content = render_to_string('booking_confirmation_email.html', {'user': user, 'booking': booking}))
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
    # Render the HTML content
    # html_content = render_to_string('booking_confirmation_email.html', {'user': user, 'booking': booking})
    
    # Strip the HTML to create a plain-text version
    # text_content = strip_tags(html_content)

    # Send the email
    # send_mail(
    #     'Booking Confirmation',  # Subject
    #     text_content,  # Plain-text content
    #     settings.DEFAULT_FROM_EMAIL,  # From email
    #     [user.email],  # To email
    #     html_message=html_content  # HTML content
    # )
class ConfirmBookingView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
   
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        send_booking_confirmation_email(booking.user, booking)
        if booking.status == 'confirmed':
            return Response({
                "status": "error",
                "message": "Booking is already confirmed."
            }, status=status.HTTP_400_BAD_REQUEST)

        booking.status = 'confirmed'
        booking.save()
        # send_booking_confirmation_email()
        return Response({
            "status": "success",
            "message": "Booking confirmed successfully",
            "data": BookingSerializer(booking).data
        }, status=status.HTTP_200_OK)

class UserBookingHistoryView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "message": "User booking history retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class RescheduleBookingView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user, status='confirmed')

    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        new_date = request.data.get('date')

        if not new_date:
            return Response({"status": "error", "message": "New date is required"}, status=status.HTTP_400_BAD_REQUEST)

        booking.date = new_date
        booking.status = 'pending'
        booking.save()
        
        return Response({
            "status": "success",
            "message": "Booking rescheduled successfully",
            "data": BookingSerializer(booking).data
        }, status=status.HTTP_200_OK)

class ServiceListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        services = []
        content_types = ContentType.objects.filter(app_label__in=['car_rental', 'tours'])
        
        for ct in content_types:
            services.append({
                "id": ct.id,
                "app_label": ct.app_label,
                "model": ct.model,
                "name": f"{ct.app_label}.{ct.model}"
            })
        
        return Response({
            "status": "success",
            "message": "Available services retrieved successfully",
            "data": services
         }, status=status.HTTP_200_OK)