from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import OnboardingStatus, OnboardingData
from .forms import (
    RoleSelectionForm,
    StudentOnboardingForm,
    TutorOnboardingForm,
    CityAdminOnboardingForm
)
from users.models import User


@login_required
def onboarding_check(request):
    """Check if user needs onboarding and redirect accordingly"""
    user = request.user
    
    # Immediately check if user is an admin - admins skip onboarding
    if user.role in ['city_admin', 'global_admin']:
        status, created = OnboardingStatus.objects.get_or_create(user=user)
        if not status.onboarding_completed:
            status.onboarding_completed = True
            status.save()
        return redirect_to_dashboard(user)
    
    status, created = OnboardingStatus.objects.get_or_create(user=user)
    
    # If onboarding is completed, redirect to dashboard
    if status.onboarding_completed:
        return redirect_to_dashboard(user)
    
    # Check if user is an old user (created more than 30 days ago with non-default role)
    days_ago_30 = timezone.now() - timedelta(days=30)
    date_joined = user.date_joined
    if timezone.is_naive(date_joined):
        date_joined = timezone.make_aware(date_joined)
    
    if date_joined < days_ago_30 and user.role != 'student':
        # Old user with non-default role - skip onboarding
        status.onboarding_completed = True
        status.save()
        return redirect_to_dashboard(user)
    
    # Redirect to appropriate step for new users
    if not status.role_selected:
        return redirect('onboarding:role_selection')
    elif not status.basic_info_completed:
        return redirect('onboarding:basic_info')
    
    return redirect_to_dashboard(user)


@login_required
def role_selection(request):
    """Step 1: Role selection - Only show to new users"""
    # Check if user is an old/existing user
    # Old users are those who:
    # 1. Have completed onboarding already
    # 2. Have an admin role (city_admin, global_admin) - these are always existing users
    # 3. Have a non-default role and were created more than 30 days ago
    # 4. Have a TutorProfile, StudentProfile, or other profile indicating they're already set up
    
    user = request.user
    status = None
    try:
        status = OnboardingStatus.objects.get(user=user)
        # If already completed, redirect
        if status.onboarding_completed:
            return redirect_to_dashboard(user)
    except OnboardingStatus.DoesNotExist:
        pass
    
    # Immediately check if user is an admin - admins are always existing users
    if user.role in ['city_admin', 'global_admin']:
        # Mark onboarding as completed for admins if not already
        if status is None:
            status, created = OnboardingStatus.objects.get_or_create(user=user)
        status.onboarding_completed = True
        status.save()
        messages.info(request, 'You are already set up. Welcome back!')
        return redirect_to_dashboard(user)
    
    # Check if user is an old user (created more than 30 days ago and has a non-default role)
    days_ago_30 = timezone.now() - timedelta(days=30)
    is_old_user = False
    
    # Make date_joined timezone-aware if needed
    date_joined = user.date_joined
    if timezone.is_naive(date_joined):
        date_joined = timezone.make_aware(date_joined)
    
    if date_joined < days_ago_30:
        # Check if user has a non-default role or has profiles set up
        if user.role != 'student':
            is_old_user = True
        else:
            # Check if user has tutor or student profile
            from tutors.models import TutorProfile
            from students.models import StudentProfile
            
            try:
                TutorProfile.objects.get(user=user)
                is_old_user = True
            except TutorProfile.DoesNotExist:
                pass
            
            try:
                StudentProfile.objects.get(user=user)
                is_old_user = True
            except StudentProfile.DoesNotExist:
                pass
    
    # If old user, redirect to dashboard
    if is_old_user:
        # Mark onboarding as completed for old users
        if status is None:
            status, created = OnboardingStatus.objects.get_or_create(user=user)
        status.onboarding_completed = True
        status.save()
        messages.info(request, 'You are already set up. Welcome back!')
        return redirect_to_dashboard(user)
    
    # Create status if it doesn't exist
    if status is None:
        status, created = OnboardingStatus.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        form = RoleSelectionForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            # Update user role
            user.role = role
            user.save()
            
            # Update onboarding status
            status.role_selected = True
            status.current_step = 2
            status.save()
            
            # Create onboarding data entry
            OnboardingData.objects.get_or_create(user=user)
            
            messages.success(request, f'Role selected: {dict(User.ROLE_CHOICES)[role]}')
            return redirect('onboarding:basic_info')
    else:
        form = RoleSelectionForm()
    
    return render(request, 'onboarding/role_selection.jinja', {'form': form})


@login_required
def basic_info(request):
    """Step 2: Basic info form based on role"""
    status, created = OnboardingStatus.objects.get_or_create(user=request.user)
    
    # Check if role is selected
    if not status.role_selected:
        return redirect('onboarding:role_selection')
    
    # If already completed, redirect
    if status.onboarding_completed:
        return redirect_to_dashboard(request.user)
    
    user_role = request.user.role
    onboarding_data, created = OnboardingData.objects.get_or_create(user=request.user)
    
    # Select form based on role
    if user_role == 'student':
        FormClass = StudentOnboardingForm
    elif user_role == 'tutor':
        FormClass = TutorOnboardingForm
    elif user_role == 'city_admin':
        FormClass = CityAdminOnboardingForm
    else:
        messages.error(request, 'Invalid role selected.')
        return redirect('onboarding:role_selection')
    
    if request.method == 'POST':
        form = FormClass(request.POST, instance=onboarding_data)
        if form.is_valid():
            form.save()
            
            # Update onboarding status
            status.basic_info_completed = True
            status.onboarding_completed = True
            status.current_step = 3
            status.save()
            
            # Update user profile with city if available
            if hasattr(request.user, 'profile'):
                profile = request.user.profile
                if onboarding_data.city:
                    profile.city = onboarding_data.city
                    profile.save()
            
            messages.success(request, 'Onboarding completed! Welcome to RankTutor!')
            return redirect_to_dashboard(request.user)
    else:
        form = FormClass(instance=onboarding_data)
    
    return render(request, 'onboarding/basic_info.jinja', {
        'form': form,
        'user_role': user_role,
        'role_display': dict(User.ROLE_CHOICES).get(user_role, user_role)
    })


def redirect_to_dashboard(user):
    """Helper function to redirect user to appropriate dashboard"""
    if user.is_tutor():
        return redirect('tutors:dashboard')
    elif user.is_student() or user.is_parent():
        return redirect('students:dashboard')
    elif user.is_city_admin():
        return redirect('admin_panel:city_dashboard')
    elif user.is_global_admin():
        return redirect('admin_panel:global_dashboard')
    else:
        return redirect('/')
