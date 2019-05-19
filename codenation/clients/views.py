from clients.models import Client
from clients.serializers import ClientSerializer, ClientDetailSerializer

from django.shortcuts import get_object_or_404
from rest_framework import status
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ClientApi(APIView):
    @swagger_auto_schema(
        security=[],
        operation_description='Retrive all existing clients',
        operation_id='GET /clients',
        manual_parameters=[
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, default=1,
                type=openapi.TYPE_INTEGER, description='Page number'),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, default=50,
                type=openapi.TYPE_INTEGER, description='Number of page elements'),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description='Clients list',
                examples={
                    'application/json': {
                        'count': openapi.TYPE_INTEGER,
                        'next': openapi.TYPE_STRING,
                        'previous': openapi.TYPE_STRING,
                        'results': [{
                            'client_id': openapi.FORMAT_UUID,
                            'name': openapi.TYPE_STRING,
                            'cpf': openapi.TYPE_STRING,
                        }]
                    }
                }
            )
        },
    )
    def get(self, request, format=None):
        paginator = api_settings.DEFAULT_PAGINATION_CLASS()
        return paginator.get_paginated_response(
            queryset=Client.objects.all(),
            request=request,
            serializer=ClientDetailSerializer,
            serializer_kwargs={
                'fields': ('client_id', 'name', 'cpf',)
            }
        )
    
    @swagger_auto_schema(
        request_body=ClientSerializer(),
        security=[],
        operation_description='Create a client',
        operation_id='POST /clients',
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                    description='Client has been created',
                    examples={
                        'application/json': {
                            'client_id': openapi.FORMAT_UUID
                        }
                    }
                ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Fields are invalid',
                examples={
                    'application/json_required': [{
                        'field': 'This field is required'
                    }],
                    'application/json_wrong': [{
                        'field': 'Reason of the error'
                    }]
                }
            )
        }
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


class ClientDetailApi(APIView):
    @swagger_auto_schema(
        security=[],
        operation_description='Retrive client with its details',
        operation_id='GET /clients/{client_id}',
        responses={
            status.HTTP_200_OK: ClientDetailSerializer(),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description='Client not found',
                examples={
                    'application/json': {'detail': 'Not Found.'}
                }
            )
        }
    )
    def get(self, request, client_id, format=None):
        client = get_object_or_404(Client, client_id=client_id)
        return Response(ClientDetailSerializer(client).data)
