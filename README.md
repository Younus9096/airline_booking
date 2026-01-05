# Airline Ticket Booking System
A Django REST Framework backend for managing airline seat bookings with state machine logic, seat locking, payment processing, and automatic expiration.

## Features
- State machine-based booking flow with validation
- Atomic seat locking with database transactions
- 10-minute temporary seat hold
- Mocked payment processing (80% success rate)
- Booking cancellation and refund processing
- Automatic seat hold expiration
- RESTful API using APIView
- Docker containerization

## State Machine Flow
INITIATED → SEAT_HELD → PAYMENT_PENDING → CONFIRMED
                ↓                              ↓
            EXPIRED                       CANCELLED → REFUNDED


## Installation & Setup

### Prerequisites

- Docker
- Docker Compose

### Quick Start

1. **Clone the repository**

git clone <repository-url>
cd airline-booking


2. **Build and run with Docker Compose**
docker-compose up --build


3. **Run migrations** (in a new terminal)

docker exec -it <container_id> bash
python manage.py makemigrations
python manage.py migrate

4. **Create superuser** (optional)
python manage.py createsuperuser


6. **Access the application**

- API: http://localhost/api/
- Admin: http://localhost/admin/

## API Endpoints

### Flight Endpoints

GET    /api/flights/                    # List all flights
GET    /api/flights/{flight_id}/        # Get flight details
GET    /api/flights/{flight_id}/seats/  # Get available seats

### Booking Endpoints

GET    /api/bookings/                        # List all bookings
GET    /api/bookings/{booking_id}/           # Get booking details
POST   /api/bookings/create/                 # Create new booking
POST   /api/bookings/{booking_id}/hold-seat/ # Hold a seat
POST   /api/bookings/{booking_id}/initiate-payment/  # Initiate payment
POST   /api/bookings/{booking_id}/process-payment/   # Process payment
POST   /api/bookings/{booking_id}/cancel/    # Cancel booking
POST   /api/bookings/{booking_id}/refund/    # Process refund


## API Usage Examples

### 1. Create a Booking

curl -X POST http://localhost/api/bookings/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "flight_id": 1,
    "seat_number": "1A",
    "passenger_name": "Mohd Younus",
    "passenger_email": "Younus@example.com"
  }'


### 2. Hold a Seat

curl -X POST http://localhost/api/bookings/1/hold-seat/ \
  -H "Content-Type: application/json" \
  -d '{
    "seat_number": "1A"
  }'


### 3. Initiate Payment

curl -X POST http://localhost/api/bookings/1/initiate-payment/ \
  -H "Content-Type: application/json"

### 4. Process Payment

curl -X POST http://localhost/api/bookings/1/process-payment/ \
  -H "Content-Type: application/json" \
  -d '{
    "payment_method": "card"
  }'


### 5. Cancel Booking

curl -X POST http://localhost/api/bookings/1/cancel/ \
  -H "Content-Type: application/json"


### 6. Process Refund

curl -X POST http://localhost/api/bookings/1/refund/ \
  -H "Content-Type: application/json"


## Automatic Seat Hold Expiration

To automatically expire seat holds after 10 minutes, run the management command:

docker exec -it <container_id> bash
python manage.py expire_bookings


## Database Models

### Flight
- flight_number, origin, destination, departure_time
- total_seats, price

### Seat
- flight (FK), seat_number, is_available

### Booking
- booking_reference, flight (FK), seat (FK)
- passenger_name, passenger_email
- state, amount, seat_hold_expires_at
- payment_id, refund_id

### BookingStateTransition
- booking (FK), from_state, to_state
- created_at, notes


## Testing

The system includes:
- Atomic database transactions for seat locking
- State machine validation
- Automatic seat release on cancellation/expiration
- Mocked payment with 80% success rate
- Refund idempotency (prevents double refunds)
