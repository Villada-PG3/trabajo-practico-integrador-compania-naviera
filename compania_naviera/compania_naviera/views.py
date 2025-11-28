from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy,reverse
from django.utils.text import slugify
from django.utils.timezone import now
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash  
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Prefetch, Q, Max
from django.views.generic import CreateView, TemplateView, ListView, DetailView, FormView, UpdateView, View
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.templatetags.static import static

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
# Recursos visuales estáticos
# ===========================

DEFAULT_DESTINO_IMAGE = static("puerto_buenos_aire.jpg")

DESTINO_IMAGES = {
    "Puerto Buenos Aires": static("puerto_buenos_aire.jpg"),
    "Puerto de Río": static("puerto_rio.jpg"),
    "Terminal Salvador": static("puerto_salvador.jpg"),
    "Puerto Montevideo": static("puerto_montevideo.jpg"),
    "Puerto Punta del Este": static("puerto_punta_Del_este.jpg"),
    "Puerto Punta Arenas": static("puerto_punta_arenas.avif"),
    "Puerto Ushuaia": static("puerto_usuahia.png"),
    "Puerto Reykjavík": static("puerto_raijkaw.jpg"),
    "Puerto Qikiqtarjuaq": static("Puerto Qikiqtarjuaq.jpg"),
}

CABIN_IMAGE_FALLBACK = static("a.jpg")
CABIN_FALLBACK_IMAGES = [
    static("camarote1.jpg"),
    static("camarote2.jpg"),
    static("camarote3.jpg"),
    static("camarote4.jpg"),
]
BATH_FALLBACK_IMAGES = [
    static("baño_camarote2.jpg"),
    static("baño_camarote3.jpg"),
    static("baño_camarote4.jpg"),
    static("baño_camarote2.jpg"),  # reutilizamos para completar el set
]

AURORA_GALLERY = [
    {
        "url": static("crucero1.1"),
        "label": "Cubierta principal del SEA Star Aurora",
        "type": "exterior",
    },
    {
        "url": static("crucero1.2"),
        "label": "Piscinas con horizonte infinito",
        "type": "exterior",
    },
    {
        "url": static("crucero1.3"),
        "label": "Lobby panorámico luminoso",
        "type": "interior",
    },
    {
        "url": static("crucero1.4.jpg"),
        "label": "Suites con balcones privados",
        "type": "cabin",
    },
    {
        "url": static("crucero1.5.jpg"),
        "label": "Restaurante Signature a bordo",
        "type": "interior",
    },
    {
        "url": static("crucero1.6.webp"),
        "label": "Puente de mando del Aurora",
        "type": "exterior",
    },
]

POLARIS_GALLERY = [
    {
        "url": static("crucero2.1"),
        "label": "Cubierta reforzada para expediciones",
        "type": "exterior",
    },
    {
        "url": static("crucero2.2"),
        "label": "Pasarelas calefaccionadas",
        "type": "exterior",
    },
    {
        "url": static("crucero2.3"),
        "label": "Observatorio polar de 270°",
        "type": "interior",
    },
    {
        "url": static("crucero2.4.webp"),
        "label": "Camarote polar con ventanal",
        "type": "cabin",
    },
    {
        "url": static("crucero2.5.webp"),
        "label": "Lounge de briefing científico",
        "type": "interior",
    },
    {
        "url": static("crucero2.6.webp"),
        "label": "Zodiac listos para desembarcos",
        "type": "exterior",
    },
]

HARMONY_GALLERY = [
    {
        "url": static("crucero3.1"),
        "label": "Harmony navegando en aguas turquesa",
        "type": "exterior",
    },
    {
        "url": static("crucero3.2"),
        "label": "Solárium familiar con toboganes",
        "type": "exterior",
    },
    {
        "url": static("crucero3.3"),
        "label": "Atrio central con jardines verticales",
        "type": "interior",
    },
    {
        "url": static("crucero3.4.jpg"),
        "label": "Camarote Harmony Breeze Club",
        "type": "cabin",
    },
    {
        "url": static("crucero3.5.jpg"),
        "label": "Teatro Ocean Sound en función",
        "type": "interior",
    },
    {
        "url": static("crucero3.6.jpg"),
        "label": "Mirador Sunset en popa",
        "type": "exterior",
    },
]

NAVIO_GALLERIES = {
    "SEA Star Aurora": AURORA_GALLERY,
    "SEA Explorer Polaris": POLARIS_GALLERY,
    "SEA Harmony Breeze": HARMONY_GALLERY,
}

