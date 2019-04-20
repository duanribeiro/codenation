from django.urls import path

from loan_system.api.views import MakeLoan

urlpatterns = [
    path('', MakeLoan),
]
