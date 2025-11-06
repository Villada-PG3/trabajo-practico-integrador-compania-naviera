from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.utils.timezone import now
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash  
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Q
from django.views.generic import CreateView, TemplateView, ListView, DetailView, FormView, UpdateView, View
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
    logout(request)  # deja la sesión limpia al entrar al home
    
    return render(request, "inicio.html")

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

        # --- Filtros base (solo viajes futuros) ---
        filtros = Q(viaje__fecha_de_salida__gte=hoy)

        if destino:
            filtros &= Q(viaje__lugar_destino__icontains=destino)
        if fecha:
            filtros &= Q(viaje__fecha_de_salida=fecha)
        if precio_min:
            filtros &= Q(precio__gte=float(precio_min))
        if precio_max:
            filtros &= Q(precio__lte=float(precio_max))

        # --- Query principal (ofertas filtradas) ---
        ofertas_qs = (
            ViajeXNavio.objects.filter(filtros)
            .select_related(
                "navio",
                "viaje",
                "viaje__itinerario_viaje__itinerario__categoria",
            )
            .prefetch_related("viaje__itinerario_viaje__itinerario__ordenes")
            .order_by('precio')
        )

        ofertas = list(ofertas_qs)

        # --- Enriquecer datos ---
        for oferta in ofertas:
            noches = 0
            if oferta.viaje.fecha_de_salida and oferta.viaje.fecha_fin:
                noches = max((oferta.viaje.fecha_fin - oferta.viaje.fecha_de_salida).days, 0)

            itinerario_rel = getattr(oferta.viaje, "itinerario_viaje", None)
            itinerario_obj = getattr(itinerario_rel, "itinerario", None)
            categoria = getattr(itinerario_obj, "categoria", None)
            categoria_nombre = categoria.nombre if categoria else ""

            oferta.noches = noches
            oferta.categoria_nombre = categoria_nombre or "Otros"
            oferta.categoria_slug = slugify(categoria_nombre) if categoria_nombre else "otros"
            oferta.itinerario_rel = itinerario_rel

        # --- Determinar si hubo búsqueda sin resultados ---
        sin_resultados = len(ofertas) == 0 and any([destino, fecha, precio_min, precio_max])

        # --- Ofertas recomendadas (cuando no hay resultados) ---
        recomendadas = []
        if sin_resultados:
            recomendadas = (
                ViajeXNavio.objects.filter(viaje__fecha_de_salida__gte=hoy)
                .select_related(
                    "navio",
                    "viaje",
                    "viaje__itinerario_viaje__itinerario__categoria",
                )
                .prefetch_related("viaje__itinerario_viaje__itinerario__ordenes")
                .order_by('precio')[:6]  # las 6 más baratas
            )

            for oferta in recomendadas:
                noches = 0
                if oferta.viaje.fecha_de_salida and oferta.viaje.fecha_fin:
                    noches = max((oferta.viaje.fecha_fin - oferta.viaje.fecha_de_salida).days, 0)
                oferta.noches = noches
                itinerario_rel = getattr(oferta.viaje, "itinerario_viaje", None)
                itinerario_obj = getattr(itinerario_rel, "itinerario", None)
                categoria = getattr(itinerario_obj, "categoria", None)
                categoria_nombre = categoria.nombre if categoria else ""
                oferta.categoria_nombre = categoria_nombre or "Otros"
                oferta.categoria_slug = slugify(categoria_nombre) if categoria_nombre else "otros"
                oferta.itinerario_rel = itinerario_rel

        contexto["ofertas"] = ofertas
        contexto["sin_resultados"] = sin_resultados
        contexto["recomendadas"] = recomendadas
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
        itinerario_rel = getattr(oferta.viaje, "itinerario_viaje", None)
        itinerario_obj = getattr(itinerario_rel, "itinerario", None)
        categoria = getattr(itinerario_obj, "categoria", None)
        categoria_nombre = categoria.nombre if categoria else ""

        contexto["noches"] = noches
        contexto["categoria_nombre"] = categoria_nombre or "Otros"
        contexto["itinerario"] = itinerario_rel
        return contexto

# ===========================
# Autenticación / Perfil
# ===========================

class RegistroUsuario(CreateView):
    form_class = FormularioRegistroPersonalizado
    template_name = "registro.html"
    success_url = reverse_lazy("menu_user")

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        messages.success(self.request, "¡Registro exitoso! Ya estás conectado.")
        return redirect(self.get_success_url())


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
# ===========================from django.utils.timezone import now

class MenuUserView(LoginRequiredMixin, TemplateView):
    template_name = "menu_user.html"

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



class ReservaCreateView(LoginRequiredMixin, View):
    template_name = "crear_reserva.html"
    success_url = reverse_lazy("mis_reservas")

    def get(self, request):
        clientes = Cliente.objects.filter(usuario=request.user)
        viaje_navio_id = request.GET.get("viaje_navio_id")

        try:
            viaje_seleccionado = ViajeXNavio.objects.select_related("viaje", "navio").get(id=viaje_navio_id)
        except ViajeXNavio.DoesNotExist:
            return redirect("ofertas")

        context = {
            "clientes": clientes,
            "viaje_seleccionado": viaje_seleccionado,
        }
        return render(request, self.template_name, context)

    def post(self, request):
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
# Datos dinámicos para reservas
# ======================
def obtener_tipos_camarote(request):
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


def obtener_capacidades_camarote(request):
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


def obtener_camarotes_disponibles(request):
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
