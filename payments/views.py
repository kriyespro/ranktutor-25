from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
from datetime import timedelta
from .models import Payment, Invoice, Commission, Wallet, WalletTransaction
from bookings.models import Booking
import json


@login_required
def payment_history(request):
    """View payment history"""
    if request.user.is_tutor():
        payments = Payment.objects.filter(tutor=request.user).order_by('-created_at')
    elif request.user.is_student() or request.user.is_parent():
        payments = Payment.objects.filter(student=request.user).order_by('-created_at')
    else:
        payments = Payment.objects.none()
    
    context = {
        'payments': payments,
    }
    return render(request, 'payments/history.jinja', context)


@login_required
def payment_detail(request, payment_id):
    """Payment detail view"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Check access
    if payment.student != request.user and payment.tutor != request.user:
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    context = {
        'payment': payment,
    }
    return render(request, 'payments/detail.jinja', context)


@login_required
def generate_invoice(request, payment_id):
    """Generate invoice for a payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Check access
    if payment.student != request.user and payment.tutor != request.user:
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    # Create invoice if doesn't exist
    invoice, created = Invoice.objects.get_or_create(payment=payment)
    
    if created:
        # Generate invoice number
        invoice.invoice_number = f"INV-{payment.id:06d}-{timezone.now().strftime('%Y%m%d')}"
        invoice.save()
        messages.success(request, 'Invoice generated successfully!')
    else:
        messages.info(request, 'Invoice already exists.')
    
    return redirect('payments:detail', payment_id=payment_id)


@login_required
def tutor_earnings(request):
    """Tutor earnings dashboard"""
    if not request.user.is_tutor():
        messages.error(request, 'Access denied. Tutor access required.')
        return redirect('/')
    
    # Get earnings statistics
    total_earnings = Payment.objects.filter(
        tutor=request.user,
        status='completed'
    ).aggregate(total=Sum('tutor_payout'))['total'] or 0
    
    # Payments on hold (waiting for cooling period)
    payments_on_hold = Payment.objects.filter(
        tutor=request.user,
        status='on_hold'
    ).order_by('-created_at')
    
    on_hold_total = payments_on_hold.aggregate(total=Sum('tutor_payout'))['total'] or 0
    
    pending_earnings = Payment.objects.filter(
        tutor=request.user,
        status='processing'
    ).aggregate(total=Sum('tutor_payout'))['total'] or 0
    
    # Recent payments
    recent_payments = Payment.objects.filter(
        tutor=request.user
    ).order_by('-created_at')[:10]
    
    # Monthly earnings (last 6 months)
    from django.db.models.functions import TruncMonth
    monthly_earnings = Payment.objects.filter(
        tutor=request.user,
        status='completed'
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total=Sum('tutor_payout')
    ).order_by('-month')[:6]
    
    context = {
        'total_earnings': total_earnings,
        'pending_earnings': pending_earnings,
        'on_hold_total': on_hold_total,
        'payments_on_hold': payments_on_hold,
        'recent_payments': recent_payments,
        'monthly_earnings': monthly_earnings,
    }
    return render(request, 'payments/tutor_earnings.jinja', context)


