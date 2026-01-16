from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import User, UserProfile


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            # Auto-login user after registration
            login(request, user)
            messages.success(request, 'Registration successful!')
            # Redirect to onboarding
            return redirect('onboarding:check')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.jinja', {'form': form})


def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        user = request.user
        
        # Skip onboarding check for admins - they're always existing users
        if user.role in ['city_admin', 'global_admin']:
            # Redirect admins directly to their dashboard
            if user.is_city_admin():
                return redirect('admin_panel:city_dashboard')
            elif user.is_global_admin():
                return redirect('admin_panel:global_dashboard')
            return redirect('/')
        
        # Check onboarding for non-admin users only
        try:
            from onboarding.models import OnboardingStatus
            status, created = OnboardingStatus.objects.get_or_create(user=user)
            if not status.onboarding_completed:
                # Check if this is an old user (created more than 30 days ago with non-default role)
                from django.utils import timezone
                from datetime import timedelta
                days_ago_30 = timezone.now() - timedelta(days=30)
                date_joined = user.date_joined
                if timezone.is_naive(date_joined):
                    date_joined = timezone.make_aware(date_joined)
                
                # If old user with non-default role, mark onboarding as complete
                if date_joined < days_ago_30 and user.role != 'student':
                    status.onboarding_completed = True
                    status.save()
                elif not status.onboarding_completed:
                    return redirect('onboarding:check')
        except Exception:
            pass
        
        # Redirect authenticated users to their appropriate dashboard
        if user.is_tutor():
            return redirect('tutors:dashboard')
        elif user.is_student() or user.is_parent():
            return redirect('students:dashboard')
        elif user.is_city_admin():
            return redirect('admin_panel:city_dashboard')
        elif user.is_global_admin():
            return redirect('admin_panel:global_dashboard')
        return redirect('/')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            # Check for 'next' parameter first
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                # Validate that next_url is safe and belongs to user's role
                if user.is_tutor() and next_url.startswith('/tutors/'):
                    return redirect(next_url)
                elif (user.is_student() or user.is_parent()) and next_url.startswith('/students/'):
                    return redirect(next_url)
                elif user.is_city_admin() and next_url.startswith('/admin/city/'):
                    return redirect(next_url)
                elif user.is_global_admin() and next_url.startswith('/admin/'):
                    return redirect(next_url)
            
            # Check onboarding first
            try:
                from onboarding.models import OnboardingStatus
                status, created = OnboardingStatus.objects.get_or_create(user=user)
                if not status.onboarding_completed:
                    return redirect('onboarding:check')
            except Exception:
                pass
            
            # Redirect based on role (use URL names for consistency)
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
    else:
        form = UserLoginForm(request=request)
    
    return render(request, 'users/login.jinja', {'form': form})


@login_required
def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('users:login')


@login_required
def profile(request):
    """User profile view"""
    profile_obj, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=profile_obj)
    
    context = {
        'form': form,
        'user': request.user,
        'profile': profile_obj,
    }
    return render(request, 'users/profile.jinja', context)
