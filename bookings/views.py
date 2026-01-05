from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bookings.models import Booking, Flight, Seat
from bookings.serializers import (
    BookingSerializer, CreateBookingSerializer, HoldSeatSerializer,
    ProcessPaymentSerializer, FlightSerializer, SeatSerializer
)
from bookings.services.booking_service import BookingService
from bookings.services.state_machine import InvalidStateTransitionError

class FlightListView(APIView):
    def get(self, request):
        flights = Flight.objects.all()
        serializer = FlightSerializer(flights, many=True)
        resp = {
            "results": serializer.data,
            "resultDescription": "Flight details.",
            "resultCode": "1"
        }
        return Response(resp, status=status.HTTP_200_OK)
       

class FlightDetailView(APIView):
    def get(self, request, flight_id):

        flight =Flight.objects.filter(id=flight_id).first()       
        if not flight:            
            resp = {                
                "errorMessage": "Flight details not found.",
                "resultCode": "0"
            }
            return Response(resp, status=status.HTTP_200_OK)


        serializer = FlightSerializer(flight)
        resp = {
            "results": serializer.data,
            "resultDescription": "Flight details descriptions.",
            "resultCode": "1"
        }
        return Response(resp, status=status.HTTP_200_OK)
       

class FlightSeatsView(APIView):
    def get(self, request, flight_id):
        flight =Flight.objects.filter(id=flight_id).first()       
        if not flight:            
            resp = {                
                "errorMessage": "Flight details not found.",
                "resultCode": "0"
            }
            return Response(resp, status=status.HTTP_200_OK)
        seats = Seat.objects.filter(flight=flight)
        serializer = SeatSerializer(seats, many=True)
        resp = {
                "results": serializer.data,
                "resultDescription": "Flight seats details.",
                "resultCode": "1"
            }
        return Response(resp, status=status.HTTP_200_OK)

class CreateBookingView(APIView):
    def post(self, request):
        data = request.data

        print(f"data: {data}",flush=True)
        
        serializer = CreateBookingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            booking = BookingService.create_booking(
                flight_id=serializer.validated_data['flight_id'],
                seat_number=serializer.validated_data['seat_number'],
                passenger_name=serializer.validated_data['passenger_name'],
                passenger_email=serializer.validated_data['passenger_email']
            )
            
            response_serializer = BookingSerializer(booking)
            # return Response(response_serializer.data, status=status.HTTP_201_CREATED)

            resp = {
                "results": serializer.data,
                "resultDescription": "Booking ceate successfully.",
                "resultCode": "1"
            }
            return Response(resp, status=status.HTTP_200_OK)
        
        
        except Exception as e:
            return Response(
                {'errorMessage': f'Failed to create booking due to {str(e)}',
                 "resultCode": "0"
                 },status=status.HTTP_200_OK
            )

