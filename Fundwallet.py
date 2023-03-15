from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Transaction, Wallet
import requests
import uuid


class FundWalletAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # get the amount from the request data
        amount = request.data.get('amount')
        if not amount:
            return Response({'error': 'Please provide an amount to fund the wallet'}, status=status.HTTP_400_BAD_REQUEST)

        # generate a transaction reference using uuid
        transaction_ref = str(uuid.uuid4())

        # create a new transaction record in the database
        transaction = Transaction.objects.create(
            user=request.user,
            transaction_ref=transaction_ref,
            amount=amount
        )

        # get or create the user's wallet
        wallet, created = Wallet.objects.get_or_create(user=request.user)

        # construct the URL for the Flutterwave payment page
        payload = {
            'tx_ref': transaction_ref,
            'amount': amount,
            'currency': 'NGN',
            'redirect_url': request.build_absolute_uri(reverse('fund-wallet-success')),
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
        return Response({'payment_url': response.json()['data']['link']})
