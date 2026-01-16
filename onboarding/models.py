from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class OnboardingStatus(TimeStampedModel):
    """Track onboarding completion status for users"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='onboarding_status'
    )
    
    # Step tracking
    role_selected = models.BooleanField(default=False)
    basic_info_completed = models.BooleanField(default=False)
    onboarding_completed = models.BooleanField(default=False)
    
    # Current step (1=role selection, 2=basic info, 3=complete)
    current_step = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = 'Onboarding Status'
        verbose_name_plural = 'Onboarding Statuses'
    
    def __str__(self):
        return f"Onboarding for {self.user.username} - Step {self.current_step}"


class OnboardingData(TimeStampedModel):
    """Store basic onboarding data collected during signup"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='onboarding_data'
    )
    
    # Common fields
    city = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=255, blank=True)  # Specific location/area
    
    # Student specific
    class_level = models.CharField(max_length=50, blank=True)  # e.g., "Class 10", "Grade 12"
    subject = models.CharField(max_length=100, blank=True)  # Primary subject
    
    # Tutor specific
    subjects = models.JSONField(default=list, blank=True)  # Multiple subjects
    per_class_fees = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    locations = models.JSONField(default=list, blank=True)  # Multiple locations
    
    # City Admin specific
    team_size = models.IntegerField(null=True, blank=True)
    contact = models.CharField(max_length=20, blank=True)
    
    class Meta:
        verbose_name = 'Onboarding Data'
        verbose_name_plural = 'Onboarding Data'
    
    def __str__(self):
        return f"Onboarding data for {self.user.username}"
