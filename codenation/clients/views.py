from clients.models import Client
from clients.serializers import ClientSerializer

from rest_framework import status
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ClientApi(APIView):

    def get(self, request, format=None):
        paginator = api_settings.DEFAULT_PAGINATION_CLASS()
        return paginator.get_paginated_response(
            queryset=Client.objects.all(),
            request=request,
            serializer=ClientSerializer,
        )
    
    def post(self, request, format=None):
        client = ClientSerializer(data=request.data)
        if client.is_valid():
            client = client.save()
            return Response(
                data={
                    'client_id': client.client_id,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(client.errors, status=status.HTTP_400_BAD_REQUEST)
