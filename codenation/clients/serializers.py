import re

from clients.models import Client
from codenation.utils.serializers import DynamicFieldsModelSerializer
from rest_framework import serializers

from pycpfcnpj import cpfcnpj


class ClientSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Client
        fields = ('name', 'surname', 'email', 'telephone', 'cpf',)
    
    def validate_cpf(self, value):
        if not cpfcnpj.validate(value):
            raise serializers.ValidationError('Invalid CPF.')
        return value
    
    def validate_email(self, value):
        if re.fullmatch(r'^[-\.\w]+@{1}\w+(\.[a-zA-Z]{1,3}){1,2}$', email):
            raise serializers.ValidationError('Invalid email.')
        return value


class ClientDetailSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = Client
        fields = (
            'client_id', 'name', 'surname', 'email',
            'telephone', 'cpf', 'created_at',
        )
