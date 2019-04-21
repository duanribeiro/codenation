import json
from datetime import timedelta
from pprint import pprint as pp
from random import randint

from dateutil import parser
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Loan, Payment


def random_loan_id():
    numbers = [str(randint(1000, 9999) + randint(1, 9999)) for x in range(4)]
    return f'{numbers[0][-3:]}-{numbers[1][-4:]}-{numbers[2][-4:]}-{numbers[3][-4:]}'


@api_view(['POST'])
def MakeLoan(request):
    # Recebi as informações do usuário
    payload = json.loads(request.body)
    print(payload)
    # Contas financeiras
    r = payload['rate'] / 12
    installment = round((r + r / ((1 + r) ** payload['term'] - 1)) * payload['amount'], 2)

    # Processando os dados
    date_start = parser.parse(payload['date'])
    date_end = date_start + timedelta(days=30 * payload['term'])
    loan_id = random_loan_id()

    # Salvar no banco de dados
    loan = Loan(loan_id=loan_id,
                amount=payload['amount'],
                rate=payload['rate'],
                installment=installment,
                date_start=date_start,
                date_end=date_end)
    loan.save()

    return Response({'loan_id': loan_id, 'installment': installment}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def MakePayment(request, loan_id):
    # Recebi as informações do usuário
    payload = json.loads(request.body)

    # Processando os dados
    date = parser.parse(payload['date'])

    # Salvar no banco de dados
    payment = Payment(loan_id=Loan.objects.get(loan_id=loan_id),
                      date=date,
                      type=payload['payment'],
                      amount=payload['amount'])
    payment.save()

    return Response('Ok', status=status.HTTP_201_CREATED)


@api_view(['POST'])
def ListBalance(request, loan_id):
    # Recebi as informações do usuário
    payload = json.loads(request.body)
    date = parser.parse(payload['date'])

    # Pegando o id original do relacionamento
    loan = Loan.objects.filter(loan_id=loan_id).values('id', 'amount').get()

    # Buscar no banco de dados
    payments = Payment.objects.filter(loan_id=loan['id']).filter(date__lte=date)
    for payment in payments:
        if payment.type == 'made':
            loan['amount'] -= payment.amount
        else:
            loan['amount'] -= (loan.installment - payment.amount)
        pp(loan['amount'])

    return Response({loan['amount']}, status=status.HTTP_200_OK)

