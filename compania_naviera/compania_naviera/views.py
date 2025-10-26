from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash  
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Q
from django.views.generic import CreateView, TemplateView, ListView, DetailView, FormView, UpdateView, DeleteView, View
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import (
    FormularioCambioContrasenia,
    FormularioCliente,
    FormularioEdicionPerfil,
    FormularioRegistroPersonalizado,
)
from .models import (
    ActividadPosible,
    Camarote,
    Cliente,
    EstadoPasajero,
    EstadoReserva,
    ItinerarioViaje,
    Navio,
    OcupacionCamarote,
    Pasajero,
    Puerto,
    PuertoxActividad,
    Reserva,
    TipoCamarote,
    UsuarioPersonalizado,
    Viaje,
    ViajeXNavio,
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
class ContactoView(TemplateView):
    template_name = "contacto.html"

    def post(self, request, *args, **kwargs):
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

        return self.get(request, *args, **kwargs)

class DestinosView(ListView):
    model = Puerto
    template_name = "destinos.html"
    context_object_name = "destinos"

    def get_queryset(self):
        return Puerto.objects.select_related("orden__itinerario__categoria").prefetch_related(
            "ubicaciones",
            Prefetch(
                "actividades",
                queryset=PuertoxActividad.objects.select_related("actividad"),
            ),
        ).order_by("orden__itinerario__categoria__nombre", "orden__orden", "nombre")


class DestinoDetailView(DetailView):
    model = Puerto
    template_name = "destino_detail.html"
    context_object_name = "puerto"

class OfertasView(TemplateView):
    template_name = "ofertas.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        hoy = now().date()

        # --- FILTROS DINÁMICOS ---
        destino = self.request.GET.get('destino')
        fecha = self.request.GET.get('fecha')
        precio_min = self.request.GET.get('precio_min')
        precio_max = self.request.GET.get('precio_max')

        filtros = Q()
        if destino:
            filtros &= Q(viaje__lugar_destino__icontains=destino)
        if fecha:
            filtros &= Q(viaje__fecha_de_salida=fecha)
        if precio_min:
            filtros &= Q(precio__gte=float(precio_min))
        if precio_max:
            filtros &= Q(precio__lte=float(precio_max))

        # --- Query principal ---
        ofertas_qs = (
            ViajeXNavio.objects.filter(filtros)
            .select_related("navio", "viaje")
            .prefetch_related(
                Prefetch(
                    "viaje__itinerarioviaje_set",
                    queryset=ItinerarioViaje.objects.select_related("itinerario__categoria"),
                )
            )
            .order_by('precio')  # más baratos primero
        )

        ofertas = list(ofertas_qs)

        # --- Enriquecer datos para template ---
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

        contexto["ofertas"] = ofertas
        return contexto
    

class DetalleOfertaView(DetailView):
    model = ViajeXNavio
    template_name = "detalle_oferta.html"
    context_object_name = "oferta"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        oferta = self.get_object()

        # Calcular noches
        noches = 0
        if oferta.viaje.fecha_de_salida and oferta.viaje.fecha_fin:
            noches = max((oferta.viaje.fecha_fin - oferta.viaje.fecha_de_salida).days, 0)

        # Obtener categoría del itinerario
        itinerarios = list(oferta.viaje.itinerarioviaje_set.all())
        categoria_nombre = ""
        if itinerarios:
            itinerario_obj = getattr(itinerarios[0], "itinerario", None)
            categoria = getattr(itinerario_obj, "categoria", None)
            if categoria:
                categoria_nombre = categoria.nombre

        contexto["noches"] = noches
        contexto["categoria_nombre"] = categoria_nombre or "Otros"
        contexto["itinerarios"] = itinerarios
        return contexto

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


class EditarPerfilView(LoginRequiredMixin, UpdateView):
    form_class = FormularioEdicionPerfil
    template_name = "editar_perfil.html"
    success_url = reverse_lazy("menu_user")

    def get_object(self):
        # Siempre editar el usuario logueado
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Perfil actualizado correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Corrige los errores del formulario.")
        return super().form_invalid(form)


class CambiarContraseniaView(LoginRequiredMixin, FormView):
    form_class = FormularioCambioContrasenia
    template_name = "cambiar_contrasenia.html"
    success_url = reverse_lazy("menu_user")

    def get_form(self, form_class=None):
        # Pasar el usuario al form
        return self.form_class(user=self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        messages.success(self.request, "Contraseña actualizada correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Por favor corrige los errores.")
        return super().form_invalid(form)

# ===========================
# Panel de Usuario / Reservas
# ===========================
class MenuUserView(LoginRequiredMixin, TemplateView):
    template_name = "menu_user.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
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

        ofertas_destacadas = list(
            ViajeXNavio.objects.filter(viaje__fecha_de_salida__gte=hoy)
            .select_related("viaje", "navio")
            .order_by("precio")[:3]
        )
        actividades_destacadas = list(ActividadPosible.objects.order_by("nombre")[:3])

        context.update({
            "usuario": usuario,
            "reservas_total": reservas_usuario.count(),
            "reservas_activas": len(proximos_cruceros),
            "ofertas_destacadas": ofertas_destacadas,
            "proximos_cruceros": proximos_cruceros,
            "actividades_destacadas": actividades_destacadas,
        })
        return context


class MisReservasView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = "mis_reservas.html"
    context_object_name = "reservas"

    def get_queryset(self):
        return (
            Reserva.objects.filter(cliente__usuario=self.request.user)
            .select_related(
                "viaje_navio__viaje",
                "viaje_navio__navio",
                "camarote__tipo_camarote",
            )
            .prefetch_related("pasajeros")
            .order_by("-created_at")
        )

@login_required
def cancelar_reserva_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente__usuario=request.user)

    reserva.delete()
    messages.success(request, f"La reserva #{reserva_id} se ha eliminado correctamente.")
    return redirect(reverse_lazy("mis_reservas"))



class CrearClienteView(LoginRequiredMixin, CreateView):
    form_class = FormularioCliente
    template_name = "crear_cliente.html"
    success_url = reverse_lazy("crear_reserva")

    def form_valid(self, form):
        cliente = form.save(commit=False)
        cliente.usuario = self.request.user
        cliente.save()
        messages.success(self.request, "Cliente creado correctamente.")
        return redirect(self.success_url)

# Crear reserva
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cliente, ViajeXNavio, Camarote, OcupacionCamarote, Reserva, Pasajero, EstadoReserva, EstadoPasajero, TipoCamarote

class ReservaCreateView(LoginRequiredMixin, View):
    template_name = "crear_reserva.html"
    success_url = reverse_lazy("mis_reservas")

    def get(self, request, *args, **kwargs):
        clientes = Cliente.objects.filter(usuario=request.user)
        viaje_navio_id = request.GET.get("viaje_navio_id")

        if not viaje_navio_id:
            messages.error(request, "No se ha seleccionado un viaje.")
            return redirect("ofertas")

        try:
            viaje_seleccionado = ViajeXNavio.objects.select_related("viaje", "navio").get(id=viaje_navio_id)
        except ViajeXNavio.DoesNotExist:
            messages.error(request, "Viaje no encontrado.")
            return redirect("ofertas")

        context = {
            "clientes": clientes,
            "viaje_seleccionado": viaje_seleccionado,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        cliente_id = request.POST.get("cliente")
        viaje_id = request.POST.get("viaje_navio")
        camarote_id = request.POST.get("camarote")

        if not cliente_id or not viaje_id or not camarote_id:
            messages.error(request, "Debes seleccionar cliente y camarote.")
            return redirect(request.path + f"?viaje_navio_id={viaje_id}")

        try:
            cliente = Cliente.objects.get(id=cliente_id, usuario=request.user)
            viaje_navio = ViajeXNavio.objects.get(id=viaje_id)
            camarote = Camarote.objects.get(id=camarote_id)
        except (Cliente.DoesNotExist, ViajeXNavio.DoesNotExist, Camarote.DoesNotExist):
            messages.error(request, "Datos seleccionados inválidos.")
            return redirect(request.path + f"?viaje_navio_id={viaje_id}")

        # Verificar ocupación
        if OcupacionCamarote.objects.filter(camarote=camarote, viaje_navio=viaje_navio).exists():
            messages.error(request, f"El camarote #{camarote.numero_de_camarote} ya está ocupado en este viaje.")
            return redirect(request.path + f"?viaje_navio_id={viaje_id}")

        # Recoger pasajeros
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
            return redirect(request.path + f"?viaje_navio_id={viaje_id}")
        if len(pasajeros) > camarote.capacidad:
            messages.error(request, f"La cantidad de pasajeros excede la capacidad ({camarote.capacidad}).")
            return redirect(request.path + f"?viaje_navio_id={viaje_id}")

        # Crear reserva
        estado_reserva, _ = EstadoReserva.objects.get_or_create(nombre="Pendiente", defaults={"descripcion": "Pendiente"})
        reserva = Reserva.objects.create(
            descripcion="Reserva creada desde formulario",
            viaje_navio=viaje_navio,
            estado_reserva=estado_reserva,
            cliente=cliente,
            camarote=camarote
        )

        # Crear pasajeros y ocupación
        estado_pasajero, _ = EstadoPasajero.objects.get_or_create(nombre="Activo", defaults={"descripcion": "Activo"})
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


# ======================
# AJAX
# ======================
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
        cubierta__navio=viaje_navio.navio, tipo_camarote_id=tipo_id
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

    ocupados = OcupacionCamarote.objects.filter(viaje_navio=viaje_navio).values_list("camarote_id", flat=True)
    qs = qs.exclude(id__in=ocupados)

    data = [
        {"id": c.id, "numero_de_camarote": c.numero_de_camarote, "capacidad": c.capacidad, "tipo": c.tipo_camarote.nombre}
        for c in qs
    ]
    return JsonResponse(data, safe=False)


class CrucerosView(ListView):
    model = Navio
    template_name = "cruceros.html"
    context_object_name = "navios"
    queryset = Navio.objects.all().order_by("nombre")


class NavioDetailView(DetailView):
    model = Navio
    template_name = "navio_detail.html"
    context_object_name = "navio"