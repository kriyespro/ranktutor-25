from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from django.core.paginator import Paginator
from django.utils import timezone
from tutors.models import TutorProfile, TutorDocument, QualityAudit, QualityCertification, Subject
from bookings.models import Booking
from payments.models import Payment, Commission
from users.models import User
from reviews.models import Review, Dispute, SafetyReport
from .forms import AdminUserForm, AdminTutorForm, DisputeResolutionForm, SafetyReportForm, SubjectForm


@login_required
def admin_dashboard_redirect(request):
    """Redirect to appropriate admin dashboard based on user role"""
    # Debug: Check user role
    if not hasattr(request.user, 'role'):
        messages.error(request, 'User role not found.')
        return redirect('/')
    
    if request.user.is_global_admin():
        return redirect('admin_panel:global_dashboard')
    elif request.user.is_city_admin():
        return redirect('admin_panel:city_dashboard')
    else:
        messages.error(request, 'Access denied. Admin access required.')
        # Redirect to appropriate dashboard based on role
        if request.user.is_tutor():
            return redirect('tutors:dashboard')
        elif request.user.is_student() or request.user.is_parent():
            return redirect('students:dashboard')
        return redirect('/')


@login_required
def city_admin_dashboard(request):
    """City Admin dashboard"""
    if not request.user.is_city_admin():
        messages.error(request, 'Access denied. City Admin access required.')
        # Redirect to appropriate dashboard based on role
        if request.user.is_tutor():
            return redirect('tutors:dashboard')
        elif request.user.is_student() or request.user.is_parent():
            return redirect('students:dashboard')
        elif request.user.is_global_admin():
            return redirect('admin_panel:global_dashboard')
        return redirect('/')
    
    # Get pending items
    pending_tutors = TutorProfile.objects.filter(verification_status='pending').count()
    pending_documents = TutorDocument.objects.filter(is_verified=False).count()
    pending_disputes = Dispute.objects.filter(status='open').count()
    pending_safety_reports = SafetyReport.objects.filter(status='pending').count()
    
    # Recent bookings
    recent_bookings = Booking.objects.all().order_by('-created_at')[:10]
    
    context = {
        'pending_tutors': pending_tutors,
        'pending_documents': pending_documents,
        'pending_disputes': pending_disputes,
        'pending_safety_reports': pending_safety_reports,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'admin_panel/city_dashboard.jinja', context)


@login_required
def global_admin_dashboard(request):
    """Global Admin dashboard"""
    # Debug: Check user and role
    if not hasattr(request.user, 'role'):
        messages.error(request, 'User role not found.')
        return redirect('/')
    
    if not request.user.is_global_admin():
        messages.error(request, f'Access denied. Global Admin access required. Your role: {request.user.role}')
        # Redirect to appropriate dashboard based on role
        if request.user.is_tutor():
            return redirect('tutors:dashboard')
        elif request.user.is_student() or request.user.is_parent():
            return redirect('students:dashboard')
        elif request.user.is_city_admin():
            return redirect('admin_panel:city_dashboard')
        return redirect('/')
    
    # Platform-wide statistics
    total_users = User.objects.count()
    total_students = User.objects.filter(role__in=['student', 'parent']).count()
    total_tutors = TutorProfile.objects.count()
    total_city_admins = User.objects.filter(role='city_admin').count()
    total_bookings = Booking.objects.count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    total_commission = Payment.objects.filter(status='completed').aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
    
    # Quality metrics
    tutors_needing_intervention = TutorProfile.objects.filter(intervention_required=True).count()
    low_quality_tutors = TutorProfile.objects.filter(quality_score__lt=50).count()
    verified_tutors = TutorProfile.objects.filter(is_verified=True).count()
    
    # Pending items
    pending_tutors = TutorProfile.objects.filter(verification_status='pending').count()
    pending_documents = TutorDocument.objects.filter(is_verified=False).count()
    pending_disputes = Dispute.objects.filter(status='open').count()
    pending_safety_reports = SafetyReport.objects.filter(status='pending').count()
    
    # Reviews and ratings
    total_reviews = Review.objects.count()
    avg_rating = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Recent activity
    recent_bookings = Booking.objects.all().order_by('-created_at')[:5]
    recent_payments = Payment.objects.all().order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_tutors': total_tutors,
        'total_city_admins': total_city_admins,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'total_commission': total_commission,
        'pending_tutors': pending_tutors,
        'pending_documents': pending_documents,
        'pending_disputes': pending_disputes,
        'pending_safety_reports': pending_safety_reports,
        'tutors_needing_intervention': tutors_needing_intervention,
        'low_quality_tutors': low_quality_tutors,
        'verified_tutors': verified_tutors,
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        'recent_bookings': recent_bookings,
        'recent_payments': recent_payments,
    }
    return render(request, 'admin_panel/global_dashboard.jinja', context)


