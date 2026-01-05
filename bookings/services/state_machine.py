from django.db import transaction
from bookings.models import Booking, BookingState, BookingStateTransition

class InvalidStateTransitionError(Exception):
    pass

class BookingStateMachine:
    VALID_TRANSITIONS = {
        BookingState.INITIATED: [BookingState.SEAT_HELD],
        BookingState.SEAT_HELD: [BookingState.PAYMENT_PENDING, BookingState.EXPIRED],
        BookingState.PAYMENT_PENDING: [BookingState.CONFIRMED, BookingState.SEAT_HELD],
        BookingState.CONFIRMED: [BookingState.CANCELLED],
        BookingState.CANCELLED: [BookingState.REFUNDED],
        BookingState.EXPIRED: [],
        BookingState.REFUNDED: [],
    }
    
    @classmethod
    def can_transition(cls, from_state, to_state):
        return to_state in cls.VALID_TRANSITIONS.get(from_state, [])
    
    @classmethod
    @transaction.atomic
    def transition(cls, booking, to_state, notes=''):
        from_state = booking.state
        
        if not cls.can_transition(from_state, to_state):
            raise InvalidStateTransitionError(
                f"Invalid transition from {from_state} to {to_state}"
            )
        
        # Update booking state
        booking.state = to_state
        booking.save(update_fields=['state', 'updated_at'])
        
        # Record transition
        BookingStateTransition.objects.create(
            booking=booking,
            from_state=from_state,
            to_state=to_state,
            notes=notes
        )
        
        return booking