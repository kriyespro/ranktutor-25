from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/<int:booking_id>/', views.create_review, name='create'),
    path('dispute/<int:booking_id>/', views.raise_dispute, name='raise_dispute'),
    path('dispute/detail/<int:dispute_id>/', views.dispute_detail, name='dispute_detail'),
    path('safety/<int:user_id>/', views.report_safety_issue, name='report_safety'),
    path('flag-content/', views.flag_content, name='flag_content'),
]

