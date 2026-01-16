from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('create/<int:tutor_id>/', views.create_booking, name='create'),
    path('<int:booking_id>/', views.booking_detail, name='detail'),
    path('<int:booking_id>/accept/', views.accept_booking, name='accept'),
    path('<int:booking_id>/reject/', views.reject_booking, name='reject'),
    path('<int:booking_id>/complete/', views.complete_lesson, name='complete'),
    path('<int:booking_id>/notes/', views.lesson_notes, name='lesson_notes'),
    path('availability/', views.manage_availability, name='manage_availability'),
    path('calendar-sync/', views.calendar_sync, name='calendar_sync'),
]

