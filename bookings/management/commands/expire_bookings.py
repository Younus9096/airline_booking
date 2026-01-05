from django.core.management.base import BaseCommand
from django.utils import timezone
from bookings.models import Booking, BookingState
from bookings.services.booking_service import BookingService

class Command(BaseCommand):
    help = 'Expire bookings with expired seat holds'
    
    def handle(self, *args, **options):
        now = timezone.now()
        expired_bookings = Booking.objects.filter(
            state=BookingState.SEAT_HELD,
            seat_hold_expires_at__lt=now
        )
        
        count = 0
        for booking in expired_bookings:
            try:
                BookingService.expire_booking(booking.id)
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Expired booking {booking.booking_reference}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to expire booking {booking.booking_reference}: {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully expired {count} bookings')
        )