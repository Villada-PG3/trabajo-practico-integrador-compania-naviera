from collections import defaultdict
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.utils.timezone import now
from django.views.generic.edit import CreateView
from django.db.models import Avg
from django.core.mail import send_mail
from django.conf import settings


from .forms import (
    FormularioCambioContrasenia,
    FormularioEdicionPerfil,
    FormularioRegistroPersonalizado,
    FormularioReserva,
    FormularioCliente,
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
    Cliente,
    EstadoReserva,
    EstadoPasajero,
    Camarote,
    Pasajero,
    OcupacionCamarote,
    TipoCamarote

)


# ===========================
# Públicos / generales
# ===========================

    
def main_view(request):
    """
    Home público: muestra próximos viajes.
    """
    logout(request)  # deja la sesión limpia al entrar al home
    proximos_viajes = (
        Viaje.objects.filter(fecha_de_salida__gte=now().date())
        .order_by("fecha_de_salida")[:6]
    )
    return render(request, "inicio.html", {"proximos_viajes": proximos_viajes})


def contacto_view(request):
    """
    Vista para el formulario de contacto.
    Envía un email a gasleones@gmail.com usando Gmail.
    """
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        email = request.POST.get("email")
        mensaje = request.POST.get("mensaje")

        if nombre and email and mensaje:
            try:
                send_mail(
                    subject=f"Mensaje de {nombre}",
                    message=mensaje,
                    from_email=email,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
                messages.success(request, "¡Tu mensaje fue enviado correctamente!")
                return redirect("contacto")
            except Exception as e:
                messages.error(request, f"Error al enviar el mensaje: {e}")
        else:
            messages.error(request, "Por favor completá todos los campos.")

    return render(request, "contacto.html")

def destinos_view(request):
    """
    Lista destinos (Puertos) agrupados por itinerario/categoría,
    con ubicaciones y actividades prefetchadas.
    """
    destinos = (
    Puerto.objects.select_related("orden__itinerario__categoria")
    .prefetch_related(
        "ubicaciones",
        Prefetch(
            "actividades",
            queryset=PuertoxActividad.objects.select_related("actividad"),
        ),
    )
    .order_by("orden__itinerario__categoria__nombre", "orden__orden", "nombre")
    )
    return render(request, "destinos.html", {"destinos": destinos})


def destino_detail_view(request, pk):
    puerto = get_object_or_404(Puerto, pk=pk)
    return render(request, "destino_detail.html", {"puerto": puerto})

def ofertas_view(request):
    hoy = now().date()

    # 🔹 1) Obtener el promedio de precio de los viajes futuros
    promedio = (
        ViajeXNavio.objects.filter(viaje__fecha_de_salida__gte=hoy)
        .aggregate(Avg("precio"))["precio__avg"]
    )

    # 🔹 2) Consultar todos los viajes futuros con distintos criterios
    ofertas_qs = ViajeXNavio.objects.filter(viaje__fecha_de_salida__gte=hoy).select_related(
        "navio", "viaje"
    ).prefetch_related(
        Prefetch(
            "viaje__itinerarioviaje_set",
            queryset=ItinerarioViaje.objects.select_related("itinerario__categoria"),
        )
    )

    # 🔹 3) Filtrar viajes que sean oferta por distintos criterios
    ofertas_qs = ofertas_qs.filter(precio__lte=1000)

    if promedio is not None:
        ofertas_qs = ofertas_qs | ViajeXNavio.objects.filter(
            viaje__fecha_de_salida__gte=hoy,
            precio__lt=promedio
        )


    # 🔹 4) Ordenar por precio de menor a mayor y tomar los 5 más baratos
    ofertas_qs = ofertas_qs.order_by("precio")[:5]

    ofertas = list(ofertas_qs)

    # 🔹 5) Agregar atributos extra para el template
    for oferta in ofertas:
        noches = 0
        if oferta.viaje.fecha_de_salida and oferta.viaje.fecha_fin:
            noches = max((oferta.viaje.fecha_fin - oferta.viaje.fecha_de_salida).days, 0)

        itinerarios = list(oferta.viaje.itinerarioviaje_set.all())
        categoria_nombre = ""
        if itinerarios:
            itinerario_obj = getattr(itinerarios[0], "itinerario", None)
            categoria = getattr(itinerario_obj, "categoria", None)
            if categoria:
                categoria_nombre = categoria.nombre

        oferta.noches = noches
        oferta.categoria_nombre = categoria_nombre or "Otros"
        oferta.categoria_slug = slugify(categoria_nombre) if categoria_nombre else "otros"

    return render(request, "ofertas.html", {"ofertas": ofertas})

# ===========================
# Autenticación / Perfil
# ===========================

class RegistroUsuario(CreateView):
    form_class = FormularioRegistroPersonalizado
    template_name = "registro.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Usuario registrado correctamente. Inicia sesión.")
        return response


def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username") or request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=username_or_email, password=password)

        if user is None:
            # login por email si el username no coincide
            try:
                usuario = UsuarioPersonalizado.objects.get(email=username_or_email)
                user = authenticate(request, username=usuario.username, password=password)
            except UsuarioPersonalizado.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            return redirect("menu_user")
        messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "inicio_sesion.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect("home")