@login_required
def process_payment(request, booking_id):
    """Process payment for an accepted or completed booking"""
    booking = get_object_or_404(Booking, id=booking_id, student=request.user)
    
    # Check if booking is accepted or completed (allow payment for both)
    if booking.status not in ['accepted', 'completed']:
        messages.error(request, 'Booking must be accepted or completed before payment.')
        return redirect('bookings:detail', booking_id=booking_id)
    
    # Check if payment already exists
    existing_payment = Payment.objects.filter(booking=booking).first()
    
    # If payment exists and is completed, redirect to detail
    if existing_payment and existing_payment.status == 'completed':
        messages.info(request, 'Payment already completed.')
        return redirect('payments:detail', payment_id=existing_payment.id)
    
    # Use existing payment if it exists (pending/processing), otherwise create new one
    if existing_payment:
        payment = existing_payment
    else:
        from .utils import create_payment_from_booking
        payment = create_payment_from_booking(booking)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'razorpay')
        transaction_id = request.POST.get('transaction_id', '')
        
        # In a real implementation, this would:
        # 1. Call payment gateway API (Stripe/Razorpay)
        # 2. Process the payment
        # 3. Get transaction ID from gateway
        # 4. Update payment status
        
        # For now, simulate payment processing
        if payment_method in ['stripe', 'razorpay']:
            # Simulate successful payment
            from .utils import process_payment as process_payment_util
            gateway_response = {
                'status': 'success',
                'transaction_id': transaction_id or f"TXN-{payment.id}-{timezone.now().timestamp()}",
                'gateway': payment_method,
            }
            process_payment_util(payment, gateway_response['transaction_id'], gateway_response)
            messages.success(request, 'Payment processed successfully!')
            return redirect('payments:detail', payment_id=payment.id)
        else:
            messages.error(request, 'Invalid payment method.')
    
    # Use booking amounts (already calculated)
    commission_percentage = getattr(settings, 'COMMISSION_PERCENTAGE', 15)
    context = {
        'booking': booking,
        'payment': payment,
        'amount': booking.total_amount,
        'commission_amount': booking.commission_amount,
        'tutor_payout': booking.total_amount - booking.commission_amount,
        'commission_percentage': commission_percentage,  # Pass commission percentage to template
    }
    return render(request, 'payments/process.jinja', context)


@login_required
def request_refund(request, payment_id):
    """Request refund for a payment"""
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)
    
    if payment.status != 'completed':
        messages.error(request, 'Only completed payments can be refunded.')
        return redirect('payments:detail', payment_id=payment_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        # In a real implementation, this would create a refund request
        # and notify admins
        messages.success(request, 'Refund request submitted. We will review it shortly.')
        return redirect('payments:detail', payment_id=payment_id)
    
    context = {
        'payment': payment,
    }
    return render(request, 'payments/request_refund.jinja', context)


@login_required
def wallet_view(request):
    """Student wallet view - show balance and recharge"""
    if not (request.user.is_student() or request.user.is_parent()):
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')[:20]
    
    context = {
        'wallet': wallet,
        'transactions': transactions,
    }
    return render(request, 'payments/wallet.jinja', context)


@login_required
@require_http_methods(["POST"])
def wallet_recharge(request):
    """Recharge wallet"""
    if not (request.user.is_student() or request.user.is_parent()):
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    # Get amount from POST data
    amount_str = request.POST.get('amount', '').strip()
    
    # Check if amount is provided
    if not amount_str:
        messages.error(request, 'Please enter an amount.')
        return redirect('payments:wallet')
    
    try:
        # Convert to Decimal for proper handling
        from decimal import Decimal
        amount = Decimal(str(amount_str))
        minimum_amount = Decimal('3000.00')
        
        # Validate amount
        if amount <= 0:
            messages.error(request, 'Amount must be greater than zero.')
            return redirect('payments:wallet')
        
        if amount < minimum_amount:
            messages.error(request, f'Minimum recharge amount is ₹{minimum_amount:.2f}.')
            return redirect('payments:wallet')
        
        # Get or create wallet
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        
        # In a real implementation, this would process payment through gateway
        # For now, simulate successful recharge
        wallet.add_balance(float(amount), transaction_type='recharge')
        
        messages.success(request, f'Wallet recharged with ₹{amount:.2f}. New balance: ₹{wallet.balance:.2f}')
        return redirect('payments:wallet')
    
    except ValueError:
        messages.error(request, f'Invalid amount format. Please enter a valid number (e.g., 3000, 5000, 11111).')
        return redirect('payments:wallet')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('payments:wallet')


@login_required
def release_payment(request, payment_id):
    """Release payment after cooling period (admin/tutor view)"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Check access - tutor can see their own payments
    if payment.tutor != request.user and not request.user.is_global_admin():
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    if payment.can_be_released():
        payment.status = 'completed'
        payment.released_at = timezone.now()
        payment.paid_at = timezone.now()  # Mark as paid when released
        payment.save()
        messages.success(request, 'Payment released successfully!')
    else:
        messages.error(request, 'Payment cannot be released yet. Cooling period not over.')
    
    return redirect('payments:tutor_earnings')
