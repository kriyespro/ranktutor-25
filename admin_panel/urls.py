from django.urls import path
from . import views
from .management_views import (
    user_list, user_detail, user_create, user_edit, user_delete,
    tutor_list, tutor_detail, tutor_edit,
    booking_list, booking_detail,
    payment_list, payment_detail,
    review_list, review_detail,
    dispute_list, dispute_detail,
    safety_report_list, safety_report_detail,
    document_list,
    subject_list, subject_create, subject_edit, subject_delete,
)

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard_redirect, name='dashboard'),
    path('city/', views.city_admin_dashboard, name='city_dashboard'),
    path('global/', views.global_admin_dashboard, name='global_dashboard'),
    
    # Quality & Verification
    path('city/document/<int:document_id>/verify/', views.verify_tutor_document, name='verify_document'),
    path('city/tutor/<int:tutor_id>/approve/', views.approve_tutor, name='approve_tutor'),
    path('quality-audits/', views.quality_audits_list, name='quality_audits'),
    path('quality-audit/<int:tutor_id>/', views.conduct_quality_audit, name='conduct_audit'),
    path('certification/<int:tutor_id>/', views.issue_certification, name='issue_certification'),
    
    # User Management
    path('users/', user_list, name='user_list'),
    path('users/create/', user_create, name='user_create'),
    path('users/<int:user_id>/', user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', user_delete, name='user_delete'),
    
    # Tutor Management
    path('tutors/', tutor_list, name='tutor_list'),
    path('tutors/<int:tutor_id>/', tutor_detail, name='tutor_detail'),
    path('tutors/<int:tutor_id>/edit/', tutor_edit, name='tutor_edit'),
    
    # Booking Management
    path('bookings/', booking_list, name='booking_list'),
    path('bookings/<int:booking_id>/', booking_detail, name='booking_detail'),
    
    # Payment Management
    path('payments/', payment_list, name='payment_list'),
    path('payments/<int:payment_id>/', payment_detail, name='payment_detail'),
    
    # Review Management
    path('reviews/', review_list, name='review_list'),
    path('reviews/<int:review_id>/', review_detail, name='review_detail'),
    
    # Dispute Management
    path('disputes/', dispute_list, name='dispute_list'),
    path('disputes/<int:dispute_id>/', dispute_detail, name='dispute_detail'),
    
    # Safety Report Management
    path('safety-reports/', safety_report_list, name='safety_report_list'),
    path('safety-reports/<int:report_id>/', safety_report_detail, name='safety_report_detail'),
    
    # Document Management
    path('documents/', document_list, name='document_list'),
    
    # Subject Management
    path('subjects/', subject_list, name='subject_list'),
    path('subjects/create/', subject_create, name='subject_create'),
    path('subjects/<int:subject_id>/edit/', subject_edit, name='subject_edit'),
    path('subjects/<int:subject_id>/delete/', subject_delete, name='subject_delete'),

    # Teaching Levels (Static configuration overview)
    path('system/teaching-levels/', views.teaching_level_management, name='teaching_levels'),
]
