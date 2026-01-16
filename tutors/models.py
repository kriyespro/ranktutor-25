from django.db import models
from django.conf import settings
from core.models import TimeStampedModel, SoftDeleteModel


class Subject(models.Model):
    """Subject categories for tutoring"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # For icon class names
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TutorProfile(TimeStampedModel, SoftDeleteModel):
    """Tutor profile information"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tutor_profile')
    
    # Basic Information
    headline = models.CharField(max_length=150, blank=True, help_text='Short headline that appears in listings')
    bio = models.TextField(help_text='Tell students about yourself')
    education = models.TextField(blank=True, help_text='Academic qualifications, certifications, and training')
    experience_summary = models.TextField(blank=True, help_text='Summary of teaching experience')
    teaching_style = models.TextField(blank=True, help_text='Describe teaching methodology and approach')
    achievements = models.TextField(blank=True, help_text='Awards, recognitions or milestones')
    languages = models.CharField(max_length=255, blank=True, help_text='Languages spoken (comma separated)')
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text='Default hourly rate in INR')
    intro_video = models.FileField(upload_to='tutor_videos/', blank=True, null=True)
    profile_complete = models.BooleanField(default=False)
    
    # Teaching Information
    subjects = models.ManyToManyField(Subject, related_name='tutors')
    teaching_levels = models.CharField(
        max_length=50,
        choices=[
            ('primary', 'Primary (1-5)'),
            ('middle', 'Middle (6-8)'),
            ('secondary', 'Secondary (9-10)'),
            ('senior_secondary', 'Senior Secondary (11-12)'),
            ('undergraduate', 'Undergraduate'),
            ('graduate', 'Graduate'),
            ('all', 'All Levels'),
        ],
        default='all'
    )
    
    # Location
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    service_areas = models.TextField(help_text='Comma-separated list of pincodes or areas', blank=True)
    
    # Geolocation (for map-based search)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text='Latitude for map location')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text='Longitude for map location')
    
    # Availability
    is_available_online = models.BooleanField(default=True)
    is_available_home = models.BooleanField(default=False)
    max_travel_distance = models.IntegerField(default=10, help_text='Maximum travel distance in km for home tutoring')
    
    # Verification Status
    is_verified = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('under_review', 'Under Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    
    # Verification Badges
    has_academic_verification = models.BooleanField(default=False)
    has_id_verification = models.BooleanField(default=False)
    has_police_verification = models.BooleanField(default=False)
    has_background_check = models.BooleanField(default=False)
    
    # Professional Credentials
    years_of_experience = models.IntegerField(default=0)
    certifications = models.TextField(blank=True, help_text='List of professional certifications')
    portfolio_url = models.URLField(blank=True)
    
    # Premium Features
    is_featured = models.BooleanField(default=False, help_text='Featured tutor listing')
    premium_boost_until = models.DateTimeField(null=True, blank=True, help_text='Premium boost expiration')
    boost_count = models.IntegerField(default=0, help_text='Number of times profile has been boosted')
    
    # Quality Assurance
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text='Overall quality score (0-100)')
    last_quality_audit = models.DateTimeField(null=True, blank=True)
    quality_issues = models.TextField(blank=True, help_text='Identified quality issues')
    intervention_required = models.BooleanField(default=False, help_text='Requires admin intervention')
    
    # Ratings (calculated fields)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Tutor Profile'
        verbose_name_plural = 'Tutor Profiles'
    
    def __str__(self):
        return f"Tutor Profile: {self.user.get_full_name() or self.user.username}"
    
    def get_verification_badges(self):
        """Get list of verification badges"""
        badges = []
        if self.has_academic_verification:
            badges.append('academic')
        if self.has_id_verification:
            badges.append('id')
        if self.has_police_verification:
            badges.append('police')
        if self.has_background_check:
            badges.append('background')
        return badges
    
    def is_premium_boosted(self):
        """Check if tutor has active premium boost"""
        if self.premium_boost_until:
            from django.utils import timezone
            return timezone.now() < self.premium_boost_until
        return False
    
    def has_premium_package(self):
        """Check if tutor has active Premium Package subscription"""
        from django.utils import timezone
        return self.premium_subscriptions.filter(
            subscription_type='premium',
            is_active=True,
            end_date__gte=timezone.now()
        ).exists()
    
    def has_featured_subscription(self):
        """Check if tutor has active Featured Listing subscription"""
        from django.utils import timezone
        return self.premium_subscriptions.filter(
            subscription_type='featured',
            is_active=True,
            end_date__gte=timezone.now()
        ).exists()
    
    def calculate_quality_score(self):
        """Calculate quality score based on various factors"""
        score = 0
        max_score = 100
        
        # Profile completeness (20 points)
        if self.bio and len(self.bio) > 50:
            score += 10
        if self.subjects.exists():
            score += 5
        if self.profile_complete:
            score += 5
        
        # Verification (30 points)
        if self.is_verified:
            score += 10
        verification_badges = len(self.get_verification_badges())
        score += min(verification_badges * 5, 20)
        
        # Ratings (30 points)
        if self.average_rating:
            score += (float(self.average_rating) / 5.0) * 30
        
        # Reviews count (10 points)
        if self.total_reviews >= 10:
            score += 10
        elif self.total_reviews >= 5:
            score += 5
        
        # Experience (10 points)
        if self.years_of_experience >= 5:
            score += 10
        elif self.years_of_experience >= 3:
            score += 5
        
        return min(score, max_score)


