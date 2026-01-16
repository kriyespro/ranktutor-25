from django.db import models
from django.conf import settings
from core.models import TimeStampedModel, SoftDeleteModel


class Review(TimeStampedModel, SoftDeleteModel):
    """Reviews and ratings"""
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given', limit_choices_to={'role__in': ['student', 'parent']})
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received', limit_choices_to={'role': 'tutor'})
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text='Rating from 1 to 5')
    comment = models.TextField(help_text='Review comment')
    
    # Moderation
    is_approved = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    flagged_reason = models.TextField(blank=True)
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_reviews',
        limit_choices_to={'role__in': ['city_admin', 'global_admin']}
    )
    
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ['booking', 'student']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review: {self.rating}/5 by {self.student.username} for {self.tutor.username}"


class Dispute(TimeStampedModel):
    """Dispute resolution system"""
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, related_name='disputes')
    raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='disputes_raised')
    
    DISPUTE_TYPES = [
        ('payment', 'Payment Issue'),
        ('service', 'Service Quality'),
        ('cancellation', 'Cancellation/Refund'),
        ('safety', 'Safety Concern'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('under_review', 'Under Review'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    dispute_type = models.CharField(max_length=20, choices=DISPUTE_TYPES)
    description = models.TextField(help_text='Describe the issue')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Resolution
    resolution = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_disputes',
        limit_choices_to={'role__in': ['city_admin', 'global_admin']}
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Dispute'
        verbose_name_plural = 'Disputes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Dispute: {self.get_dispute_type_display()} - {self.booking}"


class SafetyReport(TimeStampedModel):
    """Safety reporting system"""
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='safety_reports_made')
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='safety_reports_received')
    
    REPORT_TYPES = [
        ('harassment', 'Harassment'),
        ('inappropriate_behavior', 'Inappropriate Behavior'),
        ('safety_concern', 'Safety Concern'),
        ('fraud', 'Fraud/Suspicious Activity'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_investigation', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    description = models.TextField(help_text='Describe the incident')
    evidence = models.FileField(upload_to='safety_reports/', blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    
    # Investigation
    investigated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='investigated_reports',
        limit_choices_to={'role__in': ['city_admin', 'global_admin']}
    )
    investigation_notes = models.TextField(blank=True)
    action_taken = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Safety Report'
        verbose_name_plural = 'Safety Reports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Safety Report: {self.get_report_type_display()} - {self.reported_user.username}"


class ContentModeration(TimeStampedModel):
    """Content moderation tracking"""
    CONTENT_TYPES = [
        ('profile', 'Profile'),
        ('message', 'Message'),
        ('review', 'Review'),
        ('document', 'Document'),
    ]
    
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_id = models.IntegerField()
    flagged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='flagged_content'
    )
    reason = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_content',
        limit_choices_to={'role__in': ['city_admin', 'global_admin']}
    )
    
    class Meta:
        verbose_name = 'Content Moderation'
        verbose_name_plural = 'Content Moderation'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Moderation: {self.get_content_type_display()} #{self.content_id}"
