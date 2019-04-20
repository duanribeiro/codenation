from django.contrib import admin

from loan_system.api.models import Loan, Payment

admin.site.register(Loan)
admin.site.register(Payment)