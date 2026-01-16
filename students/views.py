from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Exists, OuterRef, Count, Avg
from .models import StudentProfile
from bookings.models import Booking
from payments.models import Payment, Wallet
from reviews.models import Review, Dispute
from tutors.utils import get_ai_recommendations
from tutors.models import TutorProfile


@login_required
def student_dashboard(request):
    """Student dashboard"""
    if not (request.user.is_student() or request.user.is_parent()):
        messages.error(request, 'Access denied. Student/Parent access required.')
        # Redirect to appropriate dashboard based on role
        if request.user.is_tutor():
            return redirect('tutors:dashboard')
        elif request.user.is_city_admin():
            return redirect('admin_panel:city_dashboard')
        elif request.user.is_global_admin():
            return redirect('admin_panel:global_dashboard')
        return redirect('/')
    
    student_profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    # Get or create wallet
    wallet, wallet_created = Wallet.objects.get_or_create(user=request.user)
    
    # Get AI recommendations
    ai_recommendations = []
    if student_profile.preferred_subjects.exists():
        ai_recommendations = get_ai_recommendations(student_profile, limit=5)
    
    # Get bookings
    upcoming_bookings = Booking.objects.filter(
        student=request.user,
        status__in=['pending', 'accepted'],
        lesson_date__gte=timezone.now().date()
    ).order_by('lesson_date', 'lesson_time')[:10]
    
    # Get accepted bookings that need payment (no completed payment exists)
    # Show bookings that either have no payment, or have pending/processing payment
    completed_payment_booking_ids = Payment.objects.filter(
        booking__student=request.user,
        status='completed'
    ).values_list('booking_id', flat=True)
    
    bookings_needing_payment = Booking.objects.filter(
        student=request.user,
        status='accepted'
    ).exclude(
        id__in=completed_payment_booking_ids
    ).order_by('lesson_date', 'lesson_time')[:10]
    
    # Get past bookings
    past_bookings = Booking.objects.filter(
        student=request.user,
        status='completed'
    ).order_by('-lesson_date', '-lesson_time')[:10]
    
    # Get completed bookings that need review (no review exists yet)
    bookings_needing_review = Booking.objects.filter(
        student=request.user,
        status='completed'
    ).exclude(
        Exists(Review.objects.filter(booking=OuterRef('pk'), student=request.user))
    ).order_by('-lesson_date', '-lesson_time')[:10]
    
    # Get all disputes raised by student
    student_disputes = Dispute.objects.filter(
        raised_by=request.user
    ).order_by('-created_at')[:10]
    
    context = {
        'student_profile': student_profile,
        'upcoming_bookings': upcoming_bookings,
        'bookings_needing_payment': bookings_needing_payment,
        'past_bookings': past_bookings,
        'bookings_needing_review': bookings_needing_review,
        'student_disputes': student_disputes,
        'ai_recommendations': ai_recommendations,
    }
    return render(request, 'students/dashboard.jinja', context)


@login_required
def student_classes(request):
    """Student classes view - past and upcoming in table format"""
    if not (request.user.is_student() or request.user.is_parent()):
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    # Get all upcoming bookings
    upcoming_bookings = Booking.objects.filter(
        student=request.user,
        status__in=['pending', 'accepted'],
        lesson_date__gte=timezone.now().date()
    ).order_by('lesson_date', 'lesson_time')
    
    # Get all past bookings
    past_bookings = Booking.objects.filter(
        student=request.user,
        status__in=['completed', 'cancelled']
    ).order_by('-lesson_date', '-lesson_time')
    
    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
    }
    return render(request, 'students/classes.jinja', context)


