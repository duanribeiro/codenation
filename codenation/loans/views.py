from loans.models import Loan
from loans.serializers import LoanSerializer

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


class LoanAPI(APIView):
    def _calculate_installment_price(self, loan):
        rate = loan.interest_rate / 12
        return (rate + rate / ((1 + rate) ** loan.installment_amount - 1)) * loan.amount
    
    def get(self, request, format=None):
        loans = Loan.objects.all()
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        loan_order = LoanSerializer(data=request.data)
        if loan_order.is_valid():
            loan = loan_order.save()
            installment_price = round(self._calculate_installment_price(loan), 4)
            return Response(
                data={
                    'id': loan.loan_id,
                    'installment': installment_price,
                },
                status=status.HTTP_201_CREATED)
        return Response(loan_order.errors, status=status.HTTP_400_BAD_REQUEST)
