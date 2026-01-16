# Admin Management Views - All CRUD operations for admin panel
# This file contains all management views for the custom admin panel

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count, Avg
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from functools import wraps
from tutors.models import TutorProfile, TutorDocument, QualityAudit, QualityCertification, Subject
from bookings.models import Booking
from payments.models import Payment, Commission
from users.models import User
from reviews.models import Review, Dispute, SafetyReport
from .forms import AdminUserForm, AdminTutorForm, DisputeResolutionForm, SafetyReportForm, SubjectForm

def admin_required(view_func):
    """Decorator to check if user is admin"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_global_admin() or request.user.is_city_admin()):
            messages.error(request, 'Access denied. Admin access required.')
            # Redirect to appropriate dashboard based on role
            if request.user.is_tutor():
                return redirect('tutors:dashboard')
            elif request.user.is_student() or request.user.is_parent():
                return redirect('students:dashboard')
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper


# ==================== USER MANAGEMENT ====================

@login_required
@admin_required
def user_list(request):
    """List all users with filtering and search"""
    users = User.objects.all()
    
    # Filtering
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(users.order_by('-created_at'), 25)
    page = request.GET.get('page', 1)
    users_page = paginator.get_page(page)
    
    context = {
        'users': users_page,
        'role_filter': role_filter,
        'search_query': search_query,
        'total_count': users.count(),
    }
    return render(request, 'admin_panel/users/list.jinja', context)


@login_required
@admin_required
def user_detail(request, user_id):
    """View user details"""
    target_user = get_object_or_404(User, id=user_id)
    
    # Get related data
    tutor_profile = getattr(target_user, 'tutor_profile', None)
    bookings = Booking.objects.filter(Q(student=target_user) | Q(tutor=target_user)).order_by('-created_at')[:10]
    payments = Payment.objects.filter(Q(student=target_user) | Q(tutor=target_user)).order_by('-created_at')[:10]
    reviews = Review.objects.filter(Q(student=target_user) | Q(tutor=target_user)).order_by('-created_at')[:10]
    
    context = {
        'target_user': target_user,  # Renamed to avoid conflict with auth context processor
        'tutor_profile': tutor_profile,
        'bookings': bookings,
        'payments': payments,
        'reviews': reviews,
    }
    return render(request, 'admin_panel/users/detail.jinja', context)


@login_required
@admin_required
def user_create(request):
    """Create a new user"""
    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            target_user = form.save()
            messages.success(request, f'User {target_user.username} created successfully!')
            return redirect('admin_panel:user_detail', user_id=target_user.id)
    else:
        form = AdminUserForm()
    
    context = {'form': form, 'action': 'Create', 'target_user': None}
    return render(request, 'admin_panel/users/form.jinja', context)


@login_required
@admin_required
def user_edit(request, user_id):
    """Edit a user"""
    target_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = AdminUserForm(request.POST, instance=target_user)
        if form.is_valid():
            target_user = form.save()
            messages.success(request, f'User {target_user.username} updated successfully!')
            return redirect('admin_panel:user_detail', user_id=target_user.id)
    else:
        form = AdminUserForm(instance=target_user)
    
    context = {'form': form, 'target_user': target_user, 'action': 'Edit'}  # Renamed to avoid conflict
    return render(request, 'admin_panel/users/form.jinja', context)


@login_required
@admin_required
def user_delete(request, user_id):
    """Delete a user"""
    target_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = target_user.username
        target_user.delete()
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('admin_panel:user_list')
    
    context = {'target_user': target_user}  # Renamed to avoid conflict
    return render(request, 'admin_panel/users/delete.jinja', context)


# ==================== TUTOR MANAGEMENT ====================

@login_required
@admin_required
def tutor_list(request):
    """List all tutors with filtering"""
    tutors = TutorProfile.objects.all()
    
    # Filtering
    status_filter = request.GET.get('status')
    if status_filter:
        tutors = tutors.filter(verification_status=status_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        tutors = tutors.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(bio__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(tutors.select_related('user').order_by('-created_at'), 25)
    page = request.GET.get('page', 1)
    tutors_page = paginator.get_page(page)
    
    context = {
        'tutors': tutors_page,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_count': tutors.count(),
    }
    return render(request, 'admin_panel/tutors/list.jinja', context)


@login_required
@admin_required
def tutor_detail(request, tutor_id):
    """View tutor details"""
    tutor = get_object_or_404(TutorProfile, id=tutor_id)
    documents = TutorDocument.objects.filter(tutor=tutor).order_by('-created_at')
    audits = QualityAudit.objects.filter(tutor=tutor).order_by('-created_at')[:10]
    bookings = Booking.objects.filter(tutor=tutor.user).order_by('-created_at')[:10]
    reviews = Review.objects.filter(tutor=tutor.user).order_by('-created_at')[:10]
    
    context = {
        'tutor': tutor,
        'documents': documents,
        'audits': audits,
        'bookings': bookings,
        'reviews': reviews,
    }
    return render(request, 'admin_panel/tutors/detail.jinja', context)


@login_required
@admin_required
def tutor_edit(request, tutor_id):
    """Edit a tutor profile"""
    tutor = get_object_or_404(TutorProfile, id=tutor_id)
    
    if request.method == 'POST':
        form = AdminTutorForm(request.POST, instance=tutor)
        if form.is_valid():
            tutor = form.save()
            messages.success(request, f'Tutor profile updated successfully!')
            return redirect('admin_panel:tutor_detail', tutor_id=tutor.id)
    else:
        form = AdminTutorForm(instance=tutor)
    
    context = {'form': form, 'tutor': tutor}
    return render(request, 'admin_panel/tutors/form.jinja', context)


# ==================== BOOKING MANAGEMENT ====================

@login_required
@admin_required
def booking_list(request):
    """List all bookings"""
    bookings = Booking.objects.all()
    
    # Filtering
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        bookings = bookings.filter(
            Q(student__username__icontains=search_query) |
            Q(tutor__username__icontains=search_query) |
            Q(subject__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(bookings.select_related('student', 'tutor', 'subject').order_by('-created_at'), 25)
    page = request.GET.get('page', 1)
    bookings_page = paginator.get_page(page)
    
    context = {
        'bookings': bookings_page,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_count': bookings.count(),
    }
    return render(request, 'admin_panel/bookings/list.jinja', context)


@login_required
@admin_required
def booking_detail(request, booking_id):
    """View booking details"""
    booking = get_object_or_404(Booking, id=booking_id)
    payments = Payment.objects.filter(booking=booking).order_by('-created_at')
    reviews = Review.objects.filter(booking=booking)
    
    context = {
        'booking': booking,
        'payments': payments,
        'reviews': reviews,
    }
    return render(request, 'admin_panel/bookings/detail.jinja', context)


# ==================== PAYMENT MANAGEMENT ====================

@login_required
@admin_required
def payment_list(request):
    """List all payments"""
    payments = Payment.objects.all()
    
    # Filtering
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        payments = payments.filter(
            Q(student__username__icontains=search_query) |
            Q(tutor__username__icontains=search_query) |
            Q(transaction_id__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(payments.select_related('student', 'tutor', 'booking').order_by('-created_at'), 25)
    page = request.GET.get('page', 1)
    payments_page = paginator.get_page(page)
    
    # Statistics
    total_revenue = payments.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    total_commission = payments.filter(status='completed').aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
    
    context = {
        'payments': payments_page,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_count': payments.count(),
        'total_revenue': total_revenue,
        'total_commission': total_commission,
    }
    return render(request, 'admin_panel/payments/list.jinja', context)


@login_required
@admin_required
def payment_detail(request, payment_id):
    """View payment details"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    context = {'payment': payment}
    return render(request, 'admin_panel/payments/detail.jinja', context)


