from django.contrib import admin
from bookings.models import Flight, Seat, Booking, BookingStateTransition

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['flight_number', 'origin', 'destination', 'departure_time', 'total_seats', 'price']
    search_fields = ['flight_number', 'origin', 'destination']
    list_filter = ['departure_time']

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['flight', 'seat_number', 'is_available']
    list_filter = ['is_available', 'flight']
    search_fields = ['seat_number', 'flight__flight_number']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'passenger_name', 'flight', 'seat', 'state', 'amount', 'created_at']
    list_filter = ['state', 'created_at']
    search_fields = ['booking_reference', 'passenger_name', 'passenger_email']
    readonly_fields = ['booking_reference', 'created_at', 'updated_at']

@admin.register(BookingStateTransition)
class BookingStateTransitionAdmin(admin.ModelAdmin):
    list_display = ['booking', 'from_state', 'to_state', 'created_at']
    list_filter = ['from_state', 'to_state', 'created_at']
    search_fields = ['booking__booking_reference']