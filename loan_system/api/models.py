from django.db import models

class Payment(models.Model):
    date = models.DateField()
    type = models.CharField(max_length=4)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    rate = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return "{} - {}".format(self.type, self.amount)

class Loan(models.Model):
    id = models.CharField(max_length=18, primary_key=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    rate = models.DecimalField(max_digits=3, decimal_places=2)
    date_start = models.DateField()
    date_end = models.DateField()
    payments =  models.ForeignKey(Payment)

    def __str__(self):
        return "{} - {}".format(self.id, self.amount)