# ==================== REVIEW MANAGEMENT ====================

@login_required
@admin_required
def review_list(request):
    """List all reviews"""
    reviews = Review.objects.all()
    
    # Filtering
    rating_filter = request.GET.get('rating')
    if rating_filter:
        reviews = reviews.filter(rating=rating_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        reviews = reviews.filter(
            Q(student__username__icontains=search_query) |
            Q(tutor__username__icontains=search_query) |
            Q(comment__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(reviews.select_related('student', 'tutor').order_by('-created_at'), 25)
    page = request.GET.get('page', 1)
    reviews_page = paginator.get_page(page)
    
    context = {
        'reviews': reviews_page,
        'rating_filter': rating_filter,
        'search_query': search_query,
        'total_count': reviews.count(),
    }
    return render(request, 'admin_panel/reviews/list.jinja', context)


@login_required
@admin_required
def review_detail(request, review_id):
    """View review details"""
    review = get_object_or_404(Review, id=review_id)
    
    context = {'review': review}
    return render(request, 'admin_panel/reviews/detail.jinja', context)


# ==================== DISPUTE MANAGEMENT ====================

@login_required
@admin_required
def dispute_list(request):
    """List all disputes"""
    disputes = Dispute.objects.all()
    
    # Filtering
    status_filter = request.GET.get('status')
    if status_filter:
        disputes = disputes.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(disputes.select_related('booking', 'raised_by').order_by('-created_at'), 25)
    page = request.GET.get('page', 1)
    disputes_page = paginator.get_page(page)
    
    context = {
        'disputes': disputes_page,
        'status_filter': status_filter,
        'total_count': disputes.count(),
    }
    return render(request, 'admin_panel/disputes/list.jinja', context)


@login_required
@admin_required
def dispute_detail(request, dispute_id):
    """View and resolve dispute"""
    dispute = get_object_or_404(Dispute, id=dispute_id)
    
    if request.method == 'POST':
        form = DisputeResolutionForm(request.POST, instance=dispute)
        if form.is_valid():
            dispute = form.save(commit=False)
            dispute.resolved_by = request.user
            dispute.resolved_at = timezone.now()
            dispute.save()
            messages.success(request, 'Dispute resolved successfully!')
            return redirect('admin_panel:dispute_list')
    else:
        form = DisputeResolutionForm(instance=dispute)
    
    context = {'dispute': dispute, 'form': form}
    return render(request, 'admin_panel/disputes/detail.jinja', context)


# ==================== SAFETY REPORT MANAGEMENT ====================

@login_required
@admin_required
def safety_report_list(request):
    """List all safety reports"""
    reports = SafetyReport.objects.all()
    
    # Filtering
    status_filter = request.GET.get('status')
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(reports.select_related('reported_by', 'reported_user').order_by('-created_at'), 25)
    page = request.GET.get('page', 1)
    reports_page = paginator.get_page(page)
    
    context = {
        'reports': reports_page,
        'status_filter': status_filter,
        'total_count': reports.count(),
    }
    return render(request, 'admin_panel/safety_reports/list.jinja', context)


@login_required
@admin_required
def safety_report_detail(request, report_id):
    """View and handle safety report"""
    report = get_object_or_404(SafetyReport, id=report_id)
    
    if request.method == 'POST':
        form = SafetyReportForm(request.POST, instance=report)
        if form.is_valid():
            report = form.save(commit=False)
            report.investigated_by = request.user
            report.save()
            messages.success(request, 'Safety report handled successfully!')
            return redirect('admin_panel:safety_report_list')
    else:
        form = SafetyReportForm(instance=report)
    
    context = {'report': report, 'form': form}
    return render(request, 'admin_panel/safety_reports/detail.jinja', context)


# ==================== DOCUMENT MANAGEMENT ====================

@login_required
@admin_required
def document_list(request):
    """List all tutor documents"""
    documents = TutorDocument.objects.all()
    
    # Filtering
    verified_filter = request.GET.get('verified')
    if verified_filter == 'true':
        documents = documents.filter(is_verified=True)
    elif verified_filter == 'false':
        documents = documents.filter(is_verified=False)
    
    doc_type_filter = request.GET.get('type')
    if doc_type_filter:
        documents = documents.filter(document_type=doc_type_filter)
    
    # Pagination
    paginator = Paginator(documents.select_related('tutor', 'tutor__user', 'verified_by').order_by('-created_at'), 25)
    page = request.GET.get('page', 1)
    documents_page = paginator.get_page(page)
    
    context = {
        'documents': documents_page,
        'verified_filter': verified_filter,
        'doc_type_filter': doc_type_filter,
        'total_count': documents.count(),
    }
    return render(request, 'admin_panel/documents/list.jinja', context)


# ==================== SUBJECT MANAGEMENT ====================

@login_required
@admin_required
def subject_list(request):
    """List all subjects"""
    subjects = Subject.objects.all()
    
    search_query = request.GET.get('search')
    if search_query:
        subjects = subjects.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(subjects.order_by('name'), 25)
    page = request.GET.get('page', 1)
    subjects_page = paginator.get_page(page)
    
    context = {
        'subjects': subjects_page,
        'search_query': search_query,
        'total_count': subjects.count(),
    }
    return render(request, 'admin_panel/subjects/list.jinja', context)


@login_required
@admin_required
def subject_create(request):
    """Create a new subject"""
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f'Subject {subject.name} created successfully!')
            return redirect('admin_panel:subject_list')
    else:
        form = SubjectForm()
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'admin_panel/subjects/form.jinja', context)


@login_required
@admin_required
def subject_edit(request, subject_id):
    """Edit a subject"""
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f'Subject {subject.name} updated successfully!')
            return redirect('admin_panel:subject_list')
    else:
        form = SubjectForm(instance=subject)
    
    context = {'form': form, 'subject': subject, 'action': 'Edit'}
    return render(request, 'admin_panel/subjects/form.jinja', context)


@login_required
@admin_required
def subject_delete(request, subject_id):
    """Delete a subject"""
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        name = subject.name
        subject.delete()
        messages.success(request, f'Subject {name} deleted successfully!')
        return redirect('admin_panel:subject_list')
    
    context = {'subject': subject}
    return render(request, 'admin_panel/subjects/delete.jinja', context)

