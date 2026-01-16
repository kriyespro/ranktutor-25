from django.contrib import admin
from .models import AvailabilitySlot, Booking, Lesson, CalendarSync


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ['tutor', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available']
    search_fields = ['tutor__username', 'tutor__email']
    raw_id_fields = ['tutor']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'tutor', 'subject', 'lesson_date', 'lesson_time', 'status', 'is_recurring', 'total_amount']
    list_filter = ['status', 'mode', 'is_trial', 'is_recurring', 'lesson_date']
    search_fields = ['student__username', 'tutor__username', 'subject__name']
    raw_id_fields = ['student', 'tutor', 'subject', 'parent_booking']
    date_hierarchy = 'lesson_date'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['booking', 'is_completed', 'student_attended', 'tutor_attended', 'completed_at']
    list_filter = ['is_completed', 'student_attended', 'tutor_attended']
    search_fields = ['booking__student__username', 'booking__tutor__username']
    raw_id_fields = ['booking']


@admin.register(CalendarSync)
class CalendarSyncAdmin(admin.ModelAdmin):
    list_display = ['user', 'calendar_type', 'is_active', 'last_synced_at']
    list_filter = ['calendar_type', 'is_active', 'last_synced_at']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']
