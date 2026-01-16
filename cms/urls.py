from django.urls import path
from . import views

app_name = 'cms'

urlpatterns = [
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('faq/', views.faq_list, name='faq'),
    path('page/<slug:slug>/', views.page_detail, name='page'),
]

