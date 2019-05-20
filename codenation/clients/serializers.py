from clients.models import Client
from codenation.utils.serializers import DynamicFieldsModelSerializer

from rest_framework import serializers
from validate_email import validate_email
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
        if not validate_email(value):
            raise serializers.ValidationError('Invalid email.')
        return value


class ClientDetailSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = Client
        fields = (
            'client_id', 'name', 'surname', 'email',
            'telephone', 'cpf', 'created_at',
        )
