from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateAPIView
from rest_framework import permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from .models import Transaction, Wallet
from .serializers import TransactionSerializer


class FundWalletView(LoginRequiredMixin, CreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        wallet = get_object_or_404(Wallet, user=request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']
        transaction_ref = f'{request.user.username}_{uuid.uuid4()}'
        # create a new transaction record in the database
        transaction = Transaction.objects.create(
            user=request.user,
            wallet=wallet,
            transaction_ref=transaction_ref,
            amount=amount
        )
        # construct the payload for the Flutterwave payment page
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
        # return the Flutterwave payment link to the client
        return Response({'payment_link': response.json()['data']['link']})
