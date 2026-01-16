from django.contrib import admin
from .models import Payment, Invoice, Commission


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'student', 'tutor', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'student__username', 'tutor__username']
    raw_id_fields = ['booking', 'student', 'tutor']
    date_hierarchy = 'created_at'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'payment', 'created_at']
    search_fields = ['invoice_number', 'payment__student__username']
    raw_id_fields = ['payment']


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ['payment', 'amount', 'percentage', 'is_paid_to_platform', 'paid_at']
    list_filter = ['is_paid_to_platform', 'paid_at']
    search_fields = ['payment__student__username', 'payment__tutor__username']
    raw_id_fields = ['payment']
