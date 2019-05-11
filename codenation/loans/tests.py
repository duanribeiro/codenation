import json
import uuid
from decimal import Decimal

from django.test import TestCase, Client
from rest_framework import status

from loans.models import Loan, LoanPayment
from loans.serializers import LoanSerializer, LoanPaymentSerializer

client = Client()


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


class LoanTest(TestCase):
    def test_empty_db(self):
        response = client.get(path='http://localhost:8000/loans/')

        self.assertEqual(response.data, [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_one_loan(self):
        payload = {
            "amount": 5000,
            "term": 24,
            "rate": 0.5,
            "date": "2019-05-09 03:18Z"
        }
        response = client.post(path='http://localhost:8000/loans/',
                               data=json.dumps(payload),
                               content_type="application/json")
        loan = Loan.objects.first()
        serializer = LoanSerializer(loan)

        self.assertEqual(is_valid_uuid(response.data['id']), True)
        self.assertEqual(response.data['installment'], Decimal('333.5539'))

        self.assertEqual(serializer.data['amount'], '5000.00')
        self.assertEqual(serializer.data['term'], 24)
        self.assertEqual(serializer.data['rate'], '0.500')

    def test_two_or_more_loan(self):
        for i in range(9):
            payload = {
                "amount": i * 100,
                "term": i * 10,
                "rate": i * 1,
                "date": f'2019-01-0{i} 03:18Z'
            }
            response = client.post(path='http://localhost:8000/loans/',
                                   data=json.dumps(payload),
                                   content_type="application/json")

        self.assertEqual(is_valid_uuid(response.data['id']), True)
        loan = Loan.objects.all().filter(amount__gte=Decimal('100'))
        serializer = LoanSerializer(loan, many=True)
        self.assertGreaterEqual(serializer.data[0]['amount'], '100.00')

        loan = loan.filter(interest_rate__lte=Decimal('3'))
        serializer = LoanSerializer(loan, many=True)
        self.assertLessEqual(Decimal(serializer.data[2]['rate']), 3)

        loan = loan.filter(amount=200)
        serializer = LoanSerializer(loan, many=True)
        self.assertEqual(serializer.data[0]['amount'], '200.00')

    def test_wrong_inputs_loan(self):
        payload = {
            "amount": "%¨&%&",
            "term": "%¨&%&",
            "rate": "%¨&%&",
            "date": "%¨&%&",
        }
        response = client.post(path='http://localhost:8000/loans/',
                               data=json.dumps(payload),
                               content_type="application/json")

        self.assertEqual(response.data['amount'][0], 'A valid number is required.')
        self.assertEqual(response.data['term'][0], 'A valid integer is required.')
        self.assertEqual(response.data['rate'][0], 'A valid number is required.')
        self.assertEqual(response.data['date'][0], 'Datetime has wrong format.'
        ' Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].')

class PaymentTest(TestCase):
    def test_one_payment_made(self):
        payload_loan = {
            "amount": 1000,
            "term": 10,
            "rate": 1,
            "date": "2019-05-09 03:18Z"
        }
        response_loan = client.post(path='http://localhost:8000/loans/',
                                    data=json.dumps(payload_loan),
                                    content_type="application/json")
        payload_payment = {
            "payment": "made",
            "date": "2019-05-07 04:18Z",
            "amount": round(float(response_loan.data["installment"]), 2)
        }
        response_payment = client.post(path=f'http://localhost:8000/loans/{response_loan.data["id"]}/payments',
                                       data=json.dumps(payload_payment),
                                       content_type="application/json")

        self.assertEqual(response_payment.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_payment.data['payment_number'], 1)
        self.assertEqual(response_payment.data['payment_type'], payload_payment['payment'])
        self.assertEqual(response_payment.data['payment_amount'], str(payload_payment['amount']))
        self.assertEqual(response_payment.data['loan'], response_loan.data["id"])

        loan_payment = LoanPayment.objects.first()
        loan_payment_serializer = LoanPaymentSerializer(loan_payment)

        self.assertEqual(loan_payment_serializer.data['payment'], payload_payment['payment'])
        self.assertEqual(loan_payment_serializer.data['date'][:10], payload_payment['date'][:10])
        self.assertEqual(loan_payment_serializer.data['amount'], str(payload_payment['amount']))

    def test_two_or_more_payment_made(self):
        payload_loan = {
            "amount": 1000,
            "term": 10,
            "rate": 1,
            "date": "2019-05-09 03:18Z"
        }
        response_loan = client.post(path='http://localhost:8000/loans/',
                                    data=json.dumps(payload_loan),
                                    content_type="application/json")
        payload_payment = {
            "payment": "made",
            "date": "2019-05-07 04:18Z",
            "amount": round(float(response_loan.data["installment"]), 2)
        }
        for i in range(1, 5):
            response_payment = client.post(path=f'http://localhost:8000/loans/{response_loan.data["id"]}/payments',
                                           data=json.dumps(payload_payment),
                                           content_type="application/json")

            self.assertEqual(response_payment.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response_payment.data['payment_number'], i)
            self.assertEqual(response_payment.data['payment_type'], payload_payment['payment'])
            self.assertEqual(response_payment.data['payment_amount'], str(payload_payment['amount']))
            self.assertEqual(response_payment.data['loan'], response_loan.data["id"])



    def test_wrong_inputs_payments(self):
        payload_loan = {
            "amount": 1000,
            "term": 10,
            "rate": 1,
            "date": "2019-05-09 03:18Z"
        }
        response_loan = client.post(path='http://localhost:8000/loans/',
                                    data=json.dumps(payload_loan),
                                    content_type="application/json")
        payload_payment = {
            "payment": "%¨&%&",
            "date": "%¨&%&",
            "amount": "%¨&%&"
        }
        response_payment = client.post(path=f'http://localhost:8000/loans/{response_loan.data["id"]}/payments',
                                       data=json.dumps(payload_payment),
                                       content_type="application/json")

        self.assertEqual(response_payment.data['amount'][0], 'A valid number is required.')


class BalanceTest(TestCase):
    def test_balance(self):
        payload_loan = {
            "amount": 1000,
            "term": 10,
            "rate": 1,
            "date": "2019-05-09 03:18Z"
        }
        response_loan = client.post(path='http://localhost:8000/loans/',
                                    data=json.dumps(payload_loan),
                                    content_type="application/json")
        payload_payment = {
            "payment": "made",
            "date": "2019-05-07 04:18Z",
            "amount": round(float(response_loan.data["installment"]), 2)
        }
        response_payment = client.post(path=f'http://localhost:8000/loans/{response_loan.data["id"]}/payments',
                                       data=json.dumps(payload_payment),
                                       content_type="application/json")

        response_balance = client.post(path=f'http://localhost:8000/loans/{response_loan.data["id"]}/balance')

        self.assertEqual(response_payment.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_balance.data['balance'], (payload_loan['amount'] * payload_loan['term'])
                         - payload_payment['amount'])

