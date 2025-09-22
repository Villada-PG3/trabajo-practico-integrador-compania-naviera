from collections import defaultdict

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.utils.timezone import now
from django.views.generic.edit import CreateView

from .forms import (
    FormularioCambioContrasenia,
    FormularioEdicionPerfil,
    FormularioRegistroPersonalizado,
)
from .models import (
    ActividadPosible,
    HistorialPago,
    ItinerarioViaje,
    Navio,
    Pago,
    Puerto,
    PuertoxActividad,
    Reserva,
    UsuarioPersonalizado,
    Viaje,
    ViajeXNavio,
)


def destinos_view(request):
    destinos = (
        Puerto.objects.select_related("itinerario__categoria")
        .prefetch_related(
            "ubicaciones",
            Prefetch(
                "actividades",
                queryset=PuertoxActividad.objects.select_related("actividad"),
            ),
        )
        .order_by("itinerario__categoria__nombre", "orden", "nombre")
    )
    return render(request, "destinos.html", {"destinos": destinos})


@login_required
def cambiar_contrasenia(request):
    if request.method == "POST":
        form = FormularioCambioContrasenia(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect("menu_user")
        messages.error(request, "Por favor corrige los errores.")
    else:
        form = FormularioCambioContrasenia(user=request.user)

    return render(request, "cambiar_contrasenia.html", {"form": form})


def main_view(request):
    logout(request)
    proximos_viajes = (
        Viaje.objects.filter(fecha_de_salida__gte=now().date())
        .order_by("fecha_de_salida")[:6]
    )

    return render(request, "inicio.html", {"proximos_viajes": proximos_viajes})


class RegistroUsuario(CreateView):
    form_class = FormularioRegistroPersonalizado
    template_name = "registro.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, "Usuario registrado correctamente. Inicia sesión."
        )
        return response


def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username") or request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=username_or_email, password=password)

        if user is None:
            try:
                usuario = UsuarioPersonalizado.objects.get(email=username_or_email)
                user = authenticate(
                    request, username=usuario.username, password=password
                )
            except UsuarioPersonalizado.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            return redirect("menu_user")
        messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "inicio_sesion.html")


@login_required
def menu_user(request):
    usuario = request.user
    hoy = now().date()

    reservas_usuario = (
        Reserva.objects.filter(cliente__usuario=usuario)
        .select_related(
            "estado_reserva",
            "viaje_navio__viaje",
            "viaje_navio__navio",
        )
        .order_by("viaje_navio__viaje__fecha_de_salida")
    )

    proximos_cruceros = []
    for reserva in reservas_usuario:
        viaje = reserva.viaje_navio.viaje
        if viaje.fecha_de_salida and viaje.fecha_de_salida >= hoy:
            proximos_cruceros.append(
                {
                    "nombre": viaje.nombre,
                    "fecha": viaje.fecha_de_salida,
                    "estado": reserva.estado_reserva.nombre
                    if reserva.estado_reserva
                    else "",
                    "navio_id": reserva.viaje_navio.navio_id,
                    "navio_nombre": reserva.viaje_navio.navio.nombre,
                }
            )

    proximos_cruceros = proximos_cruceros[:3]

    ofertas_destacadas = list(
        ViajeXNavio.objects.filter(viaje__fecha_de_salida__gte=hoy)
        .select_related("viaje", "navio")
        .order_by("precio")[:3]
    )

    actividades_destacadas = list(
        ActividadPosible.objects.order_by("nombre")[:3]
    )

    contexto = {
        "usuario": usuario,
        "reservas_total": reservas_usuario.count(),
        "reservas_activas": len(proximos_cruceros),
        "ofertas_destacadas": ofertas_destacadas,
        "proximos_cruceros": proximos_cruceros,
        "actividades_destacadas": actividades_destacadas,
    }

    return render(request, "menu_user.html", contexto)


