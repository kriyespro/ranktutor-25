import math
from django.db.models import Q, Avg, Count, F
from django.conf import settings


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    if not all([lat1, lon1, lat2, lon2]):
        return None
    
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r


def filter_tutors_by_proximity(tutors, user_lat, user_lon, max_distance_km=10):
    """
    Filter tutors by proximity to user location
    Returns tutors within max_distance_km
    """
    if not user_lat or not user_lon:
        return tutors
    
    nearby_tutors = []
    for tutor in tutors:
        if tutor.latitude and tutor.longitude:
            distance = calculate_distance(
                user_lat, user_lon,
                float(tutor.latitude), float(tutor.longitude)
            )
            if distance and distance <= max_distance_km:
                tutor.distance = distance
                nearby_tutors.append(tutor)
    
    return nearby_tutors


def calculate_match_score(tutor_profile, student_profile, preferences=None):
    """
    Calculate AI matchmaking score between tutor and student
    Returns a score from 0-100
    """
    score = 0
    max_score = 100
    
    # Subject match (30 points)
    if student_profile.preferred_subjects.exists():
        common_subjects = tutor_profile.subjects.filter(
            id__in=student_profile.preferred_subjects.values_list('id', flat=True)
        ).count()
        total_preferred = student_profile.preferred_subjects.count()
        if total_preferred > 0:
            score += (common_subjects / total_preferred) * 30
    
    # Level match (20 points)
    if student_profile.grade_level:
        tutor_levels = tutor_profile.teaching_levels
        if tutor_levels == 'all' or student_profile.grade_level in tutor_levels:
            score += 20
    
    # Mode preference (15 points)
    if student_profile.preferred_mode:
        if student_profile.preferred_mode == 'both':
            score += 15
        elif student_profile.preferred_mode == 'online' and tutor_profile.is_available_online:
            score += 15
        elif student_profile.preferred_mode == 'home' and tutor_profile.is_available_home:
            score += 15
    
    # Rating (20 points)
    if tutor_profile.average_rating:
        score += (float(tutor_profile.average_rating) / 5.0) * 20
    
    # Verification status (10 points)
    if tutor_profile.is_verified:
        score += 10
    
    # Experience (5 points)
    if tutor_profile.years_of_experience >= 3:
        score += 5
    
    return min(score, max_score)


def get_ai_recommendations(student_profile, limit=10):
    """
    Get AI-powered tutor recommendations for a student
    """
    from .models import TutorProfile
    
    # Get all verified tutors
    tutors = TutorProfile.objects.filter(
        is_verified=True,
        verification_status='approved'
    )
    
    # Filter by preferred subjects
    if student_profile.preferred_subjects.exists():
        tutors = tutors.filter(subjects__in=student_profile.preferred_subjects.all()).distinct()
    
    # Filter by mode
    if student_profile.preferred_mode == 'online':
        tutors = tutors.filter(is_available_online=True)
    elif student_profile.preferred_mode == 'home':
        tutors = tutors.filter(is_available_home=True)
    
    # Calculate match scores
    scored_tutors = []
    for tutor in tutors:
        match_score = calculate_match_score(tutor, student_profile)
        scored_tutors.append((tutor, match_score))
    
    # Sort by match score (descending)
    scored_tutors.sort(key=lambda x: x[1], reverse=True)
    
    # Return top recommendations
    return [tutor for tutor, score in scored_tutors[:limit]]
