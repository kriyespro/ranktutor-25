from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.conversations_list, name='conversations'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('start/<int:user_id>/', views.start_conversation, name='start_conversation'),
    path('booking/<int:booking_id>/', views.start_conversation_from_booking, name='start_from_booking'),
]

