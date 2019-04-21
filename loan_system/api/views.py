import json
from datetime import timedelta
from random import randint

from dateutil import parser
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Loan


def gera_loan_id():
    numbers = [str(randint(1000, 9999)) for x in range(4)]
    return f'{numbers[0][:3]}-{numbers[1]}-{numbers[2]}-{numbers[3]}'

@api_view(['POST'])
def MakeLoan(request):
    # Recebi as informações do usuário
    payload = json.loads(request.body)

    # Contas financeiras
    r = payload['rate'] / 12
    installment = round((r + r / ((1 + r) ** payload['term'] - 1)) * payload['amount'], 2)

    # Processando os dados
    date_start = parser.parse(payload['date'])
    date_end = date_start + timedelta(days=30 * payload['term'])
    loan_id = gera_loan_id()

    # Salvar no banco de dados
    loan = Loan(loan_id=loan_id,
                amount=payload['amount'],
                rate=payload['rate'],
                date_start=date_start,
                date_end=date_end)
    loan.save()

    return Response({'loan_id': loan_id, 'installment': installment}, status=status.HTTP_201_CREATED)





