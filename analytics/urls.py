from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('revenue-forecast/', views.revenue_forecast, name='revenue_forecast'),
    path('reports/', views.custom_report_builder, name='report_builder'),
]