class HoldSeatView(APIView):
    def post(self, request, booking_id):
        serializer = HoldSeatSerializer(data=request.data)
        if not serializer.is_valid():
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {'errorMessage': f'{serializer.errors}',
                 "resultCode": "0"
                 },status=status.HTTP_200_OK
            )
        
        try:
            booking = BookingService.hold_seat(
                booking_id=booking_id,
                seat_number=serializer.validated_data['seat_number']
            )
            
            response_serializer = BookingSerializer(booking)            
            resp = {
                "results": serializer.data,
                "resultDescription": "Booking ceate successfully.",
                "resultCode": "1"
            }
            return Response(resp, status=status.HTTP_200_OK)
        
        except Booking.DoesNotExist:            
            return Response(
                {'errorMessage': f'Booking not found',
                 "resultCode": "0"
                 },status=status.HTTP_200_OK
            )
        except (ValueError, InvalidStateTransitionError) as e:
            return Response(
                {'errorMessage': f'{str(e)}',
                 "resultCode": "0"
                 },status=status.HTTP_200_OK
            )
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'errorMessage': 'Failed to hold seat',"resultCode": "0"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class InitiatePaymentView(APIView):
    def post(self, request, booking_id):
        try:
            booking = BookingService.initiate_payment(booking_id=booking_id)
            serializer = BookingSerializer(booking)
            # return Response(serializer.data)
            resp = {
                "results": serializer.data,
                "resultDescription": "Booking ceate successfully.",
                "resultCode": "1"
            }
            return Response(resp, status=status.HTTP_200_OK)
        
        except Booking.DoesNotExist:
            return Response(
                {'errorMessage': 'Booking not found',"resultCode": "0"},
                status=status.HTTP_404_NOT_FOUND
            )
        except (ValueError, InvalidStateTransitionError) as e:
            return Response({'errorMessage': str(e),"resultCode": "0"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'errorMessage': 'Failed to initiate payment',"resultCode": "0"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProcessPaymentView(APIView):
    def post(self, request, booking_id):
        serializer = ProcessPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            booking, success = BookingService.process_payment(
                booking_id=booking_id,
                payment_method=serializer.validated_data.get('payment_method', 'card')
            )
            
            response_serializer = BookingSerializer(booking)
            response_data = response_serializer.data
            response_data['payment_success'] = success            
           
            resp = {
                "results": response_data,
                "resultDescription": "Booking ceate successfully.",
                "resultCode": "1"
            }
            return Response(resp, status=status.HTTP_200_OK)
        
        except Booking.DoesNotExist:
            return Response(
                {'errorMessage': 'Booking not found',"resultCode": "0"},
                status=status.HTTP_404_NOT_FOUND
            )
        except (ValueError, InvalidStateTransitionError) as e:
            return Response({'errorMessage': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'errorMessage': 'Failed to process payment',"resultCode": "0"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CancelBookingView(APIView):
    def post(self, request, booking_id):
        try:
            booking = BookingService.cancel_booking(booking_id=booking_id)
            serializer = BookingSerializer(booking)
            resp = {
                "results": serializer.data,
                "resultDescription": "Booking ceate successfully.",
                "resultCode": "1"
            }
            return Response(resp, status=status.HTTP_200_OK)
        
        except Booking.DoesNotExist:
            return Response(
                {'errorMessage': 'Booking not found',"resultCode": "0"},
                status=status.HTTP_404_NOT_FOUND
            )
        except InvalidStateTransitionError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'errorMessage': 'Failed to cancel booking',"resultCode": "0"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProcessRefundView(APIView):
    def post(self, request, booking_id):
        try:
            booking = BookingService.process_refund(booking_id=booking_id)
            serializer = BookingSerializer(booking)            
            resp = {
                "results": serializer.data,
                "resultDescription": "Booking ceate successfully.",
                "resultCode": "1"
            }
            return Response(resp, status=status.HTTP_200_OK)
            
        
        except Booking.DoesNotExist:
            return Response(
                {'errorMessage': 'Booking not found',"resultCode": "0"},
                status=status.HTTP_404_NOT_FOUND
            )
        except (ValueError, InvalidStateTransitionError) as e:
            return Response({'errorMessage': str(e),"resultCode": "0"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'errorMessage': 'Failed to process refund',"resultCode": "0"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class BookingDetailView(APIView):
    def get(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
        except:
            resp = {                
                "errorMessage": "Flight details descriptions.",
                "resultCode": "0"
            }           

        serializer = BookingSerializer(booking)
        resp = {
            "results": serializer.data,
            "resultDescription": "Flight booking details descriptions.",
            "resultCode": "1"
        }
        return Response(resp, status=status.HTTP_200_OK)

class BookingListView(APIView):
    def get(self, request):
        bookings = Booking.objects.all()
        serializer = BookingSerializer(bookings, many=True)
        
        resp = {
            "results": serializer.data,
            "resultDescription": "All Booking data.",
            "resultCode": "1"
        }
        return Response(resp, status=status.HTTP_200_OK)