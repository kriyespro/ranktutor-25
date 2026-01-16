from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Avg, Count
from datetime import timedelta
from decimal import Decimal
from .models import TutorProfile, TutorDocument, PricingOption, Subject, PremiumSubscription
from .forms import PricingOptionForm, TutorDocumentForm
from .utils import filter_tutors_by_proximity, calculate_distance, calculate_match_score
from bookings.models import Booking, AvailabilitySlot
from payments.models import PremiumPayment, Payment
from reviews.models import Dispute, Review
from messaging.models import Message, Conversation


@login_required
def tutor_dashboard(request):
    """Tutor dashboard"""
    if not request.user.is_tutor():
        messages.error(request, 'Access denied. Tutor access required.')
        # Redirect to appropriate dashboard based on role
        if request.user.is_student() or request.user.is_parent():
            return redirect('students:dashboard')
        elif request.user.is_city_admin():
            return redirect('admin_panel:city_dashboard')
        elif request.user.is_global_admin():
            return redirect('admin_panel:global_dashboard')
        return redirect('/')
    
    tutor_profile, created = TutorProfile.objects.get_or_create(user=request.user)
    
    # Get statistics
    total_bookings = Booking.objects.filter(tutor=request.user).count()
    pending_bookings_count = Booking.objects.filter(tutor=request.user, status='pending').count()
    
    # Get actual pending bookings list (most recent first)
    pending_bookings = Booking.objects.filter(
        tutor=request.user,
        status='pending'
    ).order_by('-created_at')[:10]
    
    # Get upcoming accepted bookings
    upcoming_bookings = Booking.objects.filter(
        tutor=request.user,
        status='accepted',
        lesson_date__gte=timezone.now().date()
    ).order_by('lesson_date', 'lesson_time')[:5]
    
    # Get all disputes related to tutor's bookings
    tutor_disputes = Dispute.objects.filter(
        booking__tutor=request.user
    ).order_by('-created_at')[:10]
    
    # Check premium status
    is_premium_boosted = tutor_profile.is_premium_boosted()
    active_subscriptions = PremiumSubscription.objects.filter(
        tutor=tutor_profile,
        is_active=True,
        end_date__gte=timezone.now()
    )
    
    # Calculate profile completion percentage
    profile_fields = {
        'headline': tutor_profile.headline,
        'bio': tutor_profile.bio,
        'city': tutor_profile.city,
        'subjects': tutor_profile.subjects.exists(),
        'hourly_rate': tutor_profile.hourly_rate,
        'education': tutor_profile.education,
        'years_of_experience': tutor_profile.years_of_experience,
    }
    completed_fields = sum(1 for v in profile_fields.values() if v)
    total_fields = len(profile_fields)
    profile_completion = int((completed_fields / total_fields) * 100) if total_fields > 0 else 0
    
    # Class per day chart data (last 7 days) - SQLite compatible
    from django.db.models import Count
    from collections import defaultdict
    last_7_days = timezone.now() - timedelta(days=7)
    classes_per_day_qs = Booking.objects.filter(
        tutor=request.user,
        status='accepted',
        lesson_date__gte=last_7_days.date()
    ).values('lesson_date').annotate(
        count=Count('id')
    ).order_by('lesson_date')
    
    # Prepare chart data - group by date
    class_data_dict = defaultdict(int)
    for item in classes_per_day_qs:
        date_str = item['lesson_date'].strftime('%Y-%m-%d')
        class_data_dict[date_str] = item['count']
    
    # Fill in all 7 days
    from datetime import date
    today = timezone.now().date()
    class_dates = []
    class_counts = []
    for i in range(7):
        day = today - timedelta(days=6-i)
        day_str = day.strftime('%Y-%m-%d')
        class_dates.append(day.strftime('%b %d'))
        class_counts.append(class_data_dict.get(day_str, 0))
    
    # Weekly earnings (last 4 weeks) - use paid_at for completed payments
    from django.db.models import Sum, Q
    weekly_earnings = []
    now = timezone.now()
    
    # Get all completed payments for this tutor with paid_at or created_at
    all_completed_payments = list(Payment.objects.filter(
        tutor=request.user,
        status='completed'
    ).select_related('booking'))
    
    # Calculate 4 weeks of data (most recent week first)
    for week_num in range(4):
        # Week 0 = current week (last 7 days)
        # Week 1 = 7-14 days ago
        # Week 2 = 14-21 days ago  
        # Week 3 = 21-28 days ago
        days_ago_start = (week_num + 1) * 7
        days_ago_end = week_num * 7
        
        week_start = now - timedelta(days=days_ago_start)
        week_end = now - timedelta(days=days_ago_end) if week_num > 0 else now
        
        # Calculate total for this week
        week_total = 0.0
        for payment in all_completed_payments:
            # Use paid_at if available, otherwise use created_at
            payment_date = payment.paid_at if payment.paid_at else payment.created_at
            if payment_date:
                # Ensure timezone-aware comparison
                if hasattr(payment_date, 'tzinfo') and payment_date.tzinfo is None:
                    payment_date = timezone.make_aware(payment_date)
                elif hasattr(week_start, 'tzinfo') and week_start.tzinfo is None:
                    week_start = timezone.make_aware(week_start)
                    week_end = timezone.make_aware(week_end)
                
                if week_start <= payment_date <= week_end:
                    week_total += float(payment.tutor_payout)
        
        weekly_earnings.insert(0, week_total)
    
    # Monthly earnings (last 6 months) - SQLite compatible
    from collections import defaultdict
    
    # Get all completed payments
    all_payments = Payment.objects.filter(
        tutor=request.user,
        status='completed'
    )
    
    # Group by month in Python - use paid_at for completed payments, fallback to created_at
    monthly_data = defaultdict(float)
    for payment in all_payments:
        # Use paid_at if available (when payment was actually completed), otherwise use created_at
        payment_date = payment.paid_at if payment.paid_at else payment.created_at
        # Convert to date if datetime
        if hasattr(payment_date, 'date') and callable(getattr(payment_date, 'date', None)):
            payment_date = payment_date.date()
        
        month_key = payment_date.strftime('%Y-%m')
        monthly_data[month_key] += float(payment.tutor_payout)
    
    # Get last 6 months (current month + 5 previous) - proper month calculation
    monthly_labels = []
    monthly_amounts = []
    from datetime import date
    current = timezone.now()
    current_date = current.date() if hasattr(current, 'date') else date.today()
    
    for i in range(5, -1, -1):  # 5 months ago to current month
        # Calculate month properly
        year = current_date.year
        month = current_date.month - i
        while month <= 0:
            month += 12
            year -= 1
        month_date = date(year, month, 1)
        
        month_key = month_date.strftime('%Y-%m')
        monthly_labels.append(month_date.strftime('%b %Y'))
        monthly_amounts.append(float(monthly_data.get(month_key, 0)))
    
    # Recent bookings for column
    recent_bookings = Booking.objects.filter(
        tutor=request.user
    ).order_by('-created_at')[:5]
    
    # Recent payments for column
    recent_payments = Payment.objects.filter(
        tutor=request.user,
        status='completed'
    ).order_by('-created_at')[:5]
    
    # Recent messages for column
    conversations = Conversation.objects.filter(
        Q(participant1=request.user) | Q(participant2=request.user)
    )
    recent_messages = Message.objects.filter(
        conversation__in=conversations
    ).exclude(sender=request.user).order_by('-created_at')[:5]
    
    # Student statistics
    from reviews.models import Review
    all_students = Booking.objects.filter(tutor=request.user).values('student').distinct()
    total_students = all_students.count()
    
    # New students monthly (last 6 months) - proper month calculation
    new_students_monthly = []
    students_monthly_labels = []
    from datetime import date, datetime
    
    current = timezone.now()
    current_date = current.date() if hasattr(current, 'date') else date.today()
    
    for i in range(5, -1, -1):  # Last 6 months
        # Calculate month start and end properly
        year = current_date.year
        month = current_date.month - i
        while month <= 0:
            month += 12
            year -= 1
        
        month_start = date(year, month, 1)
        if i == 0:
            month_end = current_date
        else:
            # Get last day of month
            if month == 12:
                month_end = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(year, month + 1, 1) - timedelta(days=1)
        
        # Convert to datetime for query
        month_start_dt = timezone.make_aware(datetime.combine(month_start, datetime.min.time()))
        month_end_dt = timezone.make_aware(datetime.combine(month_end, datetime.max.time()))
        
        month_new = Booking.objects.filter(
            tutor=request.user,
            created_at__gte=month_start_dt,
            created_at__lte=month_end_dt
        ).values('student').distinct().count()
        
        new_students_monthly.append(month_new)
        students_monthly_labels.append(month_start.strftime('%b %Y'))
    
    # Rating data (last 6 months) - properly grouped by month
    rating_data = defaultdict(list)
    reviews = Review.objects.filter(tutor=request.user).order_by('created_at')
    for review in reviews:
        # Use the actual created_at date
        review_date = review.created_at
        if hasattr(review_date, 'date'):
            review_date = review_date.date()
        month_key = review_date.strftime('%Y-%m')
        rating_data[month_key].append(review.rating)
    
    # Calculate average rating per month (last 6 months) - proper month calculation
    rating_labels = []
    rating_averages = []
    from datetime import date
    
    current = timezone.now()
    current_date = current.date() if hasattr(current, 'date') else date.today()
    
    for i in range(5, -1, -1):
        # Calculate month properly
        year = current_date.year
        month = current_date.month - i
        while month <= 0:
            month += 12
            year -= 1
        month_date = date(year, month, 1)
        
        month_key = month_date.strftime('%Y-%m')
        month_label = month_date.strftime('%b %Y')
        ratings = rating_data.get(month_key, [])
        # If no ratings for this month, use previous month's average or 0
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
        else:
            # Try to get the last known rating average
            if rating_averages:
                avg_rating = rating_averages[-1] if rating_averages else 0
            else:
                avg_rating = 0
        rating_labels.append(month_label)
        rating_averages.append(round(avg_rating, 1))
    
    # Current average rating
    current_avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    
    # Calculate earnings for dashboard
    # Total earning this week (current week - weekly_earnings[0])
    earnings_this_week = weekly_earnings[0] if weekly_earnings else 0.0
    
    # Total earning this month (current month - last item in monthly_amounts)
    earnings_this_month = monthly_amounts[-1] if monthly_amounts else 0.0
    
    # Total earning till now (sum of all completed payments)
    total_earnings = sum(float(payment.tutor_payout) for payment in all_completed_payments)
    
    context = {
        'tutor_profile': tutor_profile,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'pending_bookings_count': pending_bookings_count,
        'upcoming_bookings': upcoming_bookings,
        'tutor_disputes': tutor_disputes,
        'is_premium_boosted': is_premium_boosted,
        'active_subscriptions': active_subscriptions,
        'profile_completion': profile_completion,
        'class_dates': class_dates,
        'class_counts': class_counts,
        'weekly_earnings': weekly_earnings,
        'monthly_labels': monthly_labels,
        'monthly_amounts': monthly_amounts,
        'recent_bookings': recent_bookings,
        'recent_payments': recent_payments,
        'recent_messages': recent_messages,
        'total_students': total_students,
        'new_students_monthly': new_students_monthly,
        'students_monthly_labels': students_monthly_labels,
        'rating_labels': rating_labels,
        'rating_averages': rating_averages,
        'current_avg_rating': round(current_avg_rating, 1),
        'earnings_this_week': earnings_this_week,
        'earnings_this_month': earnings_this_month,
        'total_earnings': total_earnings,
    }
    return render(request, 'tutors/dashboard.jinja', context)


