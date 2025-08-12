# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UsuarioPersonalizado

class FormularioRegistroPersonalizado(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = UsuarioPersonalizado
        fields = [
            'username', 'nombre', 'apellido', 'email', 'telefono',
            'pais',  'password1', 'password2'
        ]
        widgets = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UsuarioPersonalizado.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario con ese correo electrónico.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if UsuarioPersonalizado.objects.filter(username=username).exists():
            raise forms.ValidationError("Ya existe un usuario con ese nombre de usuario.")
        return username
