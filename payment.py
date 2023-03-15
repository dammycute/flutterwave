from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Transaction, Wallet
import requests

@login_required
def payment(request):
    amount = 500 # or whatever amount you want to charge
    transaction_ref = f'{request.user.username}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")}'
    # create a new transaction record in the database
    transaction = Transaction.objects.create(
        user=request.user,
        transaction_ref=transaction_ref,
        amount=amount
    )
    # construct the URL for the Flutterwave payment page
    payload = {
        'tx_ref': transaction_ref,
        'amount': amount,
        'currency': 'NGN',
        'redirect_url': request.build_absolute_uri(reverse('payment-success')),
        'payment_options': 'card',
        'customer': {
            'email': request.user.email,
            'phonenumber': request.user.profile.phone_number,
            'name': request.user.get_full_name()
        },
        'customizations': {
            'title': 'My Store',
            'description': 'Payment for items in cart',
            'logo': 'https://example.com/logo.png'
        }
    }
    response = requests.post('https://api.flutterwave.com/v3/payments', headers={
        'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}',
        'Content-Type': 'application/json'
    }, json=payload)
    # redirect the user to the Flutterwave payment page
    return redirect(response.json()['data']['link'])
