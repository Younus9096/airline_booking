import uuid
import random
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from bookings.models import Booking, BookingState, Seat, Flight
from bookings.services.state_machine import BookingStateMachine

class BookingService:
    
    @staticmethod
    def generate_booking_reference():
        return f"BK{uuid.uuid4().hex[:10].upper()}"
    
    @staticmethod
    @transaction.atomic
    def create_booking(flight_id, seat_number, passenger_name, passenger_email):
        try:
            flight = Flight.objects.select_for_update().get(id=flight_id)
        except Flight.DoesNotExist:
            raise ValueError("Flight not found")
        
        # Create booking
        booking = Booking.objects.create(
            booking_reference=BookingService.generate_booking_reference(),
            flight=flight,
            passenger_name=passenger_name,
            passenger_email=passenger_email,
            amount=flight.price,
            state=BookingState.INITIATED
        )
        
        return booking
    
    @staticmethod
    @transaction.atomic
    def hold_seat(booking_id, seat_number):
        booking = Booking.objects.select_for_update().get(id=booking_id)
        
        # Check if seat hold has expired
        if booking.is_seat_hold_expired():
            BookingStateMachine.transition(booking, BookingState.EXPIRED, "Seat hold expired")
            raise ValueError("Seat hold has expired")
        
        # Get and lock the seat
        try:
            seat = Seat.objects.select_for_update().get(
                flight=booking.flight,
                seat_number=seat_number,
                is_available=True
            )
        except Seat.DoesNotExist:
            raise ValueError("Seat not available or does not exist")
        
        # Mark seat as unavailable
        seat.is_available = False
        seat.save(update_fields=['is_available'])
        
        # Update booking
        booking.seat = seat
        booking.seat_hold_expires_at = timezone.now() + settings.SEAT_HOLD_DURATION
        booking.save(update_fields=['seat', 'seat_hold_expires_at', 'updated_at'])
        
        # Transition state
        BookingStateMachine.transition(
            booking,
            BookingState.SEAT_HELD,
            f"Seat {seat_number} held until {booking.seat_hold_expires_at}"
        )
        
        return booking
    
    @staticmethod
    @transaction.atomic
    def initiate_payment(booking_id):
        booking = Booking.objects.select_for_update().get(id=booking_id)
        
        # Check if seat hold has expired
        if booking.is_seat_hold_expired():
            BookingService._release_seat(booking)
            BookingStateMachine.transition(booking, BookingState.EXPIRED, "Seat hold expired")
            raise ValueError("Seat hold has expired")
        
        # Transition to payment pending
        BookingStateMachine.transition(
            booking,
            BookingState.PAYMENT_PENDING,
            "Payment initiated"
        )
        
        return booking
    
    @staticmethod
    @transaction.atomic
    def process_payment(booking_id, payment_method='card'):
        booking = Booking.objects.select_for_update().get(id=booking_id)
        
        # Check if seat hold has expired
        if booking.is_seat_hold_expired():
            BookingService._release_seat(booking)
            BookingStateMachine.transition(booking, BookingState.EXPIRED, "Seat hold expired")
            raise ValueError("Seat hold has expired")
        
        # Mock payment processing (80% success rate)
        payment_success = random.random() < 0.8
        payment_id = f"PAY{uuid.uuid4().hex[:12].upper()}"
        
        if payment_success:
            booking.payment_id = payment_id
            booking.save(update_fields=['payment_id', 'updated_at'])
            
            BookingStateMachine.transition(
                booking,
                BookingState.CONFIRMED,
                f"Payment successful: {payment_id}"
            )
            return booking, True
        else:
            # Payment failed - return to seat held state
            BookingStateMachine.transition(
                booking,
                BookingState.SEAT_HELD,
                f"Payment failed: {payment_id}"
            )
            return booking, False
    
    @staticmethod
    @transaction.atomic
    def cancel_booking(booking_id):
        booking = Booking.objects.select_for_update().get(id=booking_id)
        
        # Transition to cancelled
        BookingStateMachine.transition(
            booking,
            BookingState.CANCELLED,
            "Booking cancelled by user"
        )
        
        # Release seat
        BookingService._release_seat(booking)
        
        return booking
    
    @staticmethod
    @transaction.atomic
    def process_refund(booking_id):
        booking = Booking.objects.select_for_update().get(id=booking_id)
        
        # Check if already refunded
        if booking.refund_id:
            raise ValueError("Refund already processed")
        
        # Mock refund processing
        refund_id = f"REF{uuid.uuid4().hex[:12].upper()}"
        booking.refund_id = refund_id
        booking.save(update_fields=['refund_id', 'updated_at'])
        
        # Transition to refunded
        BookingStateMachine.transition(
            booking,
            BookingState.REFUNDED,
            f"Refund processed: {refund_id}"
        )
        
        return booking
    
    @staticmethod
    @transaction.atomic
    def expire_booking(booking_id):
        booking = Booking.objects.select_for_update().get(id=booking_id)
        
        # Release seat
        BookingService._release_seat(booking)
        
        # Transition to expired
        BookingStateMachine.transition(
            booking,
            BookingState.EXPIRED,
            "Seat hold expired automatically"
        )
        
        return booking
    
    @staticmethod
    def _release_seat(booking):
        if booking.seat:
            seat = Seat.objects.select_for_update().get(id=booking.seat.id)
            seat.is_available = True
            seat.save(update_fields=['is_available'])