@login_required
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


# ===========================
# Panel de Usuario / Reservas
# ===========================

@login_required
def menu_user(request):
    """
    Dashboard del usuario con KPIs + próximos cruceros a partir de sus reservas.
    """
    usuario = request.user
    hoy = now().date()

    reservas_usuario = (
        Reserva.objects.filter(cliente__usuario=usuario)
        .select_related("estado_reserva", "viaje_navio__viaje", "viaje_navio__navio")
        .order_by("viaje_navio__viaje__fecha_de_salida")
    )

    proximos_cruceros = []
    for reserva in reservas_usuario:
        viaje = reserva.viaje_navio.viaje
        if viaje.fecha_de_salida and viaje.fecha_de_salida >= hoy:
            navio_id = getattr(reserva.viaje_navio, "navio_id", None)
            navio_nombre = getattr(getattr(reserva.viaje_navio, "navio", None), "nombre", "")
            proximos_cruceros.append(
                {
                    "nombre": viaje.nombre,
                    "fecha": viaje.fecha_de_salida,
                    "estado": reserva.estado_reserva.nombre if reserva.estado_reserva else "",
                    "navio_id": navio_id,
                    "navio_nombre": navio_nombre or "(sin asignar)",
                }
            )
    proximos_cruceros = proximos_cruceros[:3]

    # Ofertas y actividades simples para el panel
    ofertas_destacadas = list(
        ViajeXNavio.objects.filter(viaje__fecha_de_salida__gte=hoy)
        .select_related("viaje", "navio")
        .order_by("precio")[:3]
    )
    actividades_destacadas = list(ActividadPosible.objects.order_by("nombre")[:3])

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
def mis_reservas_view(request):
    usuario = request.user
    reservas = (
        Reserva.objects.filter(cliente__usuario=usuario)
        .select_related(
            "viaje_navio__viaje",
            "viaje_navio__navio",
            "camarote__tipo_camarote",
        )
        .prefetch_related("pasajeros")
        .order_by("-created_at")
    )
    return render(request, "mis_reservas.html", {"reservas": reservas})


@login_required
def cancelar_reserva_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente__usuario=request.user)

    reserva.delete()
    messages.success(request, f"La reserva #{reserva_id} se ha eliminado correctamente.")
    return redirect(reverse_lazy("mis_reservas"))

