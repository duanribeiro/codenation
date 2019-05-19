import json

from decimal import Decimal

from loans.models import Loan, LoanPayment
from clients.models import Client
from loans.serializers import LoanSerializer, LoanDetailSerializer, \
    LoanPaymentSerializer, LoanPaymentDetailSerializer, \
    LoanPaymentBalanceSerializer
from codenation.exceptions import ClientNoLongerCanMakeLoan

from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Case, When, IntegerField, F
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class LoanAPI(APIView):
    def __get_loans_payments_by_paid_loan_queryset(self, client_id):
        return LoanPayment \
            .objects \
            .values('loan', 'loan__amount_of_payments') \
            .annotate(
                made_payments=Sum(
                    Case(
                        When(payment_type='made', then=1),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                missed_payments=Sum(
                    Case(
                        When(payment_type='missed', then=1),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                received_payments=Count('payment_id')
            ) \
            .filter(loan__client=client_id) \
            .filter(received_payments=F('loan__amount_of_payments'))
    
    def __client_has_more_than_three_missed_payment_per_loan(self, client_id):
        queryset = self.__get_loans_payments_by_paid_loan_queryset(client_id) \
            .filter(missed_payments__gt=3)
        return queryset.count() != 0
    
    def __client_has_less_than_or_equal_three_missed_payment_per_loan(self, client_id):
        queryset = self.__get_loans_payments_by_paid_loan_queryset(client_id) \
            .filter(missed_payments__range=(1, 3))
        return queryset.count() != 0
    
    def __client_no_has_missed_payments(self, client_id):
        queryset = self.__get_loans_payments_by_paid_loan_queryset(client_id) \
            .filter(missed_payments__gt=0)
        return queryset.count() == 0
    
    def validate_loan_to_client(self, client_id):
        client = get_object_or_404(Client, client_id=client_id)
        if self.__client_has_more_than_three_missed_payment_per_loan(client):
            raise ClientNoLongerCanMakeLoan()
        return client
    
    def apply_rate_modification(self, rate, client_id):
        if self.__client_has_less_than_or_equal_three_missed_payment_per_loan(client_id):
            return rate * Decimal(1.04)
        elif self.__client_no_has_missed_payments(client_id):
            return rate * Decimal(0.98)
        return rate
    
    def calculate_payment_amount(self, loan):
        rate = self.apply_rate_modification(loan['interest_rate'] / 12, loan['client'])
        return (rate + rate / ((1 + rate) ** loan['amount_of_payments'] - 1)) * loan['amount']

    @swagger_auto_schema(
        security=[],
        operation_description='Retrive all existing loans',
        operation_id='GET /loans',
        manual_parameters=[
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, default=1,
                type=openapi.TYPE_INTEGER, description='Page number'),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, default=50,
                type=openapi.TYPE_INTEGER, description='Number of page elements'),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description='Loans list',
                examples={
                    'application/json': {
                        'count': openapi.TYPE_INTEGER,
                        'next': openapi.TYPE_STRING,
                        'previous': openapi.TYPE_STRING,
                        'results': [{
                            'loan_id': openapi.FORMAT_UUID,
                            'amount': openapi.TYPE_NUMBER,
                            'term': openapi.TYPE_INTEGER,
                        }]
                    }
                }
            )
        },
    )
    def get(self, request, format=None):
        paginator = api_settings.DEFAULT_PAGINATION_CLASS()
        return paginator.get_paginated_response(
            queryset=Loan.objects.all(),
            request=request,
            serializer=LoanDetailSerializer,
            serializer_kwargs={
                'fields': ('loan_id', 'amount', 'term', 'client_id', )
            }
        )
    
    @swagger_auto_schema(
        request_body=LoanSerializer(),
        security=[],
        operation_description='Create a loan',
        operation_id='POST /loans',
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                    description='Loan has been created',
                    examples={
                        'application/json': {
                            'id': openapi.FORMAT_UUID,
                            'installment': openapi.TYPE_NUMBER
                        }
                    }
                ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Fields are invalid',
                examples={
                    'application/json_required': [{
                        'field': 'This field is required'
                    }],
                    'application/json_wrong': [{
                        'field': 'Reason of the error'
                    }]
                }
            )
        }
    )
    def post(self, request, format=None):
        loan_order = LoanSerializer(data=request.data)
        if loan_order.is_valid():
            client = self.validate_loan_to_client(
                loan_order.validated_data['client']
            )
            loan = loan_order.save(
                client=client,
                payment_amount=self.calculate_payment_amount(
                    loan_order.validated_data
                )
            )
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
            status.HTTP_200_OK: LoanDetailSerializer(),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description='Loan not found',
                examples={
                    'application/json': {'detail': 'Not Found.'}
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
            status.HTTP_200_OK: LoanPaymentDetailSerializer(many=True)
        }
    )
    def get(self, request, loan_id, format=None):
        loan_payments = self._get_loan_payments(loan_id)
        return Response(LoanPaymentDetailSerializer(loan_payments, many=True).data)

    @swagger_auto_schema(
        request_body=LoanPaymentSerializer(),
        security=[],
        operation_description='Crete Loan Payment',
        operation_id='POST /loans/{loan_id}/payments',
        responses={
            status.HTTP_201_CREATED: LoanPaymentDetailSerializer(),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Fields are invalid',
                examples={
                    'application/json_required': [{
                        'field_name': 'This field is required'
                    }],
                    'application/json_wrong': [{
                        'field_name': 'Reason of the error'
                    }]
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
            status.HTTP_201_CREATED: openapi.Response(
                description='Loan Payments\' balance',
                examples={
                    'application/json_balance': {
                        'balance': openapi.TYPE_NUMBER
                    }
                }
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description='Loan not found',
                examples={
                    'application/json_not_found': {
                        'detail': 'Not Found.'
                    }
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
