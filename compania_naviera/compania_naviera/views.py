from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.utils.timezone import now

from .forms import FormularioRegistroPersonalizado, FormularioEdicionPerfil, FormularioCambioContrasenia
from .models import UsuarioPersonalizado, Viaje,ItinerarioViaje

def destinos_view(request):
    destinos = ItinerarioViaje.objects.prefetch_related('Viaje').all()
    return render(request, 'destinos.html', {'destinos': destinos})


@login_required
def cambiar_contrasenia(request):
    if request.method == 'POST':
        form = FormularioCambioContrasenia(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Mantener sesión activa
            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect('menu_user')
        else:
            messages.error(request, "Por favor corrige los errores.")
    else:
        form = FormularioCambioContrasenia(user=request.user)

    return render(request, 'cambiar_contrasenia.html', {'form': form})

from django.shortcuts import render
from django.contrib.auth import logout
from django.utils.timezone import now
from .models import Viaje

def main_view(request):
    logout(request)  
    cruceros = (
        Viaje.objects.filter(fecha_de_salida__gte=now())
        .order_by('fecha_de_salida')[:6]
    )

    return render(request, 'inicio.html', {'cruceros': cruceros})


class RegistroUsuario(CreateView):
    form_class = FormularioRegistroPersonalizado
    template_name = 'registro.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Usuario registrado correctamente. Inicia sesión.")
        return response

def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username') or request.POST.get('email')
        password = request.POST.get('password')

        # Intentamos autenticar por username
        user = authenticate(request, username=username_or_email, password=password)

        # Si falla, intentamos autenticar por email
        if user is None:
            try:
                usuario = UsuarioPersonalizado.objects.get(email=username_or_email)
                user = authenticate(request, username=usuario.username, password=password)
            except UsuarioPersonalizado.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            return redirect('menu_user')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'inicio_sesion.html')

@login_required
def menu_user(request):
    return render(request, 'menu_user.html', {'usuario': request.user})

def contacto_view(request):
    return render(request, 'contacto.html')

def cruceros_view(request):
    return render(request, 'cruceros.html')


def contacto_log_view(request):
    return render (request, "contacto_log.html")

def ofertas_view(request):
    return render(request, 'ofertas.html')

def cruceros_view(request):
    return render(request, 'crucero.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('home')  # o main_view

def editar_perfil(request):
    if request.method == 'POST':
        form = FormularioEdicionPerfil(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('menu_user')
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = FormularioEdicionPerfil(instance=request.user)
    return render(request, 'editar_perfil.html', {'form': form})