def get_navio_gallery(navio_nombre):
    gallery = NAVIO_GALLERIES.get(navio_nombre, [])
    return [image.copy() for image in gallery]

def get_navio_cabin_details(navio_nombre):
    for image in get_navio_gallery(navio_nombre):
        if image.get("type") == "cabin":
            return image["url"], image["label"]
    return CABIN_IMAGE_FALLBACK, "Camarote premium"

def get_port_image(nombre):
    nombre = (nombre or "").strip()
    return DESTINO_IMAGES.get(nombre, DEFAULT_DESTINO_IMAGE)

def get_port_gallery(nombre):
    titulo = (nombre or "el destino").strip() or "el destino"
    image_url = get_port_image(nombre)
    return [
        {
            "url": image_url,
            "label": f"Vista de {titulo}",
            "type": "destino",
        }
    ]

def get_itinerary_port_gallery(oferta, limit=6):
    itinerario_rel = getattr(oferta, "itinerario_rel", None)
    itinerario = getattr(itinerario_rel, "itinerario", None)
    if not itinerario:
        return []

    ordenes_manager = getattr(itinerario, "ordenes", None)
    if not ordenes_manager:
        return []

    ordenes_iter = ordenes_manager.all() if hasattr(ordenes_manager, "all") else ordenes_manager
    gallery = []

    for orden in ordenes_iter:
        puertos_manager = getattr(orden, "puertos", None)
        if not puertos_manager:
            continue
        puertos_iter = puertos_manager.all() if hasattr(puertos_manager, "all") else puertos_manager
        for puerto in puertos_iter:
            gallery.extend(get_port_gallery(puerto.nombre))
            if limit and len(gallery) >= limit:
                return gallery[:limit]

    return gallery

def get_destino_gallery(destino_nombre):
    gallery = get_port_gallery(destino_nombre)
    if gallery:
        return gallery
    return [
        {
            "url": DEFAULT_DESTINO_IMAGE,
            "label": "Postales del itinerario",
            "type": "destino",
        }
    ]

def build_oferta_gallery(oferta):
    gallery = []
    seen_urls = set()

    def append_image(url, label, image_type):
        if not url or url in seen_urls:
            return
        gallery.append(
            {
                "url": url,
                "label": label or "Ambiente destacado",
                "type": image_type or "destino",
            }
        )
        seen_urls.add(url)

    navio = getattr(oferta, "navio", None)
    navio_nombre = getattr(navio, "nombre", "")
    navio_principal = getattr(navio, "imagen", "")
    if navio_principal:
        append_image(
            navio_principal,
            f"Exterior del {navio_nombre or 'navío principal'}",
            "exterior",
        )

    cabin_image = getattr(oferta, "cabin_image", None)
    cabin_label = getattr(oferta, "cabin_label", "")
    if cabin_image and cabin_image != navio_principal:
        append_image(
            cabin_image,
            cabin_label or (f"Camarote del {navio_nombre}" if navio_nombre else "Camarote destacado"),
            "cabin",
        )

    destino_gallery = get_itinerary_port_gallery(oferta, limit=6)
    if not destino_gallery:
        destino_nombre = getattr(oferta.viaje, "lugar_destino", "")
        destino_gallery = get_destino_gallery(destino_nombre)
    for image in destino_gallery:
        append_image(
            image.get("url"),
            image.get("label"),
            image.get("type", "destino"),
        )

    if not gallery:
        backup_gallery = get_navio_gallery(navio_nombre)
        if not backup_gallery:
            backup_gallery = [{"url": CABIN_IMAGE_FALLBACK, "label": "Camarote premium", "type": "cabin"}]
        for image in backup_gallery:
            append_image(image.get("url"), image.get("label"), image.get("type", "exterior"))

    return gallery


def human_join(labels):
    labels = [label for label in labels if label]
    if not labels:
        return ""
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} y {labels[1]}"
    return ", ".join(labels[:-1]) + f" y {labels[-1]}"


def build_navio_description(navio, feature_labels):
    base = f"{navio.tipo_navio.nombre} · {navio.cantidad_maxima_de_pasajeros} pasajeros"
    extras = human_join(feature_labels[:2])
    if extras:
        base += f" · {extras}"
    return base

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

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        destinos = contexto.get("destinos") or []
        for puerto in destinos:
            nombre = (puerto.nombre or "").strip()
            puerto.display_image = get_port_image(nombre)
        return contexto

