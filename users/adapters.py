from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

User = get_user_model()


def check_onboarding_and_redirect(user):
    """Check if user needs onboarding, return redirect URL or None"""
    try:
        from onboarding.models import OnboardingStatus
        status, created = OnboardingStatus.objects.get_or_create(user=user)
        
        if not status.onboarding_completed:
            return reverse('onboarding:check')
    except Exception:
        # If onboarding app not available, skip check
        pass
    
    return None


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter for social account signup with role selection"""
    
    def pre_social_login(self, request, sociallogin):
        """Called before social login completes"""
        # If user already exists, just connect the account
        if sociallogin.is_existing:
            return
        
        # Check if user with this email already exists
        if sociallogin.email_addresses:
            email = sociallogin.email_addresses[0].email
            try:
                user = User.objects.get(email=email)
                # User exists, connect the social account
                sociallogin.connect(request, user)
            except User.DoesNotExist:
                # New user, will need role selection
                pass
    
    def save_user(self, request, sociallogin, form=None):
        """Save user from social login"""
        user = super().save_user(request, sociallogin, form)
        
        # Role is set by the CustomSocialSignupForm
        # If somehow role is not set, default to 'student'
        if not user.role:
            user.role = 'student'
            user.save()
        
        # Mark email as verified if coming from Google
        if sociallogin.account.provider == 'google':
            user.email_verified = True
            user.save()
        
        # Create user profile if it doesn't exist
        from .models import UserProfile
        UserProfile.objects.get_or_create(user=user)
        
        return user
    
    def get_connect_redirect_url(self, request, socialaccount):
        """Redirect after connecting social account - check onboarding first"""
        user = request.user
        onboarding_url = check_onboarding_and_redirect(user)
        if onboarding_url:
            return onboarding_url
        
        # If onboarding completed, redirect to dashboard
        if user.is_tutor():
            return reverse('tutors:dashboard')
        elif user.is_student() or user.is_parent():
            return reverse('students:dashboard')
        elif user.is_city_admin():
            return reverse('admin_panel:city_dashboard')
        elif user.is_global_admin():
            return reverse('admin_panel:global_dashboard')
        return reverse('users:profile')
    
    def get_signup_redirect_url(self, request):
        """Redirect after social signup - check onboarding first"""
        user = request.user
        onboarding_url = check_onboarding_and_redirect(user)
        if onboarding_url:
            return onboarding_url
        
        # If onboarding completed, redirect to dashboard
        if user.is_tutor():
            return reverse('tutors:dashboard')
        elif user.is_student() or user.is_parent():
            return reverse('students:dashboard')
        elif user.is_city_admin():
            return reverse('admin_panel:city_dashboard')
        elif user.is_global_admin():
            return reverse('admin_panel:global_dashboard')
        return reverse('users:profile')


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom adapter for regular account signup/login"""
    
    def get_login_redirect_url(self, request):
        """Redirect after login - check onboarding first"""
        user = request.user
        onboarding_url = check_onboarding_and_redirect(user)
        if onboarding_url:
            return onboarding_url
        
        # If onboarding completed, redirect to dashboard
        if user.is_tutor():
            return reverse('tutors:dashboard')
        elif user.is_student() or user.is_parent():
            return reverse('students:dashboard')
        elif user.is_city_admin():
            return reverse('admin_panel:city_dashboard')
        elif user.is_global_admin():
            return reverse('admin_panel:global_dashboard')
        return super().get_login_redirect_url(request)
    
    def get_signup_redirect_url(self, request):
        """Redirect after signup"""
        return reverse('users:login')