@login_required
def tutor_profile_builder(request):
    """Tutor profile builder - guided form"""
    if not request.user.is_tutor():
        messages.error(request, 'Access denied. Tutor access required.')
        return redirect('/')
    
    tutor_profile, created = TutorProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update basic info
        tutor_profile.headline = request.POST.get('headline', '')
        tutor_profile.bio = request.POST.get('bio', '')
        tutor_profile.education = request.POST.get('education', '')
        tutor_profile.experience_summary = request.POST.get('experience_summary', '')
        tutor_profile.teaching_style = request.POST.get('teaching_style', '')
        tutor_profile.achievements = request.POST.get('achievements', '')
        tutor_profile.languages = request.POST.get('languages', '')
        tutor_profile.city = request.POST.get('city', '')
        tutor_profile.state = request.POST.get('state', '')
        tutor_profile.pincode = request.POST.get('pincode', '')
        tutor_profile.service_areas = request.POST.get('service_areas', '')
        tutor_profile.is_available_online = request.POST.get('is_available_online') == 'on'
        tutor_profile.is_available_home = request.POST.get('is_available_home') == 'on'
        tutor_profile.teaching_levels = request.POST.get('teaching_levels', 'all')
        
        # Update geolocation
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        if latitude and longitude:
            try:
                tutor_profile.latitude = float(latitude)
                tutor_profile.longitude = float(longitude)
            except (ValueError, TypeError):
                pass
        
        # Update max travel distance
        max_travel = request.POST.get('max_travel_distance')
        if max_travel:
            try:
                tutor_profile.max_travel_distance = int(max_travel)
            except (ValueError, TypeError):
                pass
        
        # Update professional credentials
        years_exp = request.POST.get('years_of_experience')
        if years_exp:
            try:
                tutor_profile.years_of_experience = int(years_exp)
            except (ValueError, TypeError):
                pass
        
        hourly_rate = request.POST.get('hourly_rate')
        if hourly_rate:
            try:
                tutor_profile.hourly_rate = float(hourly_rate)
            except (ValueError, TypeError):
                tutor_profile.hourly_rate = None

        tutor_profile.certifications = request.POST.get('certifications', '')
        # Portfolio URL removed - not saving anymore
        
        tutor_profile.save()
        
        # Update subjects
        subject_ids = request.POST.getlist('subjects')
        tutor_profile.subjects.set(Subject.objects.filter(id__in=subject_ids))
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('tutors:dashboard')
    
    subjects = Subject.objects.all()
    selected_subjects = list(tutor_profile.subjects.all())
    teaching_level_choices = TutorProfile._meta.get_field('teaching_levels').choices
    
    # Sync onboarding data if available
    try:
        from onboarding.models import OnboardingData
        onboarding_data = OnboardingData.objects.filter(user=request.user).first()
        
        if onboarding_data:
            # Pre-populate subjects from onboarding
            if onboarding_data.subjects and not selected_subjects:
                # Try to match onboarding subjects with Subject model
                onboarding_subject_names = onboarding_data.subjects
                matched_subjects = []
                for subject_name in onboarding_subject_names:
                    # Try exact match first
                    subject = Subject.objects.filter(name__iexact=subject_name.strip()).first()
                    if subject:
                        matched_subjects.append(subject)
                    else:
                        # Try partial match
                        subject = Subject.objects.filter(name__icontains=subject_name.strip()).first()
                        if subject:
                            matched_subjects.append(subject)
                
                if matched_subjects:
                    tutor_profile.subjects.set(matched_subjects)
                    selected_subjects = matched_subjects
            
            # Pre-populate hourly rate from onboarding per_class_fees
            if onboarding_data.per_class_fees and not tutor_profile.hourly_rate:
                tutor_profile.hourly_rate = onboarding_data.per_class_fees
                tutor_profile.save()
            
            # Pre-populate city if not set
            if onboarding_data.city and not tutor_profile.city:
                tutor_profile.city = onboarding_data.city
                tutor_profile.save()
    except Exception:
        pass
    
    context = {
        'tutor_profile': tutor_profile,
        'subjects': subjects,
        'selected_subjects': selected_subjects,
        'teaching_level_choices': teaching_level_choices,
    }
    return render(request, 'tutors/profile_builder.jinja', context)


