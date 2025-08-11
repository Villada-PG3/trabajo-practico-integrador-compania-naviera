# views.py
from django.shortcuts import render, redirect
from .forms import FormularioRegistroPersonalizado
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def main_view(request):
    logout(request)  
    return render(request, 'inicio.html')

def registro_usuario(request):
    if request.method == 'POST':
        form = FormularioRegistroPersonalizado(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario registrado correctamente. Inicia sesión.")
            return redirect('login')  
    else:
        form = FormularioRegistroPersonalizado()
    return render(request, 'registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username') or request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
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

def reservas_view(request):
    return render(request, 'reservas.html')

def ofertas_view(request):
    return render(request, 'ofertas.html')
