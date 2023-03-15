from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Transaction, Wallet

@api_view(['POST'])
def payment_webhook(request):
    if request.method == 'POST':
        # get the transaction reference and status from the request body
        data = request.data
        tx_ref = data.get('tx_ref')
        status = data.get('status')
        # update the transaction record in the database with the payment status
        try:
            transaction = Transaction.objects.get(transaction_ref=tx_ref)
            if status == 'successful':
                transaction.status = 'completed'
                # credit the user's wallet with the amount of the transaction
                wallet = Wallet.objects.get(user=transaction.user)
                wallet.balance += transaction.amount
                wallet.save()
            else:
                transaction.status = 'failed'
            transaction.save()
        except Transaction.DoesNotExist:
            pass
        # return a success response or error response depending on the payment status
        if status == 'successful':
            return Response({'message': 'Payment successful'}, status=200)
        else:
            return Response({'message': 'Payment failed'}, status=400)
