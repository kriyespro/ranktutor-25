from django.urls import path
from . import views

app_name = 'tutors'

urlpatterns = [
    path('dashboard/', views.tutor_dashboard, name='dashboard'),
    path('profile-builder/', views.tutor_profile_builder, name='profile_builder'),
    path('pricing/', views.manage_pricing, name='manage_pricing'),
    path('documents/', views.upload_documents, name='upload_documents'),
    path('premium/', views.premium_features, name='premium_features'),
    path('premium/payment/<int:payment_id>/', views.process_premium_payment, name='process_premium_payment'),
    path('search/', views.tutor_search, name='search'),
    path('become-tutor/', views.become_tutor, name='become_tutor'),
    path('resources/', views.tutor_resources, name='resources'),
    path('disputes/', views.tutor_disputes, name='disputes'),
    path('<int:tutor_id>/', views.tutor_detail, name='detail'),
]

