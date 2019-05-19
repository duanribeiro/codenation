class BasicData:

    model = None

    def __init__(self, pk, fields):
        self.pk = pk
        self.fields = fields
    
    def __dict__(self):
        return {
            'model': self.model,
            'pk': self.pk,
            'fields': self.fields
        }


class Loan(BasicData):

    model = 'loans.loan'


class LoanPayment(BasicData):

    model = 'loans.loanpayment'


class Client(BasicData):

    model = 'clients.client'
