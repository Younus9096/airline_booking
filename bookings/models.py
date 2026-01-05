from django.db import models
from django.db import models
from django.utils import timezone
from django.conf import settings

class BookingState(models.TextChoices):
    INITIATED = 'INITIATED', 'Initiated'
    SEAT_HELD = 'SEAT_HELD', 'Seat Held'
    PAYMENT_PENDING = 'PAYMENT_PENDING', 'Payment Pending'
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    CANCELLED = 'CANCELLED', 'Cancelled'
    EXPIRED = 'EXPIRED', 'Expired'
    REFUNDED = 'REFUNDED', 'Refunded'

class Flight(models.Model):
    flight_number = models.CharField(max_length=10, unique=True)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    total_seats = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'flights'
    
    def __str__(self):
        return f"{self.flight_number} - {self.origin} to {self.destination}"

class Seat(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'seats'
        unique_together = ['flight', 'seat_number']
    
    def __str__(self):
        return f"{self.flight.flight_number} - Seat {self.seat_number}"

class Booking(models.Model):
    booking_reference = models.CharField(max_length=20, unique=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, null=True, blank=True)
    passenger_name = models.CharField(max_length=100)
    passenger_email = models.EmailField()
    state = models.CharField(
        max_length=20,
        choices=BookingState.choices,
        default=BookingState.INITIATED
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    seat_hold_expires_at = models.DateTimeField(null=True, blank=True)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    refund_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.booking_reference} - {self.state}"
    
    def is_seat_hold_expired(self):
        if self.seat_hold_expires_at and self.state == BookingState.SEAT_HELD:
            return timezone.now() > self.seat_hold_expires_at
        return False

class BookingStateTransition(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='transitions')
    from_state = models.CharField(max_length=20, choices=BookingState.choices)
    to_state = models.CharField(max_length=20, choices=BookingState.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'booking_state_transitions'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.booking.booking_reference}: {self.from_state} -> {self.to_state}"