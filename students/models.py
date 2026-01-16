from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class StudentProfile(TimeStampedModel):
    """Student profile information"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile', limit_choices_to={'role__in': ['student', 'parent']})
    
    # Student Information (if user is parent, this is child info)
    student_name = models.CharField(max_length=100, blank=True)
    student_age = models.IntegerField(null=True, blank=True)
    grade_level = models.CharField(
        max_length=30,
        choices=[
            ('primary', 'Primary (1-5)'),
            ('middle', 'Middle (6-8)'),
            ('secondary', 'Secondary (9-10)'),
            ('senior_secondary', 'Senior Secondary (11-12)'),
            ('undergraduate', 'Undergraduate'),
            ('graduate', 'Graduate'),
        ],
        blank=True
    )
    
    # Learning Preferences
    preferred_subjects = models.ManyToManyField('tutors.Subject', blank=True, related_name='interested_students')
    preferred_mode = models.CharField(
        max_length=20,
        choices=[
            ('online', 'Online'),
            ('home', 'Home Tutoring'),
            ('both', 'Both'),
        ],
        default='both'
    )
    
    # Location
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    
    # Learning Goals
    learning_goals = models.TextField(blank=True, help_text='What do you want to achieve?')
    
    class Meta:
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
    
    def __str__(self):
        return f"Student Profile: {self.user.get_full_name() or self.user.username}"
