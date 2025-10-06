from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    # Usando 'email' como username
    email = models.EmailField(unique=True)  # Tornar o e-mail único
    cpf = models.TextField(null=False, blank=True)
    birth_date = models.DateField(null=False, blank=True)
    phone = models.TextField(null=False, blank=True)
    

    def __str__(self):
        return self.email
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_set',  # Renomeando o reverse accessor para evitar o conflito
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_permissions_set',  # Renomeando o reverse accessor para evitar o conflito
        blank=True
    )
    def __str__(self):
        return super().__str__()