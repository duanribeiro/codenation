from loans.models import Loan
from rest_framework import serializers


class LoanSerializer(serializers.ModelSerializer):
    
    amount = serializers.DecimalField(max_digits=16, decimal_places=2)
    term = serializers.IntegerField(source='installment_amount')
    rate = serializers.DecimalField(max_digits=4, decimal_places=3, source='interest_rate')
    date = serializers.DateTimeField(source='requested_date')
    
    class Meta:
        model = Loan
        fields = ('amount', 'term', 'rate', 'date',)
