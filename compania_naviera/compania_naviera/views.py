from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import FormularioRegistroPersonalizado
from .models import UsuarioPersonalizado

def main_view(request):
    logout(request)  
    return render(request, 'inicio.html')

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



def ofertas_view(request):
    return render(request, 'ofertas.html')

def cruceros_view(request):
    return render(request, 'crucero.html')

