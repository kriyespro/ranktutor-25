from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Booking, Lesson, AvailabilitySlot, CalendarSync
from tutors.models import TutorProfile, PricingOption
from payments.utils import create_payment_from_booking
from payments.models import Payment, Wallet


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def _parse_time(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%H:%M').time()
    except (ValueError, TypeError):
        return None


def _parse_decimal(value, default=0):
    if value in (None, ''):
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


@login_required
def create_booking(request, tutor_id):
    """Create a booking request"""
    tutor_profile = get_object_or_404(TutorProfile, id=tutor_id)
    
    if request.method == 'POST':
        lesson_date = _parse_date(request.POST.get('lesson_date'))
        lesson_time = _parse_time(request.POST.get('lesson_time'))
        duration_hours = _parse_decimal(request.POST.get('duration_hours'), 1.0)
        price_per_hour = _parse_decimal(request.POST.get('price_per_hour'), 0)
        
        booking = Booking.objects.create(
            student=request.user,
            tutor=tutor_profile.user,
            subject_id=request.POST.get('subject'),
            lesson_date=lesson_date,
            lesson_time=lesson_time,
            duration_hours=duration_hours,
            mode=request.POST.get('mode', 'online'),
            price_per_hour=price_per_hour,
            student_notes=request.POST.get('notes', ''),
            is_trial=request.POST.get('is_trial') == 'on',
            is_recurring=request.POST.get('is_recurring') == 'on',
            recurrence_pattern=request.POST.get('recurrence_pattern', ''),
            recurrence_end_date=_parse_date(request.POST.get('recurrence_end_date')),
        )
        
        # Create recurring bookings if needed
        if booking.is_recurring and booking.recurrence_pattern:
            create_recurring_bookings(booking)
        
        messages.success(request, 'Booking request sent! The tutor will review it.')
        return redirect('bookings:detail', booking_id=booking.id)
    
    # Get pricing options
    pricing_options = PricingOption.objects.filter(tutor=tutor_profile, is_active=True)
    
    # Fallback: If no pricing options, use tutor's subjects with default pricing
    if not pricing_options.exists():
        # Get tutor's subjects and create temporary pricing options for display
        tutor_subjects = tutor_profile.subjects.all()
        # We'll handle this in the template by showing subjects directly
        pricing_options = None
    
    context = {
        'tutor_profile': tutor_profile,
        'pricing_options': pricing_options,
        'tutor_subjects': tutor_profile.subjects.all() if not pricing_options else None,
        'default_hourly_rate': tutor_profile.hourly_rate or 500,  # Default rate if not set
        'today': timezone.now().date(),
    }
    return render(request, 'bookings/create.jinja', context)


def create_recurring_bookings(parent_booking):
    """Create recurring bookings based on pattern"""
    if not parent_booking.is_recurring or not parent_booking.recurrence_pattern:
        return
    
    current_dt = datetime.combine(parent_booking.lesson_date, parent_booking.lesson_time)
    end_date = parent_booking.recurrence_end_date or (parent_booking.lesson_date + timedelta(days=90))
    
    delta_days = {
        'daily': 1,
        'weekly': 7,
        'biweekly': 14,
        'monthly': 30,
    }.get(parent_booking.recurrence_pattern, 7)
    
    while current_dt.date() <= end_date:
        current_dt += timedelta(days=delta_days)
        if current_dt.date() > end_date:
            break
        
        Booking.objects.create(
            student=parent_booking.student,
            tutor=parent_booking.tutor,
            subject=parent_booking.subject,
            lesson_date=current_dt.date(),
            lesson_time=current_dt.time(),
            duration_hours=parent_booking.duration_hours,
            mode=parent_booking.mode,
            price_per_hour=parent_booking.price_per_hour,
            is_recurring=True,
            parent_booking=parent_booking,
            status='pending',
        )


@login_required
def booking_detail(request, booking_id):
    """Booking detail view"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check access
    if booking.student != request.user and booking.tutor != request.user:
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    # Get lesson if exists
    lesson = None
    try:
        lesson = booking.lesson
    except Lesson.DoesNotExist:
        pass
    
    # Get recurring bookings if this is a parent booking
    recurring_bookings = []
    if booking.is_recurring and not booking.parent_booking:
        recurring_bookings = Booking.objects.filter(parent_booking=booking).order_by('lesson_date')
    
    context = {
        'booking': booking,
        'lesson': lesson,
        'recurring_bookings': recurring_bookings,
    }
    return render(request, 'bookings/detail.jinja', context)


@login_required
def accept_booking(request, booking_id):
    """Tutor accepts a booking"""
    booking = get_object_or_404(Booking, id=booking_id, tutor=request.user)
    
    if booking.status != 'pending':
        messages.error(request, 'This booking cannot be accepted.')
        return redirect('bookings:detail', booking_id=booking_id)
    
    booking.status = 'accepted'
    booking.accepted_at = timezone.now()
    booking.save()
    
    # Accept all recurring bookings if this is a parent booking
    if booking.is_recurring and not booking.parent_booking:
        Booking.objects.filter(parent_booking=booking, status='pending').update(
            status='accepted',
            accepted_at=timezone.now()
        )
    
    # Create payment record (pending until payment is made)
    create_payment_from_booking(booking)
    
    messages.success(request, 'Booking accepted!')
    return redirect('tutors:dashboard')


@login_required
def reject_booking(request, booking_id):
    """Tutor rejects a booking"""
    booking = get_object_or_404(Booking, id=booking_id, tutor=request.user)
    
    if booking.status != 'pending':
        messages.error(request, 'This booking cannot be rejected.')
        return redirect('bookings:detail', booking_id=booking_id)
    
    booking.status = 'rejected'
    booking.save()
    
    messages.success(request, 'Booking rejected.')
    return redirect('tutors:dashboard')


@login_required
def complete_lesson(request, booking_id):
    """Mark lesson as completed and create lesson record"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check access
    if booking.tutor != request.user and booking.student != request.user:
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    if booking.status != 'accepted':
        messages.error(request, 'Only accepted bookings can be completed.')
        return redirect('bookings:detail', booking_id=booking_id)
    
    if request.method == 'POST':
        # Create or update lesson
        lesson, created = Lesson.objects.get_or_create(booking=booking)
        lesson.topics_covered = request.POST.get('topics_covered', '')
        lesson.homework_assigned = request.POST.get('homework_assigned', '')
        lesson.student_progress = request.POST.get('student_progress', '')
        lesson.student_attended = request.POST.get('student_attended') == 'on'
        lesson.tutor_attended = request.POST.get('tutor_attended') == 'on'
        lesson.is_completed = True
        lesson.completed_at = timezone.now()
        lesson.save()
        
        # Update booking status
        booking.status = 'completed'
        booking.completed_at = timezone.now()
        booking.save()
        
        # Auto-deduct payment from wallet if payment exists and is pending
        try:
            payment = Payment.objects.filter(booking=booking, status__in=['pending', 'processing']).first()
            if payment:
                wallet, wallet_created = Wallet.objects.get_or_create(user=booking.student)
                
                # Check if wallet has sufficient balance
                if wallet.balance >= payment.amount:
                    # Deduct from wallet (convert to float for the method, it will convert to Decimal internally)
                    wallet.deduct_balance(
                        float(payment.amount),
                        description=f"Payment for {booking.subject.name} class on {booking.lesson_date}",
                        payment=payment
                    )
                    
                    # Update payment status to on_hold with 1 week cooling period
                    payment.status = 'on_hold'
                    payment.is_wallet_payment = True
                    payment.payment_method = 'wallet'
                    payment.hold_until = timezone.now() + timedelta(weeks=1)
                    payment.paid_at = timezone.now()
                    payment.save()
                    
                    messages.success(request, f'Payment of ₹{payment.amount:.2f} deducted from wallet. Payment on hold for 1 week cooling period.')
                else:
                    messages.warning(request, f'Insufficient wallet balance (₹{wallet.balance:.2f}). Please recharge your wallet to complete payment.')
        except Exception as e:
            # Log error but don't block lesson completion
            messages.warning(request, 'Lesson completed, but payment processing encountered an issue.')
        
        messages.success(request, 'Lesson marked as completed!')
        return redirect('bookings:detail', booking_id=booking_id)
    
    # Get existing lesson if any
    lesson = None
    try:
        lesson = booking.lesson
    except Lesson.DoesNotExist:
        pass
    
    context = {
        'booking': booking,
        'lesson': lesson,
    }
    return render(request, 'bookings/complete_lesson.jinja', context)


@login_required
def lesson_notes(request, booking_id):
    """View and edit lesson notes"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check access
    if booking.tutor != request.user and booking.student != request.user:
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    lesson, created = Lesson.objects.get_or_create(booking=booking)
    
    if request.method == 'POST':
        if booking.tutor == request.user:
            # Tutor can update all fields
            lesson.topics_covered = request.POST.get('topics_covered', '')
            lesson.homework_assigned = request.POST.get('homework_assigned', '')
            lesson.student_progress = request.POST.get('student_progress', '')
        lesson.save()
        messages.success(request, 'Lesson notes updated!')
        return redirect('bookings:lesson_notes', booking_id=booking_id)
    
    context = {
        'booking': booking,
        'lesson': lesson,
    }
    return render(request, 'bookings/lesson_notes.jinja', context)


@login_required
def manage_availability(request):
    """Manage tutor availability slots"""
    if not request.user.is_tutor():
        messages.error(request, 'Access denied. Tutor access required.')
        return redirect('/')
    
    if request.method == 'POST':
        # Delete existing slots
        AvailabilitySlot.objects.filter(tutor=request.user).delete()
        
        # Create new slots
        for day in range(7):
            start_time = request.POST.get(f'day_{day}_start')
            end_time = request.POST.get(f'day_{day}_end')
            if start_time and end_time:
                AvailabilitySlot.objects.create(
                    tutor=request.user,
                    day_of_week=day,
                    start_time=start_time,
                    end_time=end_time,
                )
        
        messages.success(request, 'Availability updated!')
        return redirect('bookings:manage_availability')
    
    # Get current availability
    availability = AvailabilitySlot.objects.filter(tutor=request.user)
    availability_dict = {slot.day_of_week: slot for slot in availability}
    
    context = {
        'availability': availability_dict,
    }
    return render(request, 'bookings/manage_availability.jinja', context)


@login_required
def calendar_sync(request):
    """Manage calendar synchronization"""
    if request.method == 'POST':
        calendar_type = request.POST.get('calendar_type')
        sync_token = request.POST.get('sync_token', '')
        calendar_id = request.POST.get('calendar_id', '')
        
        sync, created = CalendarSync.objects.update_or_create(
            user=request.user,
            calendar_type=calendar_type,
            defaults={
                'sync_token': sync_token,
                'calendar_id': calendar_id,
                'is_active': True,
                'last_synced_at': timezone.now(),
            }
        )
        
        messages.success(request, f'{sync.get_calendar_type_display()} sync configured!')
        return redirect('bookings:calendar_sync')
    
    syncs = CalendarSync.objects.filter(user=request.user)
    
    context = {
        'syncs': syncs,
    }
    return render(request, 'bookings/calendar_sync.jinja', context)