def tutor_search(request):
    """Search for tutors with geolocation support"""
    tutors = TutorProfile.objects.filter(
        is_verified=True, 
        verification_status='approved'
    ).select_related('user').prefetch_related('subjects', 'premium_subscriptions')
    
    # Filters
    subject = request.GET.get('subject')
    city = request.GET.get('city')
    mode = request.GET.get('mode')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    min_rating = request.GET.get('min_rating')
    class_level = request.GET.get('class_level')
    location = request.GET.get('location')
    featured_param = request.GET.get('featured')
    featured_only = featured_param in ('on', '1', 'true', 'True')
    
    # Premium boost: Show featured tutors first
    if featured_only:
        tutors = tutors.filter(is_featured=True)
    
    if subject:
        tutors = tutors.filter(subjects__id=subject)
    if city:
        tutors = tutors.filter(city__icontains=city)
    if location:
        tutors = tutors.filter(
            Q(city__icontains=location) | 
            Q(state__icontains=location) | 
            Q(service_areas__icontains=location)
        )
    if mode == 'online':
        tutors = tutors.filter(is_available_online=True)
    elif mode == 'home':
        tutors = tutors.filter(is_available_home=True)
        # For home tutoring, filter by proximity if location provided
        user_lat = request.GET.get('lat')
        user_lon = request.GET.get('lon')
        max_distance = request.GET.get('max_distance', 10)
        if user_lat and user_lon:
            try:
                tutors = filter_tutors_by_proximity(
                    tutors,
                    float(user_lat),
                    float(user_lon),
                    float(max_distance)
                )
            except (ValueError, TypeError):
                pass
    
    # Price filters
    if min_price:
        try:
            tutors = tutors.filter(hourly_rate__gte=Decimal(min_price))
        except (ValueError, TypeError):
            pass
    if max_price:
        try:
            tutors = tutors.filter(hourly_rate__lte=Decimal(max_price))
        except (ValueError, TypeError):
            pass
    
    # Rating filter
    if min_rating:
        try:
            min_rating_decimal = Decimal(min_rating)
            tutors = tutors.filter(average_rating__gte=min_rating_decimal)
        except (ValueError, TypeError):
            pass
    
    # Class level filter
    if class_level:
        if class_level == 'all':
            pass  # Show all
        else:
            tutors = tutors.filter(teaching_levels=class_level)
    
    # Annotate with average rating (reviews_received is on User, not TutorProfile)
    tutors = tutors.annotate(avg_rating=Avg('user__reviews_received__rating'))
    
    # Sort: Premium Package first, then Featured, then Boost, then by rating
    tutors_list = list(tutors)
    
    # AI matchmaking if user is logged in and has student profile
    # Calculate match scores first, then combine with premium status
    if request.user.is_authenticated and hasattr(request.user, 'student_profile'):
        student_profile = request.user.student_profile
        # Calculate match scores
        scored_tutors = []
        for tutor in tutors_list:
            match_score = calculate_match_score(tutor, student_profile)
            scored_tutors.append((tutor, match_score))
        
        # Sort by premium status first, then match score
        scored_tutors.sort(key=lambda x: (
            not x[0].has_premium_package(),  # Premium package first
            not (x[0].is_featured or x[0].has_featured_subscription()),  # Featured next
            not x[0].is_premium_boosted(),  # Boost next
            -x[1],  # Then by match score (higher is better)
            -float(x[0].average_rating or 0),  # Then by rating
            float(x[0].hourly_rate or 999999)  # Then by price
        ))
        tutors_list = [tutor for tutor, score in scored_tutors]
    else:
        # Sort: Premium Package first, then Featured, then Boost, then by rating
        tutors_list.sort(key=lambda t: (
            not t.has_premium_package(),  # Premium package first (False sorts before True)
            not (t.is_featured or t.has_featured_subscription()),  # Featured next
            not t.is_premium_boosted(),  # Boost next
            -float(t.average_rating or 0),  # Then by rating
            float(t.hourly_rate or 999999)  # Then by price
        ))
    
    subjects = Subject.objects.all()
    context = {
        'tutors': tutors_list,
        'subjects': subjects,
        'user_lat': request.GET.get('lat'),
        'user_lon': request.GET.get('lon'),
    }
    return render(request, 'tutors/search.jinja', context)


