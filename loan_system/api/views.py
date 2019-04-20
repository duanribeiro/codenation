from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Loan
from .serializers import LoanSerializer


@api_view(['GET', 'POST'])
def ListPayment(request):
    return_object = Loan.objects.all()
    serializer = LoanSerializer(return_object, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)