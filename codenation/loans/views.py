import json

from loans.models import Loan, LoanPayment
from loans.serializers import LoanSerializer, LoanDetailSerializer, \
    LoanPaymentSerializer, LoanPaymentDetailSerializer, \
    LoanPaymentBalanceSerializer

from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class LoanAPI(APIView):
    @swagger_auto_schema(
        security=[],
        operation_description='Retrive all existing loans',
        operation_id='GET /loans',
        responses={
            200: LoanDetailSerializer(fields=('loan_id', 'amount', 'term',), many=True)
        },
    )
    def get(self, request, format=None):
        loans = Loan.objects.all()
        serializer = LoanDetailSerializer(
            loans,
            fields=('loan_id', 'amount', 'term',),
            many=True
        )
        return Response(serializer.data)
    
    @swagger_auto_schema(
        request_body=LoanSerializer(),
        security=[],
        operation_description='Create a loan',
        operation_id='POST /loans',
        responses={
            201: openapi.Response(
                    description='Loan has been created',
                    examples={
                        'created': json.dumps({
                            'id': openapi.TYPE_STRING,
                            'installment': openapi.TYPE_NUMBER
                            }
                        )
                    }
                ),
            400: openapi.Response(
                description='Fields are invalid',
                examples={
                    'field_required': json.dumps([{'field': 'This field is required'}]),
                    'field_wrong': json.dumps([{'field': 'Reason of the error'}])
                }
            )
        }
    )
    def post(self, request, format=None):
        loan_order = LoanSerializer(data=request.data)
        if loan_order.is_valid():
            loan = loan_order.save()
            return Response(
                data={
                    'id': loan.loan_id,
                    'installment': loan.payment_amount,
                },
                status=status.HTTP_201_CREATED)
        return Response(loan_order.errors, status=status.HTTP_400_BAD_REQUEST)


class LoanDetailAPI(APIView):
    @swagger_auto_schema(
        security=[],
        operation_description='Retrive loan with its details',
        operation_id='GET /loans/{loan_id}',
        responses={
            200: LoanDetailSerializer(),
            404: openapi.Response(
                description='Loan not found',
                examples={
                    'not_found': json.dumps({'detail': 'Not Found.'})
                }
            )
        }
    )
    def get(self, request, loan_id, format=None):
        loan = get_object_or_404(Loan, loan_id=loan_id)
        return Response(LoanDetailSerializer(loan).data)


class LoanPaymentApi(APIView):
    def _get_loan(self, loan_id):
        return get_object_or_404(Loan, loan_id=loan_id)

    def _get_loan_payments(self, loan_id):
        return LoanPayment.objects.filter(loan=loan_id)

    def _get_payment_count(self, loan):
        return self._get_loan_payments(loan).count()

    def _verify_number_of_payments(self, loan):
        payments_count = self._get_payment_count(loan)
        if payments_count < loan.amount_of_payments:
            return payments_count
        return -1
    
    def _get_errors(self, loan, payment_order):
        payments_count = self._verify_number_of_payments(loan)
        if payments_count == -1:
            return Response(
                {'error': 'The Loan does not have payments to be effectuated'},
                status=status.HTTP_412_PRECONDITION_FAILED
            )
        
        if loan.payment_amount != payment_order.validated_data['payment_amount']:
            return Response(
                {'error': 'Payment amount is different from original value'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if payment_order.validated_data['payment_type'] not in ['made', 'missed']:
            return Response(
                {'error': 'The field "payment" must be "made" or "missed"'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        security=[],
        operation_description='Retrive payments from a especific loan',
        operation_id='GET /loans/{loan_id}/payments',
        responses={
            200: LoanPaymentDetailSerializer(many=True)
        }
    )
    def get(self, request, loan_id, format=None):
        loan_payments = self._get_loan_payments(loan_id)
        return Response(LoanPaymentDetailSerializer(loan_payments, many=True).data)

    @swagger_auto_schema(
        security=[],
        operation_description='Crete Loan Payment',
        operation_id='POST /loans/{loan_id}',
        responses={
            201: LoanPaymentDetailSerializer(),
            400: openapi.Response(
                description='Fields are invalid',
                examples={
                    'field_required': json.dumps([{'field': 'This field is required'}]),
                    'field_wrong': json.dumps([{'field': 'Reason of the error'}])
                }
            )
        }
    )
    def post(self, request, loan_id, format=None):
        payment_order = LoanPaymentSerializer(data=request.data)
        if payment_order.is_valid():
            loan = self._get_loan(loan_id)
            errors = self._get_errors(loan, payment_order)

            if errors:
                return errors
            
            payment = payment_order.save(
                loan=loan,
                payment_number=self._get_payment_count(loan) + 1
            )
            return Response(LoanPaymentDetailSerializer(payment).data, status=status.HTTP_201_CREATED)
        return Response(payment_order.errors, status=status.HTTP_400_BAD_REQUEST)


class LoanPaymentBalanceApi(APIView):
    def _get_loan(self, loan_id):
        return get_object_or_404(Loan, loan_id=loan_id)
    
    def _get_paid_loan_amount(self, loan, date):
        paid_loan = LoanPayment.objects.filter(loan=loan) \
            .exclude(payment_date__gte=date) \
            .aggregate(paid_amount=Sum('payment_amount'))['paid_amount']
        return paid_loan or 0

    @swagger_auto_schema(
        security=[],
        operation_description='Crete Loan Payment',
        operation_id='POST /loans/{loan_id}/balance',
        request_body=LoanPaymentBalanceSerializer(),
        responses={
            201: openapi.Response(
                description='Loan Payments\' balance',
                examples={
                    'balance': json.dumps({'balance': openapi.TYPE_NUMBER})
                }
            ),
            404: openapi.Response(
                description='Loan not found',
                examples={
                    'not_found': json.dumps({'detail': 'Not Found.'})
                }
            )
        }
    )
    def post(self, request, loan_id, format=None):
        loan = self._get_loan(loan_id)
        data = LoanPaymentBalanceSerializer(request.data).data
        paid_amount = self._get_paid_loan_amount(loan, data['date'])
        return Response({
                'balance': (loan.payment_amount * loan.amount_of_payments) - paid_amount
                },
                status=status.HTTP_201_CREATED)
