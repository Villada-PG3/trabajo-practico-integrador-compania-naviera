# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class UsuarioPersonalizado(AbstractUser):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    pais = models.CharField(max_length=50, blank=True)
    metodo_pago = models.CharField(
        max_length=30,
        choices=[
            ('tarjeta', 'Tarjeta de crédito/débito'),
            ('paypal', 'PayPal'),
            ('transferencia', 'Transferencia bancaria'),
            ('mercadopago', 'Mercado Pago'),  
        ],
        blank=True
    )

    # Evitar conflicto con auth.User
    groups = models.ManyToManyField(
        Group,
        related_name="usuario_personalizado_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="usuario_personalizado_permissions_set",
        blank=True
    )

    def __str__(self):
        return self.username