@login_required
def student_payments(request):
    """Student payments view - check past classes and pay now"""
    if not (request.user.is_student() or request.user.is_parent()):
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    # Get accepted bookings that need payment
    completed_payment_booking_ids = Payment.objects.filter(
        booking__student=request.user,
        status='completed'
    ).values_list('booking_id', flat=True)
    
    bookings_needing_payment = Booking.objects.filter(
        student=request.user,
        status='accepted'
    ).exclude(
        id__in=completed_payment_booking_ids
    ).order_by('lesson_date', 'lesson_time')
    
    # Get past bookings with pending payments
    past_bookings_with_pending_payment = Booking.objects.filter(
        student=request.user,
        status='completed'
    ).filter(
        payments__status__in=['pending', 'processing']
    ).distinct().prefetch_related('payments').order_by('-lesson_date', '-lesson_time')
    
    # Create a dictionary mapping booking IDs to their pending payments
    booking_pending_payments = {}
    for booking in past_bookings_with_pending_payment:
        pending_payments = [p for p in booking.payments.all() if p.status in ['pending', 'processing']]
        if pending_payments:
            booking_pending_payments[booking.id] = pending_payments[0]  # Get first pending payment
    
    # Get all payments
    all_payments = Payment.objects.filter(
        student=request.user
    ).order_by('-created_at')
    
    context = {
        'bookings_needing_payment': bookings_needing_payment,
        'past_bookings_with_pending_payment': past_bookings_with_pending_payment,
        'booking_pending_payments': booking_pending_payments,
        'all_payments': all_payments,
    }
    return render(request, 'students/payments.jinja', context)


@login_required
def student_homework(request):
    """Student homework view"""
    if not (request.user.is_student() or request.user.is_parent()):
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    from bookings.models import Lesson
    
    # Get all completed lessons with homework
    lessons_with_homework = Lesson.objects.filter(
        booking__student=request.user,
        is_completed=True
    ).exclude(
        homework_assigned=''
    ).order_by('-completed_at')
    
    # Get upcoming lessons
    upcoming_bookings = Booking.objects.filter(
        student=request.user,
        status__in=['pending', 'accepted'],
        lesson_date__gte=timezone.now().date()
    ).order_by('lesson_date', 'lesson_time')
    
    context = {
        'lessons_with_homework': lessons_with_homework,
        'upcoming_bookings': upcoming_bookings,
    }
    return render(request, 'students/homework.jinja', context)


@login_required
def my_tutors(request):
    """My Tutors view - shows all tutors student has taken classes with"""
    if not (request.user.is_student() or request.user.is_parent()):
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    # Get all bookings for this student (completed, accepted, or any with classes)
    student_bookings = Booking.objects.filter(
        student=request.user
    ).select_related('tutor', 'subject')
    
    # Get unique tutor IDs from all bookings using a set to ensure uniqueness
    tutor_ids = list(set(student_bookings.values_list('tutor_id', flat=True)))
    
    # Get unique tutor profiles directly (handles OneToOneField properly)
    tutor_profiles = TutorProfile.objects.filter(
        user_id__in=tutor_ids
    ).select_related('user').distinct()
    
    # Get tutor profiles with additional info
    tutors_with_info = []
    processed_tutor_ids = set()  # Track tutor user IDs we've already processed
    
    for tutor_profile in tutor_profiles:
        # Skip if we've already processed this tutor (by user_id)
        if tutor_profile.user_id in processed_tutor_ids:
            continue
        
        processed_tutor_ids.add(tutor_profile.user_id)
        
        # Get booking stats for this tutor
        tutor_bookings = student_bookings.filter(tutor_id=tutor_profile.user_id)
        total_classes = tutor_bookings.count()
        completed_classes = tutor_bookings.filter(status='completed').count()
        last_class_date = tutor_bookings.order_by('-lesson_date').first()
        first_class_date = tutor_bookings.order_by('lesson_date').first()
        
        # Get subjects taught to this student
        subjects_taught = tutor_bookings.values_list('subject__name', flat=True).distinct()
        
        # Get reviews given by this student for this tutor
        student_reviews = Review.objects.filter(
            tutor=tutor_profile.user,
            student=request.user
        ).order_by('-created_at')
        
        tutors_with_info.append({
            'tutor_profile': tutor_profile,
            'total_classes': total_classes,
            'completed_classes': completed_classes,
            'last_class_date': last_class_date.lesson_date if last_class_date else None,
            'first_class_date': first_class_date.lesson_date if first_class_date else None,
            'subjects_taught': list(subjects_taught),
            'has_reviewed': student_reviews.exists(),
            'student_reviews': list(student_reviews),
        })
    
    # Sort by last class date (most recent first)
    tutors_with_info.sort(key=lambda x: x['last_class_date'] if x['last_class_date'] else timezone.now().date(), reverse=True)
    
    context = {
        'tutors_with_info': tutors_with_info,
        'total_tutors': len(tutors_with_info),
    }
    return render(request, 'students/my_tutors.jinja', context)
