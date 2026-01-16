from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class AnalyticsEvent(TimeStampedModel):
    """Track analytics events"""
    EVENT_TYPES = [
        ('page_view', 'Page View'),
        ('tutor_search', 'Tutor Search'),
        ('booking_created', 'Booking Created'),
        ('payment_completed', 'Payment Completed'),
        ('review_submitted', 'Review Submitted'),
        ('message_sent', 'Message Sent'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_events')
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    event_data = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Analytics Event'
        verbose_name_plural = 'Analytics Events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.user or 'Anonymous'}"


class PerformanceMetric(TimeStampedModel):
    """Performance metrics for tutors and platform"""
    METRIC_TYPES = [
        ('tutor_rating', 'Tutor Average Rating'),
        ('booking_conversion', 'Booking Conversion Rate'),
        ('student_retention', 'Student Retention Rate'),
        ('revenue', 'Revenue'),
        ('commission', 'Commission Collected'),
    ]
    
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    period_start = models.DateField()
    period_end = models.DateField()
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Performance Metric'
        verbose_name_plural = 'Performance Metrics'
        ordering = ['-period_start', 'metric_type']
    
    def __str__(self):
        return f"{self.get_metric_type_display()}: {self.value} ({self.period_start} to {self.period_end})"


class RevenueForecast(TimeStampedModel):
    """Revenue forecasting"""
    forecast_date = models.DateField()
    forecasted_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    confidence_level = models.DecimalField(max_digits=5, decimal_places=2, help_text='Confidence level as percentage')
    factors = models.JSONField(default=dict, blank=True, help_text='Factors influencing the forecast')
    
    class Meta:
        verbose_name = 'Revenue Forecast'
        verbose_name_plural = 'Revenue Forecasts'
        ordering = ['-forecast_date']
    
    def __str__(self):
        return f"Forecast: ₹{self.forecasted_revenue} on {self.forecast_date}"


class TrendAnalysis(TimeStampedModel):
    """Trend analysis data"""
    TREND_TYPES = [
        ('user_growth', 'User Growth'),
        ('booking_trend', 'Booking Trend'),
        ('revenue_trend', 'Revenue Trend'),
        ('tutor_growth', 'Tutor Growth'),
        ('subject_popularity', 'Subject Popularity'),
    ]
    
    trend_type = models.CharField(max_length=30, choices=TREND_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()
    trend_data = models.JSONField(default=dict, help_text='Trend data points')
    analysis = models.TextField(blank=True, help_text='Analysis and insights')
    
    class Meta:
        verbose_name = 'Trend Analysis'
        verbose_name_plural = 'Trend Analyses'
        ordering = ['-period_start', 'trend_type']
    
    def __str__(self):
        return f"{self.get_trend_type_display()} ({self.period_start} to {self.period_end})"
