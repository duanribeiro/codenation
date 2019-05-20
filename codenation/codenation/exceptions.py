from rest_framework import status
from rest_framework.exceptions import APIException


class ClientNoLongerCanMakeLoan(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Client has more than three missed payments per loan'
    default_code = 'client_error'