def tutor_detail(request, tutor_id):
    """Tutor profile detail page"""
    tutor_profile = get_object_or_404(TutorProfile, id=tutor_id, is_verified=True)
    
    # Get pricing options
    pricing_options = PricingOption.objects.filter(tutor=tutor_profile, is_active=True)
    
    # Get reviews
    from reviews.models import Review
    reviews = Review.objects.filter(tutor=tutor_profile.user, is_approved=True).order_by('-created_at')[:10]
    
    # Calculate match score if user is a student
    match_score = None
    if request.user.is_authenticated and hasattr(request.user, 'student_profile'):
        match_score = calculate_match_score(tutor_profile, request.user.student_profile)
    
    context = {
        'tutor_profile': tutor_profile,
        'pricing_options': pricing_options,
        'reviews': reviews,
        'match_score': match_score,
    }
    return render(request, 'tutors/detail.jinja', context)


@login_required
def manage_pricing(request):
    """Manage pricing options"""
    if not request.user.is_tutor():
        messages.error(request, 'Access denied. Tutor access required.')
        return redirect('/')
    
    tutor_profile = get_object_or_404(TutorProfile, user=request.user)
    
    if request.method == 'POST':
        form = PricingOptionForm(request.POST)
        if form.is_valid():
            pricing = form.save(commit=False)
            pricing.tutor = tutor_profile
            pricing.save()
            messages.success(request, 'Pricing option added successfully!')
            return redirect('tutors:manage_pricing')
    else:
        form = PricingOptionForm()
    
    pricing_options = PricingOption.objects.filter(tutor=tutor_profile)
    subjects = Subject.objects.all()
    
    context = {
        'form': form,
        'pricing_options': pricing_options,
        'subjects': subjects,
    }
    return render(request, 'tutors/manage_pricing.jinja', context)


