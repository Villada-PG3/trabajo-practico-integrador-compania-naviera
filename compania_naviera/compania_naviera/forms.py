from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.utils.timezone import now
from django_countries.widgets import CountrySelectWidget

from .models import UsuarioPersonalizado, Reserva, ViajeXNavio, Cliente, Rol


class FormularioRegistroPersonalizado(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = UsuarioPersonalizado
        fields = ['username', 'email', 'password1', 'password2']  # SOLO los campos del modelo

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Asignar clase base a todos los campos
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control p-2 rounded-lg bg-white/10 text-white border border-white/30 "
                         "focus:outline-none focus:ring-2 focus:ring-orange-400 w-full",
            })

        # Etiquetas
        self.fields['username'].label = "Nombre de usuario"
        self.fields['email'].label = "Correo electrónico"
        self.fields['password1'].label = "Contraseña"
        self.fields['password2'].label = "Confirmar contraseña"

        # Placeholders
        placeholders = {
            'username': "Nombre de usuario",
            'email': "Correo electrónico",
            'password1': "Contraseña",
            'password2': "Confirmar contraseña",
        }
        for field_name, placeholder in placeholders.items():
            self.fields[field_name].widget.attrs["placeholder"] = placeholder

        # Eliminar textos de ayuda largos en contraseñas
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

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

    def save(self, commit=True):
        user = super().save(commit=False)
        # Asignar automáticamente el rol "cliente"
        try:
            rol_cliente = Rol.objects.get(nombre="cliente")
        except Rol.DoesNotExist:
            rol_cliente = None  # o podrías crearlo automáticamente
        user.rol = rol_cliente
        if commit:
            user.save()
        return user
    

class FormularioEdicionPerfil(forms.ModelForm):
    class Meta:
        model = UsuarioPersonalizado
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "form-control p-2 rounded-lg bg-white/10 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-orange-400 w-full",
                "placeholder": field.label
            })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UsuarioPersonalizado.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un usuario con ese correo electrónico.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if UsuarioPersonalizado.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un usuario con ese nombre de usuario.")
        return username


class FormularioCambioContrasenia(PasswordChangeForm):
    old_password = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput(attrs={
            "class": "form-control p-2 rounded-lg bg-white/10 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-orange-400 w-full",
            "placeholder": "Contraseña actual"
        })
    )
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-control p-2 rounded-lg bg-white/10 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-orange-400 w-full",
            "placeholder": "Nueva contraseña"
        })
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-control p-2 rounded-lg bg-white/10 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-orange-400 w-full",
            "placeholder": "Confirmar nueva contraseña"
        })
    )
class FormularioReserva(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ["viaje_navio", "cliente"]  # descripción la generamos sola

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # estilos consistentes
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control p-2 rounded-lg bg-white text-black border border-gray-300 w-full",
            })

        # limitar viajes a futuros
        self.fields["viaje_navio"].queryset = (
            ViajeXNavio.objects.select_related("viaje", "navio")
            .filter(viaje__fecha_de_salida__gte=now().date())
            .order_by("viaje__fecha_de_salida")
        )
        self.fields["viaje_navio"].label = "Viaje"

        # limitar clientes al usuario actual
        if user:
            self.fields["cliente"].queryset = Cliente.objects.filter(usuario=user)

    def clean(self):
        cleaned_data = super().clean()
        viaje_navio = cleaned_data.get("viaje_navio")
        cliente = cleaned_data.get("cliente")

        if not viaje_navio:
            raise forms.ValidationError("Debes seleccionar un viaje.")
        if not cliente:
            raise forms.ValidationError("Debes seleccionar un cliente.")

        return cleaned_data

class FormularioCliente(forms.ModelForm):
    nacionalidad = forms.ChoiceField(
        choices=Cliente._meta.get_field('nacionalidad').get_choices(),
        widget=forms.Select(attrs={
            'class': 'form-control p-2 rounded-lg bg-white text-black border border-gray-300 w-full',
        }),
        label='Nacionalidad',
    )

    class Meta:
        model = Cliente
        exclude = ['usuario']  # se asigna automáticamente en la vista

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control p-2 rounded-lg bg-white text-black border border-gray-300 w-full',
                'placeholder': 'Nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control p-2 rounded-lg bg-white text-black border border-gray-300 w-full',
                'placeholder': 'Apellido'
            }),
            'dni': forms.TextInput(attrs={
                'class': 'form-control p-2 rounded-lg bg-white text-black border border-gray-300 w-full',
                'placeholder': 'DNI'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control p-2 rounded-lg bg-white text-black border border-gray-300 w-full',
                'placeholder': 'Dirección'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control p-2 rounded-lg bg-white text-black border border-gray-300 w-full',
                'type': 'date'
            }),
            'genero': forms.Select(attrs={
                'class': 'form-control p-2 rounded-lg bg-white text-black border border-gray-300 w-full'
            }),
        }

        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'dni': 'DNI',
            'direccion': 'Dirección',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'genero': 'Género',
        }