class DestinoDetailView(DetailView):
    model = Puerto
    template_name = "destino_detail.html"
    context_object_name = "puerto"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        puerto = contexto.get("puerto")
        if puerto:
            nombre = (puerto.nombre or "").strip()
            contexto["display_image"] = get_port_image(nombre)
        return contexto


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
            .prefetch_related("viaje__itinerario_viaje__itinerario__ordenes__puertos")
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
            cabin_image, cabin_label = get_navio_cabin_details(oferta.navio.nombre)
            oferta.cabin_image = cabin_image
            oferta.cabin_label = cabin_label
            oferta.gallery = build_oferta_gallery(oferta)

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
                .prefetch_related("viaje__itinerario_viaje__itinerario__ordenes__puertos")
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
                cabin_image, cabin_label = get_navio_cabin_details(oferta.navio.nombre)
                oferta.cabin_image = cabin_image
                oferta.cabin_label = cabin_label
                oferta.gallery = build_oferta_gallery(oferta)

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

        oferta.itinerario_rel = itinerario_rel
        contexto["noches"] = noches
        contexto["categoria_nombre"] = categoria_nombre or "Otros"
        contexto["itinerario"] = itinerario_rel
        cabin_image, cabin_label = get_navio_cabin_details(oferta.navio.nombre)
        oferta.cabin_image = cabin_image
        oferta.cabin_label = cabin_label
        contexto["cabin_image"] = cabin_image
        contexto["cabin_label"] = cabin_label
        oferta.gallery = build_oferta_gallery(oferta)
        contexto["gallery"] = oferta.gallery
        contexto["oferta"] = oferta
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

    if request.method != "POST":
        messages.error(request, "Acción inválida.")
        return redirect(reverse_lazy("mis_reservas"))

    reserva.delete()
    messages.success(request, f"La reserva #{reserva_id} se ha eliminado correctamente.")
    return redirect(reverse_lazy("mis_reservas"))


class CrearClienteView(LoginRequiredMixin, CreateView):
    form_class = FormularioCliente
    template_name = "crear_cliente.html"

    def get_success_url(self):
        viaje_navio_id = (
            self.request.POST.get("viaje_navio_id")
            or self.request.GET.get("viaje_navio_id")
        )

    # si es vacío o "None", entonces retornamos a ofertas
        if not viaje_navio_id or viaje_navio_id == "None":
            return reverse("ofertas")

        return reverse("reserva_step1") + f"?viaje_navio_id={viaje_navio_id}"


    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # tomar el id del viaje si venía en GET/POST
        ctx["viaje_navio_id"] = (
            self.request.GET.get("viaje_navio_id")
            or self.request.POST.get("viaje_navio_id")
        )
        return ctx

    def form_valid(self, form):
        cliente = form.save(commit=False)
        cliente.usuario = self.request.user
        cliente.save()

        messages.success(self.request, "Cliente creado correctamente.")
        return redirect(self.get_success_url())
# Crear reserva


class CrucerosView(ListView):
    model = Navio
    template_name = "cruceros.html"
    context_object_name = "navios"
    queryset = Navio.objects.all().order_by("nombre")

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        navios = contexto.get("navios") or []
        for navio in navios:
            gallery = get_navio_gallery(navio.nombre)
            navio.gallery = gallery
            cabin_image, cabin_label = get_navio_cabin_details(navio.nombre)
            navio.cabin_image = cabin_image
            navio.cabin_label = cabin_label
            feature_labels = [item["label"] for item in gallery[:3]]
            navio.feature_tags = feature_labels
            navio.descripcion_card = build_navio_description(navio, feature_labels)
        return contexto

class NavioDetailView(DetailView):
    model = Navio
    template_name = "navio_detail.html"
    context_object_name = "navio"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        navio = contexto.get("navio")
        if navio:
            navio.gallery = get_navio_gallery(navio.nombre)
            contexto["gallery"] = navio.gallery
        return contexto

# --- Wizard session key and helpers ---
WIZARD_SESSION_KEY = "reserva_wizard"

def get_reserva_preview(request):
    session = request.session.get(WIZARD_SESSION_KEY, {})
    # devolvemos info compacta para el carrito
    preview = {
        "viaje_navio_id": session.get("viaje_navio_id"),
        "viaje_display": session.get("viaje_display"),   # string
        "tipo_id": session.get("tipo_id"),
        "tipo_display": session.get("tipo_display"),
        "tipo_imagen": session.get("tipo_imagen"),
        "precio": session.get("precio"),
        "capacidad_max": session.get("capacidad_max"),
        "pasajeros": session.get("pasajeros", []),
    }
    return preview

