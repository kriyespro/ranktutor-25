from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('classes/', views.student_classes, name='classes'),
    path('payments/', views.student_payments, name='payments'),
    path('homework/', views.student_homework, name='homework'),
    path('my-tutors/', views.my_tutors, name='my_tutors'),
]

