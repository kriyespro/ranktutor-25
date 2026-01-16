"""
URL configuration for ranktutor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin at /sd/ (Django templates)
    path('sd/', admin.site.urls),
    
    # Custom admin dashboard at /admin/ (Jinja2 templates)
    path('admin/', include('admin_panel.urls')),
    
    # Allauth URLs (for social authentication)
    path('accounts/', include('allauth.urls')),
    
    # Onboarding
    path('onboarding/', include('onboarding.urls')),
    
    # Core app
    path('', include('core.urls')),
    
    # User management
    path('users/', include('users.urls')),
    
    # Tutors
    path('tutors/', include('tutors.urls')),
    
    # Students
    path('students/', include('students.urls')),
    
    # Bookings
    path('bookings/', include('bookings.urls')),
    
    # Payments
    path('payments/', include('payments.urls')),
    
    # Messaging
    path('messages/', include('messaging.urls')),
    
    # Reviews
    path('reviews/', include('reviews.urls')),
    
    # CMS
    path('', include('cms.urls')),
    
    # Analytics
    path('analytics/', include('analytics.urls')),
    
    # Notifications
    path('notifications/', include('notifications.urls')),
    
    # API
    path('api/', include('api.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
