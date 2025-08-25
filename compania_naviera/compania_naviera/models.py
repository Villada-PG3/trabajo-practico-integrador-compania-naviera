from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class UsuarioPersonalizado(AbstractUser):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    pais = models.CharField(max_length=50, blank=True)
    

    def __str__(self):
        return self.username
