from django.urls import path
from .views import PaymentView, FundWalletView, payment_webhook, payment_redirect

urlpatterns = [
    path('payment/', PaymentView.as_view(), name='payment'),
    path('fund_wallet/', FundWalletView.as_view(), name='fund_wallet'),
    path('payment/webhook/', payment_webhook, name='payment_webhook'),
    path('payment/redirect/', payment_redirect, name='payment_redirect'),
]