@login_required
def verify_tutor_document(request, document_id):
    """Verify a tutor document"""
    if not (request.user.is_city_admin() or request.user.is_global_admin()):
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    document = get_object_or_404(TutorDocument, id=document_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            document.is_verified = True
            document.verification_status = 'approved'
            document.verified_by = request.user
            document.verified_at = timezone.now()
            document.notes = notes
            messages.success(request, 'Document approved.')
        elif action == 'reject':
            document.is_verified = False
            document.verification_status = 'rejected'
            document.verified_by = request.user
            document.verified_at = timezone.now()
            document.notes = notes
            messages.warning(request, 'Document rejected.')
        
        document.save()
        
        # Update tutor profile verification flags based on document type
        tutor_profile = document.tutor
        if document.document_type == 'academic':
            tutor_profile.has_academic_verification = document.is_verified
        elif document.document_type == 'id_proof':
            tutor_profile.has_id_verification = document.is_verified
        elif document.document_type == 'police_verification':
            tutor_profile.has_police_verification = document.is_verified
        elif document.document_type == 'certification':
            tutor_profile.has_background_check = document.is_verified
        tutor_profile.save()
        
        return redirect('admin_panel:city_dashboard')
    
    context = {
        'document': document,
    }
    return render(request, 'admin_panel/verify_document.jinja', context)


@login_required
def approve_tutor(request, tutor_id):
    """Approve a tutor profile"""
    if not (request.user.is_city_admin() or request.user.is_global_admin()):
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    tutor = get_object_or_404(TutorProfile, id=tutor_id)
    
    if request.method == 'POST':
        tutor.verification_status = 'approved'
        tutor.is_verified = True
        tutor.save()
        
        # Run quality audit
        quality_score = tutor.calculate_quality_score()
        tutor.quality_score = quality_score
        tutor.last_quality_audit = timezone.now()
        tutor.save()
        
        messages.success(request, 'Tutor approved and quality score calculated!')
        return redirect('admin_panel:city_dashboard')
    
    context = {
        'tutor': tutor,
    }
    return render(request, 'admin_panel/approve_tutor.jinja', context)


@login_required
def conduct_quality_audit(request, tutor_id):
    """Conduct a quality audit for a tutor"""
    if not (request.user.is_city_admin() or request.user.is_global_admin()):
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    tutor = get_object_or_404(TutorProfile, id=tutor_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Handle resolve intervention action
        if action == 'resolve_intervention':
            tutor.intervention_required = False
            tutor.save()
            messages.success(request, 'Intervention resolved. Tutor is no longer flagged for intervention.')
            return redirect('admin_panel:quality_audits')
        
        # Handle complete audit
        audit_type = request.POST.get('audit_type', 'manual')
        issues_found = request.POST.get('issues_found', '')
        recommendations = request.POST.get('recommendations', '')
        mark_resolved = request.POST.get('mark_resolved') == 'on'
        
        # Calculate quality score
        quality_score = tutor.calculate_quality_score()
        
        # Override with manual score if provided
        manual_score = request.POST.get('manual_score')
        if manual_score:
            try:
                quality_score = float(manual_score)
            except (ValueError, TypeError):
                pass
        
        # Create audit record
        audit = QualityAudit.objects.create(
            tutor=tutor,
            audit_type=audit_type,
            quality_score=quality_score,
            issues_found=issues_found,
            recommendations=recommendations,
            audited_by=request.user,
            is_resolved=mark_resolved
        )
        
        # Update tutor profile
        tutor.quality_score = quality_score
        tutor.last_quality_audit = timezone.now()
        tutor.quality_issues = issues_found
        
        # Set intervention flag if score is low
        if quality_score < 50:
            tutor.intervention_required = True
        elif mark_resolved or quality_score >= 50:
            # Clear intervention if resolved or score is acceptable
            tutor.intervention_required = False
        
        tutor.save()
        
        messages.success(request, f'Quality audit completed. Score: {quality_score:.1f}/100')
        return redirect('admin_panel:quality_audits')
    
    # Calculate current score
    current_score = tutor.calculate_quality_score()
    
    # Get recent audits
    recent_audits = QualityAudit.objects.filter(tutor=tutor).order_by('-created_at')[:5]
    
    context = {
        'tutor': tutor,
        'current_score': current_score,
        'recent_audits': recent_audits,
    }
    return render(request, 'admin_panel/conduct_audit.jinja', context)


@login_required
def quality_audits_list(request):
    """List all quality audits"""
    if not (request.user.is_city_admin() or request.user.is_global_admin()):
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    audits = QualityAudit.objects.all().order_by('-created_at')[:50]
    tutors_needing_intervention = TutorProfile.objects.filter(intervention_required=True)
    low_quality_tutors = TutorProfile.objects.filter(quality_score__lt=50)
    
    context = {
        'audits': audits,
        'tutors_needing_intervention': tutors_needing_intervention,
        'low_quality_tutors': low_quality_tutors,
    }
    return render(request, 'admin_panel/quality_audits.jinja', context)


@login_required
def issue_certification(request, tutor_id):
    """Issue a quality certification to a tutor"""
    if not (request.user.is_city_admin() or request.user.is_global_admin()):
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    tutor = get_object_or_404(TutorProfile, id=tutor_id)
    
    if request.method == 'POST':
        certification_type = request.POST.get('certification_type')
        valid_days = int(request.POST.get('valid_days', 365))
        
        QualityCertification.objects.create(
            tutor=tutor,
            certification_type=certification_type,
            issued_by=request.user,
            valid_until=timezone.now() + timezone.timedelta(days=valid_days),
            is_active=True
        )
        
        messages.success(request, 'Certification issued successfully!')
        return redirect('admin_panel:quality_audits')
    
    context = {
        'tutor': tutor,
    }
    return render(request, 'admin_panel/issue_certification.jinja', context)


@login_required
def teaching_level_management(request):
    """View teaching level configuration"""
    if not request.user.is_global_admin():
        messages.error(request, 'Access denied. Global Admin access required.')
        return redirect('/')

    teaching_level_field = TutorProfile._meta.get_field('teaching_levels')
    teaching_levels = teaching_level_field.choices

    context = {
        'teaching_levels': teaching_levels,
    }
    return render(request, 'admin_panel/system/teaching_levels.jinja', context)
