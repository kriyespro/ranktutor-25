from django.contrib import admin
from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_name', 'grade_level', 'city', 'preferred_mode']
    list_filter = ['grade_level', 'preferred_mode', 'city']
    search_fields = ['user__username', 'user__email', 'student_name', 'city']
    raw_id_fields = ['user']
    filter_horizontal = ['preferred_subjects']
