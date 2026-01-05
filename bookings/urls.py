from django.urls import path
from bookings.views import (
    FlightListView, FlightDetailView, FlightSeatsView,
    CreateBookingView, HoldSeatView, InitiatePaymentView,
    ProcessPaymentView, CancelBookingView, ProcessRefundView,
    BookingDetailView, BookingListView
)

urlpatterns = [
    # Flight endpoints
    path('flights/', FlightListView.as_view(), name='flight-list'),
    path('flights/<int:flight_id>/', FlightDetailView.as_view(), name='flight-detail'),
    path('flights/<int:flight_id>/seats/', FlightSeatsView.as_view(), name='flight-seats'),
    
    # Booking endpoints
    path('bookings/', BookingListView.as_view(), name='booking-list'),
    path('bookings/create/', CreateBookingView.as_view(), name='booking-create'),
    path('bookings/<int:booking_id>/', BookingDetailView.as_view(), name='booking-detail'),
    path('bookings/<int:booking_id>/hold-seat/', HoldSeatView.as_view(), name='booking-hold-seat'),
    path('bookings/<int:booking_id>/initiate-payment/', InitiatePaymentView.as_view(), name='booking-initiate-payment'),
    path('bookings/<int:booking_id>/process-payment/', ProcessPaymentView.as_view(), name='booking-process-payment'),
    path('bookings/<int:booking_id>/cancel/', CancelBookingView.as_view(), name='booking-cancel'),
    path('bookings/<int:booking_id>/refund/', ProcessRefundView.as_view(), name='booking-refund'),
]

