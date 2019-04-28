import uuid

from django.db import models


class Loan(models.Model):

    loan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    payment_amount = models.DecimalField(max_digits=16, decimal_places=2)
    amount_of_payments = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=4, decimal_places=3)
    requested_date = models.DateTimeField()

    class Meta:
        db_table = 'loan'
        verbose_name = 'Loan'
        verbose_name_plural = 'Loans'
    
    def __str__(self):
        return f'{self.loan_id}'


class LoanPayment(models.Model):

    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_number = models.IntegerField()
    payment_type = models.CharField(max_length=7)
    payment_date = models.DateTimeField()
    payment_amount = models.DecimalField(max_digits=16, decimal_places=2)
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='payments',
        related_query_name='payment'
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        db_table = 'loan_payment'
        verbose_name = 'Loan Payment'
        verbose_name_plural = 'Loan Payments'

    def __str__(self):
        return f'{self.payment_id}'
