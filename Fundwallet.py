import requests
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.views import APIView
from .models import Wallet

class FundWalletView(APIView):
    def get(self, request):
        # get the user and amount from the request data
        user = request.user
        amount = request.query_params.get('amount')

        # check if the user has a wallet, create one if they don't
        try:
            wallet = Wallet.objects.get(user=user)
        except Wallet.DoesNotExist:
            wallet = Wallet.objects.create(user=user)

        # generate a payment request URL using Flutterwave's API
        response = requests.post('https://api.flutterwave.com/v3/payments',
            headers={'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}'},
            json={
                'tx_ref': f'wallet-funding-{wallet.id}',
                'amount': amount,
                'currency': 'NGN',
                'redirect_url': request.build_absolute_uri('/payment/redirect/'),
                'payment_options': 'card',
                'customer': {
                    'email': user.email,
                    'name': user.get_full_name(),
                },
                'meta': {
                    'wallet_id': wallet.id,
                },
            },
        )
        payment_url = response.json()['data']['link']

        # redirect the user to the payment request URL
        return redirect(payment_url)