@login_required
def pagos_view(request):
    usuario = request.user

    pagos_qs = (
        Pago.objects.filter(reserva__cliente__usuario=usuario)
        .select_related(
            "reserva__viaje_navio__viaje",
            "reserva__viaje_navio__navio",
            "metodo_pago",
            "estado_pago",
        )
        .prefetch_related(
            Prefetch(
                "historialpago_set",
                queryset=HistorialPago.objects.select_related(
                    "estado_pago", "usuario_responsable"
                ).order_by("-fecha_cambio"),
            )
        )
        .order_by("-fecha_pago", "-created_at")
    )

    pagos = list(pagos_qs)
    resumen_por_estado = defaultdict(lambda: {"monto": 0, "cantidad": 0})
    resumen_por_metodo = defaultdict(lambda: {"monto": 0, "cantidad": 0})
    total_monto = 0

    for pago in pagos:
        resumen_por_estado[pago.estado_pago.nombre]["monto"] += pago.monto
        resumen_por_estado[pago.estado_pago.nombre]["cantidad"] += 1

        resumen_por_metodo[pago.metodo_pago.nombre]["monto"] += pago.monto
        resumen_por_metodo[pago.metodo_pago.nombre]["cantidad"] += 1

        total_monto += pago.monto

    resumen_estados = [
        {"nombre": nombre, **datos}
        for nombre, datos in resumen_por_estado.items()
    ]
    resumen_metodos = [
        {"nombre": nombre, **datos}
        for nombre, datos in resumen_por_metodo.items()
    ]

    contexto = {
        "pagos": pagos,
        "total_pagos": len(pagos),
        "total_monto": total_monto,
        "resumen_estados": resumen_estados,
        "resumen_metodos": resumen_metodos,
    }

    return render(request, "pagos.html", contexto)


def contacto_view(request):
    return render(request, "contacto.html")


def cruceros_view(request):
    cruceros = Navio.objects.all()
    return render(request, "cruceros.html", {"cruceros": cruceros})


def navio_detail_view(request, pk):
    navio = get_object_or_404(Navio, pk=pk)
    return render(request, "navio_detail.html", {"navio": navio})


def contacto_log_view(request):
    return render(request, "contacto_log.html")


def ofertas_view(request):
    hoy = now().date()
    ofertas_qs = (
        ViajeXNavio.objects.filter(viaje__fecha_de_salida__gte=hoy)
        .select_related("navio", "viaje")
        .prefetch_related(
            Prefetch(
                "viaje__itinerarioviaje_set",
                queryset=ItinerarioViaje.objects.select_related("itinerario__categoria"),
            )
        )
        .order_by("viaje__fecha_de_salida")
    )

    ofertas = list(ofertas_qs)
    for oferta in ofertas:
        noches = 0
        if oferta.viaje.fecha_de_salida and oferta.viaje.fecha_fin:
            noches = max(
                (oferta.viaje.fecha_fin - oferta.viaje.fecha_de_salida).days,
                0,
            )

        itinerarios = list(oferta.viaje.itinerarioviaje_set.all())
        categoria_nombre = ""
        if itinerarios:
            itinerario_rel = itinerarios[0]
            itinerario_obj = getattr(itinerario_rel, "itinerario", None)
            categoria = getattr(itinerario_obj, "categoria", None)
            if categoria:
                categoria_nombre = categoria.nombre

        oferta.noches = noches
        oferta.categoria_nombre = categoria_nombre or "Otros"
        oferta.categoria_slug = slugify(categoria_nombre) if categoria_nombre else "otros"

    return render(request, "ofertas.html", {"ofertas": ofertas})


def logout_view(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect("home")


def editar_perfil(request):
    if request.method == "POST":
        form = FormularioEdicionPerfil(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("menu_user")
        messages.error(request, "Corrige los errores del formulario.")
    else:
        form = FormularioEdicionPerfil(instance=request.user)
    return render(request, "editar_perfil.html", {"form": form})
