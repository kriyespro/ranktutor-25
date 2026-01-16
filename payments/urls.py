from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('history/', views.payment_history, name='history'),
    path('process/<int:booking_id>/', views.process_payment, name='process'),
    path('<int:payment_id>/', views.payment_detail, name='detail'),
    path('<int:payment_id>/invoice/', views.generate_invoice, name='generate_invoice'),
    path('earnings/', views.tutor_earnings, name='tutor_earnings'),
    path('<int:payment_id>/refund/', views.request_refund, name='request_refund'),
    path('wallet/', views.wallet_view, name='wallet'),
    path('wallet/recharge/', views.wallet_recharge, name='wallet_recharge'),
    path('<int:payment_id>/release/', views.release_payment, name='release_payment'),
]

