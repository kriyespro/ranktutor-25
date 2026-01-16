from django.conf import settings
from django.utils import timezone
from .models import Payment, Invoice, Commission
from bookings.models import Booking
import uuid


def create_payment_from_booking(booking):
    """Create payment record from booking"""
    payment = Payment.objects.create(
        booking=booking,
        student=booking.student,
        tutor=booking.tutor,
        amount=booking.total_amount,
        commission_amount=booking.commission_amount,
        tutor_payout=booking.total_amount - booking.commission_amount,
        status='pending',
    )
    
    # Create commission record
    Commission.objects.create(
        payment=payment,
        amount=booking.commission_amount,
        percentage=settings.COMMISSION_PERCENTAGE,
    )
    
    return payment


def generate_invoice_number():
    """Generate unique invoice number"""
    return f"INV-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"


def process_payment(payment, transaction_id, gateway_response):
    """Process payment after gateway confirmation"""
    payment.status = 'completed'
    payment.transaction_id = transaction_id
    payment.payment_gateway_response = gateway_response
    payment.paid_at = timezone.now()
    payment.save()
    
    # Generate invoice
    invoice, created = Invoice.objects.get_or_create(payment=payment)
    if created:
        invoice.invoice_number = generate_invoice_number()
        invoice.save()
    
    return payment


def calculate_commission(amount):
    """Calculate commission amount"""
    commission_rate = getattr(settings, 'COMMISSION_PERCENTAGE', 15) / 100
    return amount * commission_rate

