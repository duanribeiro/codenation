import os
import json
import pytz

from uuid import uuid4
from random import random, randrange, choice
from datetime import datetime, timedelta

from classes import Loan, LoanPayment, Client, BasicData


class JsonHelper(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, BasicData):
            return obj.__dict__()
        if isinstance(obj, datetime):
            return str(obj)
        return json.JSONEncoder.default(obj)


def _make_date():
    year = 2019
    month = randrange(1, 13)
    day = randrange(1, 31) if month != 2 else randrange(1, 29)
    hour, minute, seconds = randrange(0, 23), randrange(0, 59), randrange(0, 59)
    return datetime(year, month, day, hour, minute, seconds, tzinfo=pytz.UTC)

def _calculate_payment_amount(loan):
    rate = loan.fields['interest_rate'] / 12
    return (rate + rate / ((1 + rate) **loan.fields['amount_of_payments'] - 1)) * loan.fields['amount']

def generate_loans(number_of_loans, clients):
    loans = []
    for _ in range(number_of_loans):
        loan = Loan(
            pk=str(uuid4()),
            fields={
                'amount': random() * randrange(start=10, stop=1001, step=10),
                'amount_of_payments': randrange(1, 15),
                'interest_rate': randrange(10, 101) / 100,
                'requested_date': _make_date(),
                'client': choice(clients).pk,
            }
        )
        loan.fields['payment_amount'] = _calculate_payment_amount(loan)
        loans.append(loan)
    return loans

def generate_loans_payments(loans):
    loan_payments = []
    for loan in loans:
        number_of_payments = randrange(0, loan.fields['amount_of_payments'])
        for payment_number in range(1, number_of_payments + 1):
            loan_payment = LoanPayment(
                pk=str(uuid4()),
                fields={
                    'payment_number': payment_number,
                    'payment_type': 'made' if randrange(1, 3) % 2 == 0 else 'missed',
                    'payment_date': loan.fields['requested_date'] + timedelta(days=30 * payment_number),
                    'payment_amount': loan.fields['payment_amount'],
                    'loan': loan.pk,
                    'created_at': loan.fields['requested_date'] + timedelta(days=30 * payment_number),
                }
            )
            loan_payments.append(loan_payment)
    return loan_payments

def create_clients(number_of_clients):
    clients = []
    for i in range(number_of_clients):
        client = Client(
            pk=str(uuid4()),
            fields={
                'name': f'Name{i}',
                'surname': f'Surname{i}',
                'email': f'test{i}@gmail.com',
                'telephone': str(randrange(10000000000, 100000000000)),
                'cpf': str(randrange(10000000000, 100000000000)),
                'created_at': _make_date(),
            }
        )
        clients.append(client)
    return clients

def save_data(path_to_save, data):
    with open(path_to_save, 'w') as fp:
        json.dump(data, fp, cls=JsonHelper)

def generate_data(number_of_loans, number_of_clients, dir_to_save):
    clients = create_clients(number_of_clients)
    loans = generate_loans(number_of_loans, clients)
    loan_payments = generate_loans_payments(loans)
    save_data(os.path.join(
        dir_to_save, 'test_data.json'),
        clients + loans + loan_payments
    )
