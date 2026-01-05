from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from bookings.models import Flight, Seat

class Command(BaseCommand):
    help = 'Seed database with sample flights and seats'
    
    def handle(self, *args, **options):
        # Create sample flights
        flights_data = [
            {
                'flight_number': 'AI101',
                'origin': 'Delhi',
                'destination': 'Mumbai',
                'departure_time': timezone.now() + timedelta(days=7),
                'total_seats': 180,
                'price': 5500.00
            },
            {
                'flight_number': 'SG202',
                'origin': 'Bangalore',
                'destination': 'Goa',
                'departure_time': timezone.now() + timedelta(days=10),
                'total_seats': 150,
                'price': 4200.00
            },
            {
                'flight_number': 'UK303',
                'origin': 'Chennai',
                'destination': 'Kolkata',
                'departure_time': timezone.now() + timedelta(days=5),
                'total_seats': 120,
                'price': 6800.00
            },
        ]
        
        for flight_data in flights_data:
            flight, created = Flight.objects.get_or_create(
                flight_number=flight_data['flight_number'],
                defaults=flight_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created flight {flight.flight_number}')
                )
                
                # Create seats for this flight
                seat_rows = flight.total_seats // 6
                seat_letters = ['A', 'B', 'C', 'D', 'E', 'F']
                
                for row in range(1, seat_rows + 1):
                    for letter in seat_letters:
                        seat_number = f"{row}{letter}"
                        Seat.objects.create(
                            flight=flight,
                            seat_number=seat_number,
                            is_available=True
                        )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created {flight.total_seats} seats for {flight.flight_number}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Flight {flight.flight_number} already exists')
                )
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))