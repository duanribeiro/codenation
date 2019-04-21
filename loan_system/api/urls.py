from django.urls import path

from loan_system.api.views import MakeLoan, MakePayment, ListBalance

urlpatterns = [
    path('', MakeLoan),
    path('<str:loan_id>/payments', MakePayment),
    path('<str:loan_id>/balance', ListBalance)
]
