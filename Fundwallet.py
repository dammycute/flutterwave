from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Transaction, Wallet
import requests
import uuid

@login_required
def fundwallet(request):
    amount = 500 # or whatever amount you want to charge
    transaction_ref = str(uuid.uuid4())
    user_wallet = Wallet.objects.filter(user=request.user).first()
    if user_wallet is None:
        user_wallet = Wallet.objects.create(user=request.user)
    # create a new transaction record in the database
    transaction = Transaction.objects.create(
        user=request.user,
        wallet=user_wallet,
        transaction_ref=transaction_ref,
        amount=amount
    )
    # construct the URL for the Flutterwave payment page
    payload = {
        'tx_ref': transaction_ref,
        'amount': amount,
        'currency': 'NGN',
        'redirect_url': request.build_absolute_uri(reverse('fundwallet-success')),
        'payment_options': 'card',
        'customer': {
            'email': request.user.email,
            'phonenumber': request.user.profile.phone_number,
            'name': request.user.get_full_name()
        },
        'customizations': {
            'title': 'My Store',
            'description': 'Payment for wallet funding',
            'logo': 'https://example.com/logo.png'
        }
    }
    response = requests.post('https://api.flutterwave.com/v3/payments', headers={
        'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}',
        'Content-Type': 'application/json'
    }, json=payload)
    # redirect the user to the Flutterwave payment page
    return redirect(response.json()['data']['link'])
