from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.utils.timezone import now
from django_countries.widgets import CountrySelectWidget

from .models import UsuarioPersonalizado, Reserva, ViajeXNavio, Cliente, Rol, TipoCamarote, Camarote


INPUT_BASE_CLASSES = (
    "form-control p-2 rounded-lg bg-surface/60 text-text border border-primary/40 "
    "focus:outline-none focus:ring-2 focus:ring-primary/60 focus:border-primary "
    "placeholder:text-text/60 w-full"
)


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
                "class": INPUT_BASE_CLASSES,
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
                "class": INPUT_BASE_CLASSES,
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
            "class": INPUT_BASE_CLASSES,
            "placeholder": "Contraseña actual"
        })
    )
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={
            "class": INPUT_BASE_CLASSES,
            "placeholder": "Nueva contraseña"
        })
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={
            "class": INPUT_BASE_CLASSES,
            "placeholder": "Confirmar nueva contraseña"
        })
    )
class FormularioReserva(forms.ModelForm):
    tipo_camarote = forms.ModelChoiceField(
        queryset=TipoCamarote.objects.none(),
        required=False,
        label="Tipo de camarote"
    )
    capacidad = forms.ChoiceField(
        choices=[],
        required=False,
        label="Capacidad"
    )
    camarote = forms.ModelChoiceField(
        queryset=Camarote.objects.none(),
        required=False,
        label="Número de camarote"
    )
    pasajeros = forms.ModelMultipleChoiceField(
        queryset=Cliente.objects.none(),
        required=True,
        label="Pasajeros (seleccioná hasta la capacidad)",
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Reserva
        fields = ["viaje_navio", "cliente","camarote"]  # camarote lo seteamos en form_valid
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # estilos consistentes (si querés podés copiar el estilo que ya tenías)
        for field in self.fields.values():
            try:
                field.widget.attrs.update({
                    "class": INPUT_BASE_CLASSES,
                })
            except Exception:
                pass

        # limitar viajes a futuros
        self.fields["viaje_navio"].queryset = (
            ViajeXNavio.objects.select_related("viaje", "navio")
            .filter(viaje__fecha_de_salida__gte=now().date())
            .order_by("viaje__fecha_de_salida")
        )
        self.fields["viaje_navio"].label = "Viaje"

        # clientes del usuario
        if user:
            self.fields["cliente"].queryset = Cliente.objects.filter(usuario=user)
            self.fields["pasajeros"].queryset = Cliente.objects.filter(usuario=user)

        # dejar campos vacíos para que JS los cargue
        self.fields["tipo_camarote"].queryset = TipoCamarote.objects.all()
        self.fields["capacidad"].choices = [(1,"1"), (2,"2"), (4,"4")]
        # camarote queryset se llenará por JS según filtros

    def clean(self):
        cleaned = super().clean()
        viaje_navio = cleaned.get("viaje_navio")
        camarote = cleaned.get("camarote")
        pasajeros = cleaned.get("pasajeros")
        if not viaje_navio:
            raise forms.ValidationError("Seleccioná un viaje.")
        if camarote:
            # verificar que camarote pertenezca al navío del viaje
            if camarote.cubierta.navio != viaje_navio.navio:
                raise forms.ValidationError("El camarote seleccionado no pertenece al navío de ese viaje.")
            # capacidad
            if pasajeros and len(pasajeros) > camarote.capacidad:
                raise forms.ValidationError(f"Seleccionaste {len(pasajeros)} pasajeros; el camarote admite {camarote.capacidad}.")
        return cleaned

class FormularioCliente(forms.ModelForm):
    nacionalidad = forms.ChoiceField(
        choices=Cliente._meta.get_field('nacionalidad').get_choices(),
        widget=forms.Select(attrs={
            'class': INPUT_BASE_CLASSES,
        }),
        label='Nacionalidad',
    )

    class Meta:
        model = Cliente
        exclude = ['usuario']  # se asigna automáticamente en la vista

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': INPUT_BASE_CLASSES,
                'placeholder': 'Nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': INPUT_BASE_CLASSES,
                'placeholder': 'Apellido'
            }),
            'dni': forms.TextInput(attrs={
                'class': INPUT_BASE_CLASSES,
                'placeholder': 'DNI'
            }),
            'direccion': forms.TextInput(attrs={
                'class': INPUT_BASE_CLASSES,
                'placeholder': 'Dirección'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': INPUT_BASE_CLASSES,
                'type': 'date'
            }),
            'genero': forms.Select(attrs={
                'class': INPUT_BASE_CLASSES
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
