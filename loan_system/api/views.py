import json
from pprint import pprint as pp

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def MakeLoan(request):
    # Recebi as informações do usuário
    payload = json.loads(request.body)
    pp(payload)
    r = payload['rate'] / 12
    installment = round((r + r / ((1 + r) ** payload['term'] - 1)) * payload['amount'], 2)

    loan_id = '{:08d}'.format(payload['id'])
    pp(payload)

    # Salvar no banco de dados
    # loan = Loan(loan_id=,
    #             amount=,
    #             rate=,
    #             date_start=,
    #             date_end=)



    return Response(installment, status=status.HTTP_200_OK)





