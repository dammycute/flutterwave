from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def payment_redirect(request):
    # get the transaction reference and status from the query string parameters
    tx_ref = request.GET.get('tx_ref')
    status = request.GET.get('status')
    if tx_ref and status == 'successful':
        # payment was successful, return a success response
        return Response({'message': 'Payment successful'})
    else:
        # payment failed or no transaction reference was provided, return an error response
        return Response({'message': 'Payment failed'}, status=400)
