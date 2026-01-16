from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import os

from tutors.models import Subject, TutorProfile


def home(request):
    """Home page"""
    subjects = list(Subject.objects.order_by('name')[:8])
    # Show more featured tutors - prioritize verified and high-rated
    featured_qs = (
        TutorProfile.objects.filter(
            is_verified=True, 
            verification_status='approved',
            is_deleted=False
        )
        .select_related('user')
        .prefetch_related('subjects', 'pricing_options', 'premium_subscriptions')
    )
    
    # Convert to list and add premium status
    tutors_list = list(featured_qs)
    for tutor in tutors_list:
        tutor.subject_names = [subject.name for subject in tutor.subjects.all()][:4]
        tutor.verification_badges = tutor.get_verification_badges()
        full_name = tutor.user.get_full_name() or tutor.user.username
        tutor.display_name = full_name
        initials = ''.join(part[0].upper() for part in full_name.split()[:2])
        tutor.initials = initials if initials else full_name[:2].upper()
        pricing_options = list(tutor.pricing_options.all())
        prices = [float(option.price_per_hour) for option in pricing_options if option.price_per_hour]  # type: ignore[arg-type]
        if not prices and tutor.hourly_rate:
            prices = [float(tutor.hourly_rate)]
        tutor.price_min = min(prices) if prices else None
        tutor.price_max = max(prices) if prices else None
    
    # Sort: Premium Package first, then Featured, then Boost, then by rating
    tutors_list.sort(key=lambda t: (
        not t.has_premium_package(),  # Premium package first (False sorts before True)
        not (t.is_featured or t.has_featured_subscription()),  # Featured next
        not t.is_premium_boosted(),  # Boost next
        -float(t.average_rating or 0),  # Then by rating
        -float(t.quality_score or 0),  # Then by quality score
    ))
    
    featured_tutors = tutors_list[:15]

    context = {
        'subjects': subjects,
        'featured_tutors': featured_tutors,
    }
    return render(request, 'core/home.jinja', context)


def service_worker(request):
    """Service worker for PWA"""
    sw_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR / 'static', 'sw.js')
    if os.path.exists(sw_path):
        with open(sw_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='application/javascript')
    return HttpResponse('', content_type='application/javascript')
