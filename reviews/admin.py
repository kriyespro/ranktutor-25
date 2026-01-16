from django.contrib import admin
from .models import Review, Dispute, SafetyReport, ContentModeration


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'tutor', 'rating', 'is_approved', 'is_flagged', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_flagged', 'created_at']
    search_fields = ['student__username', 'tutor__username', 'comment']
    raw_id_fields = ['student', 'tutor', 'booking', 'moderated_by']
    date_hierarchy = 'created_at'


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'raised_by', 'dispute_type', 'status', 'created_at']
    list_filter = ['dispute_type', 'status', 'created_at']
    search_fields = ['booking__id', 'raised_by__username', 'description']
    raw_id_fields = ['booking', 'raised_by', 'resolved_by']
    date_hierarchy = 'created_at'


@admin.register(SafetyReport)
class SafetyReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'reported_by', 'reported_user', 'report_type', 'status', 'created_at']
    list_filter = ['report_type', 'status', 'created_at']
    search_fields = ['reported_by__username', 'reported_user__username', 'description']
    raw_id_fields = ['reported_by', 'reported_user', 'investigated_by']
    date_hierarchy = 'created_at'


@admin.register(ContentModeration)
class ContentModerationAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_type', 'content_id', 'is_resolved', 'created_at']
    list_filter = ['content_type', 'is_resolved', 'created_at']
    search_fields = ['reason']
    raw_id_fields = ['flagged_by', 'resolved_by']
    date_hierarchy = 'created_at'
