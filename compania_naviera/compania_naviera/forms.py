from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import UsuarioPersonalizado, Reserva, ViajeXNavio
from django.utils.timezone import now

class FormularioRegistroPersonalizado(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = UsuarioPersonalizado
        fields = [
            'username', 'nombre', 'apellido', 'email', 'telefono',
            'pais', 'password1', 'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asignar clase y placeholder a todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "form-control p-2 rounded-lg bg-white/10 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-orange-400 w-full",
                "placeholder": field.label
            })

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
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if UsuarioPersonalizado.objects.filter(telefono=telefono).exists():
            raise forms.ValidationError("Ya existe un usuario con ese número de teléfono.")
        return telefono
    

class FormularioEdicionPerfil(forms.ModelForm):
    class Meta:
        model = UsuarioPersonalizado
        fields = ['username', 'nombre', 'apellido', 'email', 'telefono', 'pais']

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

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if UsuarioPersonalizado.objects.filter(telefono=telefono).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un usuario con ese número de teléfono.")
        return telefono
    


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
        # usar los campos reales del modelo
        fields = ["descripcion", "viaje_navio"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # estilo consistente con el resto de tus forms
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "form-control p-2 rounded-lg bg-white/10 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-orange-400 w-full",
                "placeholder": field.label
            })

        # limitar la lista de viajes a los próximos (opcional pero útil)
        if "viaje_navio" in self.fields:
            self.fields["viaje_navio"].queryset = (
                ViajeXNavio.objects.select_related("viaje", "navio")
                .filter(viaje__fecha_de_salida__gte=now().date())
                .order_by("viaje__fecha_de_salida")
            )
            self.fields["viaje_navio"].label = "Viaje y Navío"