def clear_wizard_session(request):
    if WIZARD_SESSION_KEY in request.session:
        del request.session[WIZARD_SESSION_KEY]
        request.session.modified = True

# -------------------------
# STEP 1: elegir tipo (cards)
# -------------------------
class ReservaWizardStep1View(LoginRequiredMixin, View):
    template_name = "step1_tipo_camarote.html"

    def get(self, request):
        viaje_navio_id = self.request.GET.get("viaje_navio_id")

        if not viaje_navio_id or viaje_navio_id == "None":
            messages.error(self.request, "Debes elegir una oferta antes de continuar.")
            return redirect("ofertas")


        viaje_navio = get_object_or_404(ViajeXNavio.objects.select_related("viaje", "navio"), id=viaje_navio_id)

        tipos = list(TipoCamarote.objects.filter(camarote__cubierta__navio=viaje_navio.navio).distinct())
        # Imágenes fallback coherentes por tipo de camarote (cabina + baño)
        for idx, tipo in enumerate(tipos):
            tipo.fallback_cabin_img = CABIN_FALLBACK_IMAGES[idx % len(CABIN_FALLBACK_IMAGES)]
            tipo.fallback_bath_img = BATH_FALLBACK_IMAGES[idx % len(BATH_FALLBACK_IMAGES)]

        # inicializamos sesión del wizard (sobrescribimos para iniciar nuevo flujo)
        request.session[WIZARD_SESSION_KEY] = {
            "viaje_navio_id": viaje_navio.id,
            "viaje_display": f"{viaje_navio.viaje.nombre} — {viaje_navio.navio.nombre}",
            "tipo_id": None,
            "tipo_display": None,
            "tipo_imagen": None,
            "precio": viaje_navio.precio,
            "capacidad_max": None,
            "pasajeros": [],
        }
        request.session.modified = True

        context = {
            "viaje_navio": viaje_navio,
            "tipos": tipos,
            "carrito": get_reserva_preview(request),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        tipo_id = request.POST.get("tipo_id")
        wizard = request.session.get(WIZARD_SESSION_KEY)
        if not wizard:
            messages.error(request, "Sesión de reserva vencida. Volvé a intentarlo.")
            return redirect("ofertas")

        try:
            tipo = TipoCamarote.objects.get(id=tipo_id)
        except TipoCamarote.DoesNotExist:
            messages.error(request, "Tipo de camarote inválido.")
            return redirect(request.path + f"?viaje_navio_id={wizard.get('viaje_navio_id')}")

        viaje_navio = get_object_or_404(ViajeXNavio.objects.select_related("navio","viaje"), id=wizard["viaje_navio_id"])

        # calculamos la capacidad máxima disponible para ese tipo en ese navío
        max_cap = Camarote.objects.filter(
            cubierta__navio=viaje_navio.navio,
            tipo_camarote=tipo
        ).aggregate(max_cap=Max('capacidad'))['max_cap'] or 1

        # guardamos info legible para el carrito
        wizard["tipo_id"] = int(tipo_id)
        wizard["tipo_display"] = tipo.nombre
        # si TipoCamarote tuviera imagen, la guardamos; si no, la tomamos de un camarote ejemplo
        sample_camarote = Camarote.objects.filter(cubierta__navio=viaje_navio.navio, tipo_camarote=tipo).first()
        img = None
        if hasattr(tipo, 'imagen') and tipo.imagen:
            img = getattr(tipo, 'imagen', None)
        elif sample_camarote and sample_camarote.imagen:
            img = sample_camarote.imagen
        wizard["tipo_imagen"] = img if img else None

        wizard["capacidad_max"] = int(max_cap)
        # precio lo sacamos del viaje_navio (guardado antes)
        wizard["precio"] = viaje_navio.precio

        request.session[WIZARD_SESSION_KEY] = wizard
        request.session.modified = True

        return redirect("reserva_step2")


# -------------------------
# STEP 2: Tutor + Pasajeros
# -------------------------
class ReservaWizardStep2View(LoginRequiredMixin, View):
    template_name = "step2_tutor_pasajeros.html"

    def get(self, request):
        wizard = request.session.get(WIZARD_SESSION_KEY)
        if not wizard or not wizard.get("tipo_id"):
            messages.error(request, "Debés seleccionar un tipo de camarote primero.")
            return redirect("reserva_step1")

        viaje_navio = get_object_or_404(ViajeXNavio.objects.select_related("viaje","navio"), id=wizard["viaje_navio_id"])
        tipo = get_object_or_404(TipoCamarote, id=wizard["tipo_id"])

        # Intentamos obtener el Cliente vinculado al usuario (si existe)
        cliente_qs = Cliente.objects.filter(usuario=request.user)
        cliente = cliente_qs.first() if cliente_qs.exists() else None

        # Validamos campos obligatorios del tutor (según tu modelo)
        missing = []
        # campos que pediste obligatorios (siempre que existan en el modelo)
        required_fields = ["dni", "direccion", "fecha_nacimiento", "nacionalidad", "genero"]
        # teléfono: sólo si el modelo Cliente tiene ese atributo lo exigimos
        if hasattr(Cliente, "telefono"):
            required_fields.append("telefono")

        if cliente:
            for f in required_fields:
                val = getattr(cliente, f, None)
                # CountryField (nacionalidad) puede ser '' o None cuando no está seleccionado
                if val in (None, ""):
                    missing.append(f)
        else:
            # si no existe Cliente asociado → pedimos crear uno
            missing.append("cliente_no_creado")

        if missing:
            # Si falta cliente o datos del cliente, redirigimos a editar_perfil o crear cliente
            if "cliente_no_creado" in missing:
                messages.warning(request, "Necesitás crear tu ficha (Cliente) antes de reservar.")
                # preservamos el viaje en el flujo para que al volver siga en la reserva
                return redirect(
                    reverse("crear_cliente") + f"?viaje_navio_id={wizard.get('viaje_navio_id')}"
                )
            else:
                messages.warning(request, "Completá tus datos personales antes de continuar (DNI, dirección, fecha de nacimiento, nacionalidad, género).")
                return redirect("editar_perfil")

        # Si llegamos acá, cliente está y tiene datos obligatorios
        capacidad_max = int(wizard.get("capacidad_max") or 1)

        context = {
            "viaje_navio": viaje_navio,
            "tipo": tipo,
            "cliente": cliente,
            "capacidad_max": capacidad_max,
            "carrito": get_reserva_preview(request),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        wizard = request.session.get(WIZARD_SESSION_KEY)
        if not wizard:
            messages.error(request, "Sesión de reserva vencida.")
            return redirect("ofertas")

        # tutor será el cliente vinculado (ya validado en GET)
        cliente = Cliente.objects.filter(usuario=request.user).first()
        if not cliente:
            messages.error(request, "No se pudo identificar al tutor. Creá tu perfil de cliente.")
            return redirect("crear_cliente")

        capacidad_max = int(wizard.get("capacidad_max") or 1)

        # recoger pasajeros desde POST: esperamos pasajero_0_nombre, pasajero_0_apellido, etc.
        pasajeros = []
        # el formulario permite indicar cuántos pasajeros se cargaron; si no, iteramos hasta capacidad_max
        total_fields = int(request.POST.get("total_pasajeros_submitted", capacidad_max))
        total = min(total_fields, capacidad_max)
        for i in range(total):
            nombre = request.POST.get(f"pasajero_{i}_nombre")
            apellido = request.POST.get(f"pasajero_{i}_apellido")
            dni = request.POST.get(f"pasajero_{i}_dni")
            fecha_nac = request.POST.get(f"pasajero_{i}_fecha_nac")

            # aceptamos filas vacías (si el usuario decidió no completar todos)
            if nombre and apellido:
                pasajeros.append({
                    "nombre": nombre.strip(),
                    "apellido": apellido.strip(),
                    "dni": dni.strip() if dni else "",
                    "fecha_nacimiento": fecha_nac if fecha_nac else None
                })

        if len(pasajeros) == 0:
            messages.error(request, "Debes ingresar al menos un pasajero.")
            return redirect("reserva_step2")

        # Evitar duplicar al tutor como pasajero más de una vez
        tutor_signature = (
            (cliente.nombre or "").strip().lower(),
            (cliente.apellido or "").strip().lower(),
            (cliente.dni or "").strip(),
        )
        filtered = []
        tutor_seen = False
        tutor_duplicado = False
        for p in pasajeros:
            signature = (
                (p.get("nombre") or "").strip().lower(),
                (p.get("apellido") or "").strip().lower(),
                (p.get("dni") or "").strip(),
            )
            if signature == tutor_signature:
                if tutor_seen:
                    tutor_duplicado = True
                    continue
                tutor_seen = True
            filtered.append(p)

        if tutor_duplicado:
            wizard["pasajeros"] = filtered
            request.session[WIZARD_SESSION_KEY] = wizard
            request.session.modified = True
            messages.error(request, "El tutor solo puede cargarse una vez como pasajero en este camarote.")
            return redirect("reserva_step2")

        # Guardamos tutor y pasajeros en la sesión (temporal)
        wizard["tutor_cliente_id"] = cliente.id
        wizard["pasajeros"] = filtered
        request.session[WIZARD_SESSION_KEY] = wizard
        request.session.modified = True

        return redirect("reserva_confirm")


# -------------------------
# CONFIRM: revisar y crear
# -------------------------
class ReservaWizardConfirmView(LoginRequiredMixin, View):
    template_name = "confirmar_reserva.html"
    success_url = reverse_lazy("mis_reservas")

    def get(self, request):
        wizard = request.session.get(WIZARD_SESSION_KEY)
        if not wizard:
            messages.error(request, "Sesión de reserva vencida.")
            return redirect("ofertas")

        viaje_navio = get_object_or_404(ViajeXNavio.objects.select_related("viaje","navio"), id=wizard["viaje_navio_id"])
        tipo = get_object_or_404(TipoCamarote, id=wizard["tipo_id"])
        cliente = get_object_or_404(Cliente, id=wizard.get("tutor_cliente_id"))

        context = {
            "viaje_navio": viaje_navio,
            "tipo": tipo,
            "cliente": cliente,
            "pasajeros": wizard.get("pasajeros", []),
            "capacidad_max": wizard.get("capacidad_max"),
            "carrito": get_reserva_preview(request),
        }
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request):
        wizard = request.session.get(WIZARD_SESSION_KEY)
        if not wizard:
            messages.error(request, "Sesión de reserva vencida.")
            return redirect("ofertas")

        viaje_navio = get_object_or_404(ViajeXNavio.objects.select_related("viaje","navio"), id=wizard["viaje_navio_id"])
        tipo = get_object_or_404(TipoCamarote, id=wizard["tipo_id"])
        cliente = get_object_or_404(Cliente, id=wizard.get("tutor_cliente_id"))
        pasajeros_data = wizard.get("pasajeros", [])

        # Validación final
        if not pasajeros_data:
            messages.error(request, "No hay pasajeros para reservar.")
            return redirect("reserva_step2")

        # Encontrar camarote libre (tipo y capacidad)
        ocupados_ids = OcupacionCamarote.objects.filter(viaje_navio=viaje_navio).values_list("camarote_id", flat=True)
        camarote_libre = Camarote.objects.filter(
            cubierta__navio=viaje_navio.navio,
            tipo_camarote=tipo,
            capacidad__gte=len(pasajeros_data)
        ).exclude(id__in=ocupados_ids).order_by('numero_de_camarote').first()

        if not camarote_libre:
            messages.error(request, "Lo sentimos, no hay camarotes disponibles con ese tipo y capacidad.")
            return redirect("reserva_step1")

        # Crear Reserva
        estado_reserva, _ = EstadoReserva.objects.get_or_create(nombre="Pendiente", defaults={"descripcion": "Pendiente"})
        reserva = Reserva.objects.create(
            descripcion=f"Reserva automática por {request.user.username}",
            viaje_navio=viaje_navio,
            estado_reserva=estado_reserva,
            cliente=cliente,
            camarote=camarote_libre
        )

        # Crear pasajeros y ocupaciones
        estado_pasajero, _ = EstadoPasajero.objects.get_or_create(nombre="Activo", defaults={"descripcion":"Activo"})
        for p in pasajeros_data:
            pasajero = Pasajero.objects.create(
                reserva=reserva,
                nombre=p.get("nombre"),
                apellido=p.get("apellido"),
                dni=p.get("dni") or "",
                fecha_nacimiento=p.get("fecha_nacimiento") or None,
                fecha_inicio=viaje_navio.viaje.fecha_de_salida,
                fecha_fin=viaje_navio.viaje.fecha_fin,
                estado_pasajero=estado_pasajero
            )
            OcupacionCamarote.objects.create(
                reserva=reserva,
                camarote=camarote_libre,
                pasajero=pasajero,
                viaje_navio=viaje_navio,
                fecha_inicio=viaje_navio.viaje.fecha_de_salida,
                fecha_fin=viaje_navio.viaje.fecha_fin
            )

        # limpiamos wizard
        clear_wizard_session(request)

        messages.success(request, "Reserva creada correctamente.")
        return redirect(self.success_url)
