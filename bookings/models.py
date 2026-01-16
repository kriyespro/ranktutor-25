from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import TimeStampedModel, SoftDeleteModel


class AvailabilitySlot(TimeStampedModel):
    """Tutor availability slots"""
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='availability_slots', limit_choices_to={'role': 'tutor'})
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Availability Slot'
        verbose_name_plural = 'Availability Slots'
        unique_together = ['tutor', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.tutor.username} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class Booking(TimeStampedModel, SoftDeleteModel):
    """Booking/lesson booking"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings', limit_choices_to={'role__in': ['student', 'parent']})
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tutor_bookings', limit_choices_to={'role': 'tutor'})
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    MODE_CHOICES = [
        ('online', 'Online'),
        ('home', 'Home Tutoring'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    
    # Lesson Details
    subject = models.ForeignKey('tutors.Subject', on_delete=models.CASCADE)
    lesson_date = models.DateField()
    lesson_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    
    # Recurring lessons
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('biweekly', 'Bi-weekly'),
            ('monthly', 'Monthly'),
        ],
        blank=True
    )
    recurrence_end_date = models.DateField(null=True, blank=True)
    parent_booking = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='recurring_bookings')
    
    # Address for home tutoring
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    
    # Pricing
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Trial class
    is_trial = models.BooleanField(default=False)
    trial_is_free = models.BooleanField(default=False)
    
    # Notes
    student_notes = models.TextField(blank=True, help_text='Special requirements or notes')
    tutor_notes = models.TextField(blank=True)
    
    # Timestamps
    accepted_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-lesson_date', '-lesson_time']
    
    def __str__(self):
        return f"Booking: {self.student.username} with {self.tutor.username} on {self.lesson_date}"
    
    def save(self, *args, **kwargs):
        # Calculate total amount
        self.total_amount = float(self.price_per_hour) * float(self.duration_hours)
        # Calculate commission (15%)
        from django.conf import settings
        commission_rate = getattr(settings, 'COMMISSION_PERCENTAGE', 15) / 100
        self.commission_amount = self.total_amount * commission_rate
        super().save(*args, **kwargs)


class Lesson(TimeStampedModel):
    """Completed lesson record"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='lesson')
    
    # Lesson content
    topics_covered = models.TextField(help_text='Topics covered in this lesson')
    homework_assigned = models.TextField(blank=True)
    student_progress = models.TextField(blank=True, help_text='Notes on student progress')
    
    # Attendance
    student_attended = models.BooleanField(default=True)
    tutor_attended = models.BooleanField(default=True)
    
    # Completion
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
    
    def __str__(self):
        return f"Lesson: {self.booking}"


class CalendarSync(TimeStampedModel):
    """External calendar synchronization"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calendar_syncs')
    
    CALENDAR_TYPES = [
        ('google', 'Google Calendar'),
        ('outlook', 'Microsoft Outlook'),
        ('ical', 'iCal/Other'),
    ]
    
    calendar_type = models.CharField(max_length=20, choices=CALENDAR_TYPES)
    sync_token = models.CharField(max_length=255, blank=True)
    calendar_id = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Calendar Sync'
        verbose_name_plural = 'Calendar Syncs'
        unique_together = ['user', 'calendar_type']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_calendar_type_display()}"
