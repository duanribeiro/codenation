import uuid

from django.db import models


class Client(models.Model):

    client_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=15)
    surname = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    telephone = models.CharField(max_length=11)
    cpf = models.CharField(max_length=11, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        db_table = 'client'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
    
    def __str__(self):
        return f'{self.surname}, {self.name} - {self.cpf}'
