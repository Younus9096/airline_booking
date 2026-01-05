from rest_framework import serializers
from bookings.models import Booking, Flight, Seat, BookingStateTransition

class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ['id', 'flight_number', 'origin', 'destination', 
                  'departure_time', 'total_seats', 'price', 'created_at']

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'is_available']

class BookingStateTransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingStateTransition
        fields = ['from_state', 'to_state', 'created_at', 'notes']

class BookingSerializer(serializers.ModelSerializer):
    flight_details = FlightSerializer(source='flight', read_only=True)
    seat_details = SeatSerializer(source='seat', read_only=True)
    transitions = BookingStateTransitionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'booking_reference', 'flight', 'seat', 'passenger_name',
            'passenger_email', 'state', 'amount', 'seat_hold_expires_at',
            'payment_id', 'refund_id', 'created_at', 'updated_at',
            'flight_details', 'seat_details', 'transitions'
        ]
        read_only_fields = [
            'id', 'booking_reference', 'state', 'seat_hold_expires_at',
            'payment_id', 'refund_id', 'created_at', 'updated_at'
        ]

class CreateBookingSerializer(serializers.Serializer):
    flight_id = serializers.IntegerField()
    seat_number = serializers.CharField(max_length=10)
    passenger_name = serializers.CharField(max_length=100)
    passenger_email = serializers.EmailField()

class HoldSeatSerializer(serializers.Serializer):
    seat_number = serializers.CharField(max_length=10)

class ProcessPaymentSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(
        choices=['card', 'upi', 'wallet'],
        default='card'
    )