import uuid

from django.db import models


class Loan(models.Model):

    loan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    installment_amount = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=4, decimal_places=3)
    requested_date = models.DateTimeField()

    class Meta:
        verbose_name = 'Loan'
        verbose_name_plural = 'Loans'
    
    def __str__(self):
        return f'{self.loan_id}'