@login_required
def crear_cliente_view(request):
    if request.method == "POST":
        form = FormularioCliente(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.usuario = request.user
            cliente.save()
            messages.success(request, "Cliente creado correctamente.")
            return redirect("crear_reserva")
    else:
        form = FormularioCliente()

    return render(request, "crear_cliente.html", {"form": form})



# Crear reserva
class ReservaCreateView(LoginRequiredMixin, CreateView):
    model = Reserva
    form_class = FormularioReserva
    template_name = "crear_reserva.html"
    success_url = reverse_lazy("mis_reservas")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["clientes"] = Cliente.objects.filter(usuario=self.request.user)
        ctx["viajes"] = ViajeXNavio.objects.all()
        return ctx

    def post(self, request, *args, **kwargs):
        cliente_id = request.POST.get("cliente")
        viaje_id = request.POST.get("viaje_navio")
        camarote_id = request.POST.get("camarote")

        if not cliente_id or not viaje_id or not camarote_id:
            messages.error(request, "Debes seleccionar cliente, viaje y camarote.")
            return redirect("crear_reserva")

        try:
            cliente = Cliente.objects.get(id=cliente_id, usuario=request.user)
            viaje_navio = ViajeXNavio.objects.get(id=viaje_id)
            camarote = Camarote.objects.get(id=camarote_id)
        except (Cliente.DoesNotExist, ViajeXNavio.DoesNotExist, Camarote.DoesNotExist):
            messages.error(request, "Datos seleccionados inválidos.")
            return redirect("crear_reserva")

        # Verificar si el camarote ya está ocupado en ese viaje
        ocupado = OcupacionCamarote.objects.filter(camarote=camarote, viaje_navio=viaje_navio).exists()
        if ocupado:
            messages.error(request, f"El camarote #{camarote.numero_de_camarote} ya está ocupado en este viaje. Seleccioná otro.")
            return redirect("crear_reserva")

        # Recoger pasajeros dinámicos
        pasajeros = []
        for i in range(camarote.capacidad):
            nombre = request.POST.get(f"pasajero_nombre_{i}")
            apellido = request.POST.get(f"pasajero_apellido_{i}")
            dni = request.POST.get(f"pasajero_dni_{i}")
            fecha_nac = request.POST.get(f"pasajero_fecha_nacimiento_{i}")

            if nombre and apellido and dni and fecha_nac:
                pasajeros.append({
                    "nombre": nombre,
                    "apellido": apellido,
                    "dni": dni,
                    "fecha_nacimiento": fecha_nac,
                })

        if len(pasajeros) == 0:
            messages.error(request, "Debes agregar al menos un pasajero con todos los datos obligatorios.")
            return redirect("crear_reserva")

        if len(pasajeros) > camarote.capacidad:
            messages.error(request, f"La cantidad de pasajeros excede la capacidad ({camarote.capacidad}).")
            return redirect("crear_reserva")

        # Crear reserva
        estado_reserva, _ = EstadoReserva.objects.get_or_create(
            nombre="Pendiente",
            defaults={"descripcion": "Pendiente"}
        )
        reserva = Reserva.objects.create(
            descripcion="Reserva creada desde formulario",
            viaje_navio=viaje_navio,
            estado_reserva=estado_reserva,
            cliente=cliente,
            camarote=camarote
        )

        # Crear pasajeros y ocupación de camarote
        estado_pasajero, _ = EstadoPasajero.objects.get_or_create(
            nombre="Activo",
            defaults={"descripcion": "Activo"}
        )
        for p in pasajeros:
            pasajero = Pasajero.objects.create(
                reserva=reserva,
                nombre=p["nombre"],
                apellido=p["apellido"],
                dni=p["dni"],
                fecha_nacimiento=p["fecha_nacimiento"],
                fecha_inicio=viaje_navio.viaje.fecha_de_salida,
                fecha_fin=viaje_navio.viaje.fecha_fin,
                estado_pasajero=estado_pasajero
            )
            OcupacionCamarote.objects.create(
                reserva=reserva,
                camarote=camarote,
                pasajero=pasajero,
                viaje_navio=viaje_navio,
                fecha_inicio=viaje_navio.viaje.fecha_de_salida,
                fecha_fin=viaje_navio.viaje.fecha_fin
            )

        messages.success(request, "Reserva creada correctamente.")
        return redirect(self.success_url)


# AJAX
def ajax_tipos_camarote(request):
    viaje_navio_id = request.GET.get("viaje_navio_id")
    if not viaje_navio_id:
        return HttpResponseBadRequest("Falta viaje_navio_id")
    try:
        viaje_navio = ViajeXNavio.objects.select_related("navio").get(id=viaje_navio_id)
    except ViajeXNavio.DoesNotExist:
        return JsonResponse([], safe=False)
    tipos = TipoCamarote.objects.filter(camarote__cubierta__navio=viaje_navio.navio).distinct()
    data = [{"id": t.id, "nombre": t.nombre} for t in tipos]
    return JsonResponse(data, safe=False)

def ajax_capacidades(request):
    viaje_navio_id = request.GET.get("viaje_navio_id")
    tipo_id = request.GET.get("tipo_id")
    if not viaje_navio_id or not tipo_id:
        return HttpResponseBadRequest("Faltan parámetros")
    try:
        viaje_navio = ViajeXNavio.objects.select_related("navio").get(id=viaje_navio_id)
    except ViajeXNavio.DoesNotExist:
        return JsonResponse([], safe=False)
    capacidades = Camarote.objects.filter(
        cubierta__navio=viaje_navio.navio,
        tipo_camarote_id=tipo_id
    ).values_list("capacidad", flat=True).distinct()
    data = sorted(list(set(capacidades)))
    return JsonResponse([{"capacidad": c} for c in data], safe=False)

def ajax_camarotes(request):
    viaje_navio_id = request.GET.get("viaje_navio_id")
    tipo_id = request.GET.get("tipo_id")
    capacidad = request.GET.get("capacidad")
    if not viaje_navio_id:
        return HttpResponseBadRequest("Falta viaje_navio_id")
    try:
        viaje_navio = ViajeXNavio.objects.select_related("navio").get(id=viaje_navio_id)
    except ViajeXNavio.DoesNotExist:
        return JsonResponse([], safe=False)

    qs = Camarote.objects.filter(cubierta__navio=viaje_navio.navio)
    if tipo_id:
        qs = qs.filter(tipo_camarote_id=tipo_id)
    if capacidad:
        qs = qs.filter(capacidad=capacidad)

    ocupados = OcupacionCamarote.objects.filter(viaje_navio=viaje_navio).values_list('camarote_id', flat=True)
    qs = qs.exclude(id__in=ocupados)

    data = [
        {"id": c.id, "numero_de_camarote": c.numero_de_camarote, "capacidad": c.capacidad, "tipo": c.tipo_camarote.nombre}
        for c in qs
    ]
    return JsonResponse(data, safe=False)

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


def cruceros_view(request):
    """
    Muestra todos los navíos disponibles de la empresa.
    Ya no se listan los viajes futuros o históricos, solo los 3 navíos existentes.
    """
    # Obtiene todos los navíos registrados en la base de datos
    navios = Navio.objects.all().order_by("nombre")

    # Renderiza el template con la lista de navíos
    return render(request, "cruceros.html", {"navios": navios})


def navio_detail_view(request, pk):
    """
    Muestra el detalle de un navío.
    Redirige al login si el usuario no está autenticado.
    """
    navio = get_object_or_404(Navio, pk=pk)

    return render(request, "navio_detail.html", {
        "navio": navio,
    })