from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Review, Dispute, SafetyReport, ContentModeration
from bookings.models import Booking


@login_required
def create_review(request, booking_id):
    """Create a review for a completed booking"""
    booking = get_object_or_404(Booking, id=booking_id, student=request.user, status='completed')
    
    # Check if review already exists
    if Review.objects.filter(booking=booking, student=request.user).exists():
        messages.error(request, 'You have already reviewed this booking.')
        return redirect('bookings:detail', booking_id=booking_id)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()
        
        if not comment:
            messages.error(request, 'Please provide a review comment.')
            return redirect('reviews:create', booking_id=booking_id)
        
        review = Review.objects.create(
            booking=booking,
            student=request.user,
            tutor=booking.tutor,
            rating=rating,
            comment=comment,
            is_approved=True  # Auto-approve for now, can be moderated later
        )
        
        # Update tutor's average rating
        from tutors.models import TutorProfile
        from django.db.models import Avg
        tutor_profile = booking.tutor.tutor_profile
        reviews = Review.objects.filter(tutor=booking.tutor, is_approved=True)
        tutor_profile.average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        tutor_profile.total_reviews = reviews.count()
        tutor_profile.save()
        
        messages.success(request, 'Review submitted successfully!')
        return redirect('bookings:detail', booking_id=booking_id)
    
    context = {
        'booking': booking,
    }
    return render(request, 'reviews/create.jinja', context)


@login_required
def raise_dispute(request, booking_id):
    """Raise a dispute for a booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check access
    if booking.student != request.user and booking.tutor != request.user:
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    if request.method == 'POST':
        dispute_type = request.POST.get('dispute_type')
        description = request.POST.get('description', '').strip()
        
        if not description:
            messages.error(request, 'Please provide a description of the dispute.')
            return redirect('reviews:raise_dispute', booking_id=booking_id)
        
        Dispute.objects.create(
            booking=booking,
            raised_by=request.user,
            dispute_type=dispute_type,
            description=description,
            status='open'
        )
        
        messages.success(request, 'Dispute raised successfully. Our team will review it shortly.')
        return redirect('bookings:detail', booking_id=booking_id)
    
    context = {
        'booking': booking,
    }
    return render(request, 'reviews/raise_dispute.jinja', context)


@login_required
def report_safety_issue(request, user_id):
    """Report a safety issue"""
    from users.models import User
    reported_user = get_object_or_404(User, id=user_id)
    
    if reported_user == request.user:
        messages.error(request, 'Cannot report yourself.')
        return redirect('/')
    
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        description = request.POST.get('description', '').strip()
        
        if not description:
            messages.error(request, 'Please provide a description of the safety issue.')
            return redirect('reviews:report_safety', user_id=user_id)
        
        safety_report = SafetyReport.objects.create(
            reported_by=request.user,
            reported_user=reported_user,
            report_type=report_type,
            description=description,
            status='pending'
        )
        
        # Handle file upload if provided
        if 'evidence' in request.FILES:
            safety_report.evidence = request.FILES['evidence']
            safety_report.save()
        
        messages.success(request, 'Safety report submitted. Our team will investigate immediately.')
        return redirect('/')
    
    context = {
        'reported_user': reported_user,
    }
    return render(request, 'reviews/report_safety.jinja', context)


@login_required
def dispute_detail(request, dispute_id):
    """View dispute details (for students and tutors)"""
    dispute = get_object_or_404(Dispute, id=dispute_id)
    
    # Check access - user must be either the one who raised it or the tutor/student in the booking
    has_access = (
        dispute.raised_by == request.user or
        dispute.booking.student == request.user or
        dispute.booking.tutor == request.user
    )
    
    if not has_access:
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    context = {
        'dispute': dispute,
        'booking': dispute.booking,
    }
    return render(request, 'reviews/dispute_detail.jinja', context)


@login_required
def flag_content(request):
    """Flag inappropriate content"""
    if request.method == 'POST':
        content_type = request.POST.get('content_type')
        content_id = request.POST.get('content_id')
        reason = request.POST.get('reason', '').strip()
        
        if not reason:
            messages.error(request, 'Please provide a reason for flagging.')
            return redirect('/')
        
        ContentModeration.objects.create(
            content_type=content_type,
            content_id=content_id,
            flagged_by=request.user,
            reason=reason,
            is_resolved=False
        )
        
        messages.success(request, 'Content flagged. Our moderation team will review it.')
        return redirect('/')
    
    return redirect('/')