class TutorDocument(TimeStampedModel):
    """Documents uploaded by tutors for verification"""
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name='documents')
    
    DOCUMENT_TYPES = [
        ('academic', 'Academic Certificate'),
        ('id_proof', 'ID Proof'),
        ('police_verification', 'Police Verification'),
        ('certification', 'Professional Certification'),
        ('other', 'Other'),
    ]
    
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='tutor_documents/')
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Tutor Document'
        verbose_name_plural = 'Tutor Documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.tutor.user.username}"


class PricingOption(TimeStampedModel):
    """Pricing options for tutors"""
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name='pricing_options')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='pricing_options')
    
    MODE_CHOICES = [
        ('online', 'Online'),
        ('home', 'Home Tutoring'),
    ]
    
    LEVEL_CHOICES = [
        ('primary', 'Primary'),
        ('middle', 'Middle'),
        ('secondary', 'Secondary'),
        ('senior_secondary', 'Senior Secondary'),
        ('undergraduate', 'Undergraduate'),
        ('graduate', 'Graduate'),
    ]
    
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Pricing Option'
        verbose_name_plural = 'Pricing Options'
        unique_together = ['tutor', 'subject', 'mode', 'level']
    
    def __str__(self):
        return f"{self.tutor.user.username} - {self.subject.name} ({self.get_mode_display()}) - ₹{self.price_per_hour}/hr"


class PremiumSubscription(TimeStampedModel):
    """Premium subscriptions for tutors"""
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name='premium_subscriptions')
    
    SUBSCRIPTION_TYPES = [
        ('boost', 'Profile Boost'),
        ('featured', 'Featured Listing'),
        ('premium', 'Premium Package'),
    ]
    
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_TYPES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Premium Subscription'
        verbose_name_plural = 'Premium Subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tutor.user.username} - {self.get_subscription_type_display()}"


class QualityAudit(TimeStampedModel):
    """Quality audit records for tutors"""
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name='quality_audits')
    
    AUDIT_TYPES = [
        ('automated', 'Automated Audit'),
        ('manual', 'Manual Review'),
        ('complaint', 'Complaint-Based'),
        ('scheduled', 'Scheduled Audit'),
    ]
    
    audit_type = models.CharField(max_length=20, choices=AUDIT_TYPES)
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, help_text='Quality score (0-100)')
    issues_found = models.TextField(blank=True, help_text='Issues identified during audit')
    recommendations = models.TextField(blank=True, help_text='Recommendations for improvement')
    audited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audits_conducted',
        limit_choices_to={'role__in': ['city_admin', 'global_admin']}
    )
    is_resolved = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Quality Audit'
        verbose_name_plural = 'Quality Audits'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Quality Audit: {self.tutor.user.username} - {self.quality_score}"


class QualityCertification(TimeStampedModel):
    """Quality certifications for tutors"""
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name='quality_certifications')
    
    CERTIFICATION_TYPES = [
        ('excellent', 'Excellent Quality'),
        ('verified', 'Verified Quality'),
        ('premium', 'Premium Quality'),
    ]
    
    certification_type = models.CharField(max_length=20, choices=CERTIFICATION_TYPES)
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='certifications_issued',
        limit_choices_to={'role__in': ['city_admin', 'global_admin']}
    )
    valid_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Quality Certification'
        verbose_name_plural = 'Quality Certifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_certification_type_display()} - {self.tutor.user.username}"
