from django.contrib import admin
from .models import Subject, TutorProfile, TutorDocument, PricingOption, PremiumSubscription, QualityAudit, QualityCertification


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(TutorProfile)
class TutorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'state', 'is_verified', 'verification_status', 'quality_score', 'average_rating', 'total_reviews']
    list_filter = ['is_verified', 'verification_status', 'is_featured', 'intervention_required', 'city', 'state']
    search_fields = ['user__username', 'user__email', 'city', 'state']
    raw_id_fields = ['user']
    filter_horizontal = ['subjects']
    readonly_fields = ['quality_score', 'last_quality_audit', 'average_rating', 'total_reviews']


@admin.register(TutorDocument)
class TutorDocumentAdmin(admin.ModelAdmin):
    list_display = ['tutor', 'document_type', 'is_verified', 'verified_by', 'created_at']
    list_filter = ['document_type', 'is_verified', 'created_at']
    search_fields = ['tutor__user__username']
    raw_id_fields = ['tutor', 'verified_by']
    date_hierarchy = 'created_at'


@admin.register(PricingOption)
class PricingOptionAdmin(admin.ModelAdmin):
    list_display = ['tutor', 'subject', 'mode', 'level', 'price_per_hour', 'is_active']
    list_filter = ['mode', 'level', 'is_active']
    search_fields = ['tutor__user__username', 'subject__name']
    raw_id_fields = ['tutor', 'subject']


@admin.register(PremiumSubscription)
class PremiumSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['tutor', 'subscription_type', 'start_date', 'end_date', 'is_active']
    list_filter = ['subscription_type', 'is_active', 'start_date']
    search_fields = ['tutor__user__username']
    raw_id_fields = ['tutor']
    date_hierarchy = 'start_date'


@admin.register(QualityAudit)
class QualityAuditAdmin(admin.ModelAdmin):
    list_display = ['tutor', 'audit_type', 'quality_score', 'is_resolved', 'audited_by', 'created_at']
    list_filter = ['audit_type', 'is_resolved', 'created_at']
    search_fields = ['tutor__user__username']
    raw_id_fields = ['tutor', 'audited_by']
    date_hierarchy = 'created_at'


@admin.register(QualityCertification)
class QualityCertificationAdmin(admin.ModelAdmin):
    list_display = ['tutor', 'certification_type', 'issued_by', 'valid_until', 'is_active']
    list_filter = ['certification_type', 'is_active']
    search_fields = ['tutor__user__username']
    raw_id_fields = ['tutor', 'issued_by']
    date_hierarchy = 'created_at'
