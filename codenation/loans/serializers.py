from loans.models import Loan, LoanPayment
from rest_framework import serializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    '''
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    '''

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class LoanSerializer(serializers.ModelSerializer):

    amount = serializers.DecimalField(max_digits=16, decimal_places=2)
    term = serializers.IntegerField(source='amount_of_payments')
    rate = serializers.DecimalField(max_digits=4, decimal_places=3, source='interest_rate')
    date = serializers.DateTimeField(source='requested_date')
    
    class Meta:
        model = Loan
        fields = ('amount', 'term', 'rate', 'date',)
    
    def create(self, validated_data):
        loan = Loan(**validated_data)
        loan.payment_amount = round(self.__calculate_payment_amount(loan), 4)
        loan.save()
        return loan

    def __calculate_payment_amount(self, loan):
        rate = loan.interest_rate / 12
        return (rate + rate / ((1 + rate) ** loan.amount_of_payments - 1)) * loan.amount


class LoanPaymentSerializer(serializers.ModelSerializer):

    payment = serializers.CharField(source='payment_type')
    date = serializers.DateTimeField(source='payment_date')
    amount = serializers.DecimalField(max_digits=16, decimal_places=2, source='payment_amount')

    class Meta:
        model = LoanPayment
        fields = ('payment', 'date', 'amount',)


class LoanPaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanPayment
        fields = '__all__'


class LoanDetailSerializer(LoanSerializer, DynamicFieldsModelSerializer):

    loan_id = serializers.UUIDField()
    payments = LoanPaymentDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = Loan
        fields = ('loan_id', 'payment_amount',) + LoanSerializer.Meta.fields + ('payments',)
