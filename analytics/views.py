from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from django.http import HttpResponse, JsonResponse
from datetime import timedelta
from django.db.models.functions import TruncDate, TruncMonth
from django.contrib import messages
import csv
import json
from users.models import User
from tutors.models import TutorProfile
from bookings.models import Booking
from payments.models import Payment, Commission
from reviews.models import Review


@login_required
def analytics_dashboard(request):
    """Analytics dashboard - accessible to admins"""
    if not (request.user.is_city_admin() or request.user.is_global_admin()):
        messages.error(request, 'Access denied. Admin access required.')
        return redirect('/')
    
    # Date ranges
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # User metrics
    total_users = User.objects.count()
    new_users_30d = User.objects.filter(date_joined__gte=last_30_days).count()
    new_users_7d = User.objects.filter(date_joined__gte=last_7_days).count()
    
    # Tutor metrics
    total_tutors = TutorProfile.objects.filter(is_verified=True).count()
    pending_tutors = TutorProfile.objects.filter(verification_status='pending').count()
    verified_tutors_30d = TutorProfile.objects.filter(
        is_verified=True,
        created_at__gte=last_30_days
    ).count()
    
    # Booking metrics
    total_bookings = Booking.objects.count()
    bookings_30d = Booking.objects.filter(created_at__gte=last_30_days).count()
    bookings_7d = Booking.objects.filter(created_at__gte=last_7_days).count()
    completed_bookings = Booking.objects.filter(status='completed').count()
    conversion_rate = (completed_bookings / total_bookings * 100) if total_bookings > 0 else 0
    
    # Revenue metrics
    total_revenue = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    revenue_30d = Payment.objects.filter(
        status='completed',
        created_at__gte=last_30_days
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    revenue_7d = Payment.objects.filter(
        status='completed',
        created_at__gte=last_7_days
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_commission = Commission.objects.filter(is_paid_to_platform=True).aggregate(Sum('amount'))['amount__sum'] or 0
    commission_30d = Commission.objects.filter(
        is_paid_to_platform=True,
        created_at__gte=last_30_days
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Review metrics
    total_reviews = Review.objects.filter(is_approved=True).count()
    avg_rating = Review.objects.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Booking trends (last 30 days)
    booking_trends = Booking.objects.filter(
        created_at__gte=last_30_days
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Revenue trends (last 30 days)
    revenue_trends = Payment.objects.filter(
        status='completed',
        created_at__gte=last_30_days
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        revenue=Sum('amount')
    ).order_by('date')
    
    # Top subjects
    top_subjects = Booking.objects.values('subject__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Top tutors by bookings
    top_tutors = Booking.objects.values(
        'tutor__username',
        'tutor__tutor_profile__city'
    ).annotate(
        booking_count=Count('id')
    ).order_by('-booking_count')[:10]
    
    context = {
        # User metrics
        'total_users': total_users,
        'new_users_30d': new_users_30d,
        'new_users_7d': new_users_7d,
        
        # Tutor metrics
        'total_tutors': total_tutors,
        'pending_tutors': pending_tutors,
        'verified_tutors_30d': verified_tutors_30d,
        
        # Booking metrics
        'total_bookings': total_bookings,
        'bookings_30d': bookings_30d,
        'bookings_7d': bookings_7d,
        'completed_bookings': completed_bookings,
        'conversion_rate': conversion_rate,
        
        # Revenue metrics
        'total_revenue': total_revenue,
        'revenue_30d': revenue_30d,
        'revenue_7d': revenue_7d,
        'total_commission': total_commission,
        'commission_30d': commission_30d,
        
        # Review metrics
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        
        # Trends
        'booking_trends': list(booking_trends),
        'revenue_trends': list(revenue_trends),
        'top_subjects': list(top_subjects),
        'top_tutors': list(top_tutors),
    }
    return render(request, 'analytics/dashboard.jinja', context)


@login_required
def revenue_forecast(request):
    """Revenue forecasting"""
    if not request.user.is_global_admin():
        messages.error(request, 'Access denied. Global Admin access required.')
        return redirect('/')
    
    # Simple forecasting based on recent trends
    from payments.models import Payment
    from datetime import date
    
    # Get last 30 days revenue
    last_30_days = date.today() - timedelta(days=30)
    recent_revenue = Payment.objects.filter(
        status='completed',
        created_at__gte=last_30_days
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Simple forecast: average daily revenue * 30
    daily_avg = float(recent_revenue) / 30
    forecast_30d = daily_avg * 30
    
    # Growth assumption (5% monthly growth)
    forecast_with_growth = forecast_30d * 1.05
    
    context = {
        'current_month_revenue': recent_revenue,
        'forecast_30d': forecast_30d,
        'forecast_with_growth': forecast_with_growth,
        'confidence_level': 75,  # Placeholder
    }
    return render(request, 'analytics/revenue_forecast.jinja', context)


@login_required
def custom_report_builder(request):
    """Custom report builder"""
    if not (request.user.is_city_admin() or request.user.is_global_admin()):
        messages.error(request, 'Access denied. Admin access required.')
        return redirect('/')
    
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        format_type = request.POST.get('format', 'html')
        
        # Generate report based on type
        if report_type == 'bookings':
            return generate_bookings_report(request, start_date, end_date, format_type)
        elif report_type == 'revenue':
            return generate_revenue_report(request, start_date, end_date, format_type)
        elif report_type == 'tutors':
            return generate_tutors_report(request, start_date, end_date, format_type)
        elif report_type == 'users':
            return generate_users_report(request, start_date, end_date, format_type)
    
    return render(request, 'analytics/report_builder.jinja')


def generate_bookings_report(request, start_date, end_date, format_type):
    """Generate bookings report"""
    bookings = Booking.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).select_related('student', 'tutor', 'subject')
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="bookings_report_{start_date}_{end_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Student', 'Tutor', 'Subject', 'Date', 'Time', 'Status', 'Amount'])
        
        for booking in bookings:
            writer.writerow([
                booking.id,
                booking.student.username,
                booking.tutor.username,
                booking.subject.name,
                booking.lesson_date,
                booking.lesson_time,
                booking.status,
                booking.total_amount
            ])
        
        return response
    elif format_type == 'json':
        data = [{
            'id': b.id,
            'student': b.student.username,
            'tutor': b.tutor.username,
            'subject': b.subject.name,
            'date': str(b.lesson_date),
            'time': str(b.lesson_time),
            'status': b.status,
            'amount': str(b.total_amount)
        } for b in bookings]
        return JsonResponse(data, safe=False)
    
    # HTML format
    context = {
        'bookings': bookings,
        'start_date': start_date,
        'end_date': end_date,
        'report_type': 'Bookings'
    }
    return render(request, 'analytics/report_template.jinja', context)


def generate_revenue_report(request, start_date, end_date, format_type):
    """Generate revenue report"""
    payments = Payment.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status='completed'
    ).select_related('booking', 'student', 'tutor')
    
    total_revenue = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    total_commission = Commission.objects.filter(
        payment__in=payments
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="revenue_report_{start_date}_{end_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Date', 'Student', 'Tutor', 'Amount', 'Commission', 'Status'])
        
        for payment in payments:
            commission = Commission.objects.filter(payment=payment).first()
            writer.writerow([
                payment.id,
                payment.created_at.date(),
                payment.student.username,
                payment.tutor.username,
                payment.amount,
                commission.amount if commission else 0,
                payment.status
            ])
        
        writer.writerow([])
        writer.writerow(['Total Revenue', total_revenue])
        writer.writerow(['Total Commission', total_commission])
        
        return response
    elif format_type == 'json':
        data = {
            'payments': [{
                'id': p.id,
                'date': str(p.created_at.date()),
                'student': p.student.username,
                'tutor': p.tutor.username,
                'amount': str(p.amount),
                'status': p.status
            } for p in payments],
            'summary': {
                'total_revenue': str(total_revenue),
                'total_commission': str(total_commission)
            }
        }
        return JsonResponse(data, safe=False)
    
    # HTML format
    context = {
        'payments': payments,
        'total_revenue': total_revenue,
        'total_commission': total_commission,
        'start_date': start_date,
        'end_date': end_date,
        'report_type': 'Revenue'
    }
    return render(request, 'analytics/report_template.jinja', context)


def generate_tutors_report(request, start_date, end_date, format_type):
    """Generate tutors report"""
    tutors = TutorProfile.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).select_related('user')
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="tutors_report_{start_date}_{end_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Username', 'Email', 'City', 'State', 'Rating', 'Reviews', 'Status'])
        
        for tutor in tutors:
            writer.writerow([
                tutor.id,
                tutor.user.username,
                tutor.user.email,
                tutor.city,
                tutor.state,
                tutor.average_rating,
                tutor.total_reviews,
                tutor.verification_status
            ])
        
        return response
    elif format_type == 'json':
        data = [{
            'id': t.id,
            'username': t.user.username,
            'email': t.user.email,
            'city': t.city,
            'state': t.state,
            'rating': str(t.average_rating),
            'reviews': t.total_reviews,
            'status': t.verification_status
        } for t in tutors]
        return JsonResponse(data, safe=False)
    
    # HTML format
    context = {
        'tutors': tutors,
        'start_date': start_date,
        'end_date': end_date,
        'report_type': 'Tutors'
    }
    return render(request, 'analytics/report_template.jinja', context)


def generate_users_report(request, start_date, end_date, format_type):
    """Generate users report"""
    users = User.objects.filter(
        date_joined__date__gte=start_date,
        date_joined__date__lte=end_date
    )
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="users_report_{start_date}_{end_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Username', 'Email', 'Role', 'Date Joined', 'Is Active'])
        
        for user in users:
            writer.writerow([
                user.id,
                user.username,
                user.email,
                user.role,
                user.date_joined.date(),
                user.is_active
            ])
        
        return response
    elif format_type == 'json':
        data = [{
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'role': u.role,
            'date_joined': str(u.date_joined.date()),
            'is_active': u.is_active
        } for u in users]
        return JsonResponse(data, safe=False)
    
    # HTML format
    context = {
        'users': users,
        'start_date': start_date,
        'end_date': end_date,
        'report_type': 'Users'
    }
    return render(request, 'analytics/report_template.jinja', context)
