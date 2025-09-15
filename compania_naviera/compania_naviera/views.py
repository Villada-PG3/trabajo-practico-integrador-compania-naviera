from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.utils.timezone import now

from .forms import *
from .models import *
from django.views.generic import ListView


class DestinosListView(ListView):
    model = Puerto
    template_name = "destinos.html"
    context_object_name = "destinos"

    def get_queryset(self):
        return Puerto.objects.prefetch_related('actividades').all()


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

def main_view(request):
    logout(request)
    proximos_viajes = Viaje.objects.filter(
        fecha_de_salida__gte=now().date()
    ).order_by('fecha_de_salida')[:6]

    return render(request, 'inicio.html', {
        'proximos_viajes': proximos_viajes
    })


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
    cruceros = Navio.objects.all()
    return render(request, 'cruceros.html', {'cruceros': cruceros})

def navio_detail_view(request, pk):
    navio = get_object_or_404(Navio, pk=pk)
    return render(request, 'navio_detail.html', {'navio': navio})

def contacto_log_view(request):
    return render (request, "contacto_log.html")

def ofertas_view(request):
    # Traemos solo viajes futuros
    ofertas = ViajeXNavio.objects.filter(viaje__fecha_de_salida__gte=now()).select_related('navio', 'viaje')
    return render(request, 'ofertas.html', {'ofertas': ofertas})


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

@login_required
def crear_reserva(request):
    cliente = None
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        pass  # no redirigir, cliente seguirá siendo None

    if request.method == 'POST':
        form = FormularioReserva(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            if cliente:  # asigna solo si hay cliente
                reserva.cliente = cliente
            reserva.save()
            messages.success(request, "Reserva creada con éxito.")
            return redirect('mis_reservas')
    else:
        form = FormularioReserva()

    return render(request, 'crear_reserva.html', {'form': form})

@login_required
def mis_reservas(request):
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        reservas = Reserva.objects.filter(cliente=cliente).select_related('viaje_navio', 'estado_reserva')
    except Cliente.DoesNotExist:
        reservas = Reserva.objects.none()

    return render(request, 'mis_reservas.html', {'reservas': reservas})

