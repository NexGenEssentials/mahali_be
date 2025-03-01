from django.urls import path
from .views import (
    BookingListCreateView,
    BookingDetailView,
    CancelBookingView,
    ConfirmBookingView,
    ServiceListView,
    UserBookingHistoryView,
    RescheduleBookingView,
)

urlpatterns = [
    path('bookings/', BookingListCreateView.as_view(), name='booking-list-create'),
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('bookings/<int:pk>/cancel/', CancelBookingView.as_view(), name='cancel-booking'),
    path('bookings/<int:pk>/confirm/', ConfirmBookingView.as_view(), name='confirm-booking'),
    path('bookings/history/', UserBookingHistoryView.as_view(), name='user-booking-history'),
    path('bookings/<int:pk>/reschedule/', RescheduleBookingView.as_view(), name='reschedule-booking'),
    path('services/', ServiceListView.as_view(), name='service-list')
]