@login_required
def upload_documents(request):
    """Upload verification documents"""
    if not request.user.is_tutor():
        messages.error(request, 'Access denied. Tutor access required.')
        return redirect('/')
    
    tutor_profile = get_object_or_404(TutorProfile, user=request.user)
    
    if request.method == 'POST':
        form = TutorDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.tutor = tutor_profile
            document.save()
            messages.success(request, 'Document uploaded successfully! It will be reviewed by admin.')
            return redirect('tutors:upload_documents')
    else:
        form = TutorDocumentForm()
    
    documents = TutorDocument.objects.filter(tutor=tutor_profile).order_by('-created_at')
    
    context = {
        'form': form,
        'documents': documents,
    }
    return render(request, 'tutors/upload_documents.jinja', context)


@login_required
def premium_features(request):
    """Premium features page for tutors"""
    if not request.user.is_tutor():
        messages.error(request, 'Access denied. Tutor access required.')
        return redirect('/')
    
    tutor_profile = get_object_or_404(TutorProfile, user=request.user)
    
    if request.method == 'POST':
        feature_type = request.POST.get('feature_type')
        duration_days = int(request.POST.get('duration_days', 30))
        
        # Pricing
        pricing = {
            'boost': 299,  # ₹299 for 30 days
            'featured': 999,  # ₹999 for 30 days
            'premium': 1999,  # ₹1999 for 30 days
        }
        
        amount = pricing.get(feature_type, 0)
        
        if not amount:
            messages.error(request, 'Invalid feature type selected.')
            return redirect('tutors:premium_features')
        
        # Create premium payment (pending)
        premium_payment = PremiumPayment.objects.create(
            user=request.user,
            payment_type=feature_type,
            amount=amount,
            status='pending'
        )
        
        # Redirect to payment processing page
        return redirect('tutors:process_premium_payment', payment_id=premium_payment.id)
    
    # Get active subscriptions
    active_subscriptions = PremiumSubscription.objects.filter(
        tutor=tutor_profile,
        is_active=True,
        end_date__gte=timezone.now()
    )
    
    context = {
        'tutor_profile': tutor_profile,
        'active_subscriptions': active_subscriptions,
        'is_premium_boosted': tutor_profile.is_premium_boosted(),
    }
    return render(request, 'tutors/premium_features.jinja', context)


