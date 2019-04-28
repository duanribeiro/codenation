import json
from decimal import Decimal

from django.test import TestCase, Client
from rest_framework import status

from loans.models import Loan
from loans.serializers import LoanSerializer

client = Client()

class GetLoanTest(TestCase):
    def test_empty_db(self):
        response = client.get('http://127.0.0.1:8000/loans/')

        self.assertEqual(response.data, [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_one_loan(self):
        payload = {
            "amount": 5000,
            "term": 24,
            "rate": 0.5,
            "date": "2019-05-09 03:18Z"
        }
        client.post('http://127.0.0.1:8000/loans/', data=json.dumps(payload), content_type="application/json")
        loan = Loan.objects.first()
        serializer = LoanSerializer(loan)

        self.assertEqual(serializer.data['amount'], '5000.00')
        self.assertEqual(serializer.data['term'], 24)
        self.assertEqual(serializer.data['rate'], '0.500')
        self.assertEqual(serializer.data['date'], '2019-05-09T03:18:00Z')

    def test_two_or_more_loan(self):
        for i in range(9):
            payload = {
                "amount": i * 100,
                "term": i * 10,
                "rate": i * 1,
                "date": f'2019-01-0{i} 03:18Z'
            }
            client.post('http://127.0.0.1:8000/loans/', data=json.dumps(payload), content_type="application/json")

        loan = Loan.objects.filter(amount__gte=Decimal("100"))
        serializer = LoanSerializer(loan, many=True)
        self.assertGreaterEqual(serializer.data[0]['amount'], '100.00')
