from django.urls import path
from . import views

app_name = 'onboarding'

urlpatterns = [
    path('', views.onboarding_check, name='check'),
    path('role-selection/', views.role_selection, name='role_selection'),
    path('basic-info/', views.basic_info, name='basic_info'),
]