@login_required
def process_premium_payment(request, payment_id):
    """Process premium payment - dummy payment page"""
    if not request.user.is_tutor():
        messages.error(request, 'Access denied. Tutor access required.')
        return redirect('/')
    
    premium_payment = get_object_or_404(PremiumPayment, id=payment_id, user=request.user)
    
    if premium_payment.status == 'completed':
        messages.info(request, 'This payment has already been processed.')
        return redirect('tutors:premium_features')
    
    tutor_profile = get_object_or_404(TutorProfile, user=request.user)
    
    if request.method == 'POST':
        # Simulate payment success (dummy payment)
        action = request.POST.get('action')
        
        if action == 'confirm':
            # Mark payment as completed
            premium_payment.status = 'completed'
            premium_payment.transaction_id = f'PREMIUM_{premium_payment.id}_{timezone.now().strftime("%Y%m%d%H%M%S")}'
            premium_payment.save()
            
            feature_type = premium_payment.payment_type
            duration_days = 30  # Default 30 days
            
            # Activate premium feature
            if feature_type == 'boost':
                tutor_profile.premium_boost_until = timezone.now() + timedelta(days=duration_days)
                tutor_profile.boost_count += 1
                tutor_profile.save()
            elif feature_type == 'featured':
                tutor_profile.is_featured = True
                tutor_profile.premium_boost_until = timezone.now() + timedelta(days=duration_days)
                tutor_profile.save()
            elif feature_type == 'premium':
                # Premium package includes featured + additional benefits
                tutor_profile.is_featured = True
                tutor_profile.premium_boost_until = timezone.now() + timedelta(days=duration_days)
                tutor_profile.save()
            
            # Create subscription record
            PremiumSubscription.objects.create(
                tutor=tutor_profile,
                subscription_type=feature_type,
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=duration_days),
                amount_paid=premium_payment.amount,
                is_active=True
            )
            
            messages.success(request, f'Premium {premium_payment.get_payment_type_display()} activated for {duration_days} days!')
            return redirect('tutors:premium_features')
        elif action == 'cancel':
            premium_payment.status = 'failed'
            premium_payment.save()
            messages.info(request, 'Payment cancelled.')
            return redirect('tutors:premium_features')
    
    # Payment types display names
    feature_names = {
        'boost': 'Profile Boost',
        'featured': 'Featured Listing',
        'premium': 'Premium Package',
    }
    
    context = {
        'premium_payment': premium_payment,
        'tutor_profile': tutor_profile,
        'feature_name': feature_names.get(premium_payment.payment_type, 'Premium Feature'),
    }
    return render(request, 'tutors/process_premium_payment.jinja', context)


def become_tutor(request):
    """Become a tutor page - information and signup"""
    return render(request, 'tutors/become_tutor.jinja')


def tutor_resources(request):
    """Tutor resources page"""
    return render(request, 'tutors/resources.jinja')


@login_required
def tutor_disputes(request):
    """Tutor disputes page"""
    if not request.user.is_tutor():
        messages.error(request, 'Access denied. Tutor access required.')
        return redirect('/')
    
    # Get all disputes related to tutor's bookings
    disputes = Dispute.objects.filter(
        booking__tutor=request.user
    ).order_by('-created_at')
    
    # Count by status
    disputes_count = {
        'open': disputes.filter(status='open').count(),
        'under_review': disputes.filter(status='under_review').count(),
        'resolved': disputes.filter(status='resolved').count(),
        'closed': disputes.filter(status='closed').count(),
    }
    
    context = {
        'disputes': disputes,
        'disputes_count': disputes_count,
    }
    return render(request, 'tutors/disputes.jinja', context)
