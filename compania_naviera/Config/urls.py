from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from compania_naviera.views import (
    CambiarContraseniaView, 
    EditarPerfilView,
    ContactoView,
    DestinosView,
    DestinoDetailView,
    OfertasView,
    RegistroUsuario,
    DetalleOfertaView,
    MenuUserView,
    MisReservasView,
    CancelarReservaView,
    ReservaCreateView,
    CrearClienteView,
    CrucerosView,
    NavioDetailView,
    ajax_tipos_camarote,
    ajax_capacidades,
    ajax_camarotes,
    main_view,
    login_view
)
urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # ----------------------
    # Home y páginas públicas
    # ----------------------
    path('', main_view, name='home'),
    path('contacto/', ContactoView.as_view(), name='contacto'),
    path('destinos/', DestinosView.as_view(), name='destinos'),
    path('destino/<int:pk>/', DestinoDetailView.as_view(), name='destino_detail'),
    path('ofertas/', OfertasView.as_view(), name='ofertas'),
    path('<int:pk>/', DetalleOfertaView.as_view(), name='detalle_oferta'),

    # ----------------------
    # Login / Logout / Registro
    # ----------------------
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('registro/', RegistroUsuario.as_view(), name='registro'),

    # ----------------------
    # Perfil de usuario
    # ----------------------
    path('perfil/editar/', EditarPerfilView.as_view(), name='editar_perfil'),
    path('perfil/cambiar-contrasenia/', CambiarContraseniaView.as_view(), name='cambiar_contrasenia'),

    # ----------------------
    # Panel de usuario / Reservas
    # ----------------------
    path('menu/', MenuUserView.as_view(), name='menu_user'),
    path('mis-reservas/', MisReservasView.as_view(), name='mis_reservas'),
    path('reserva/<int:reserva_id>/cancelar/', CancelarReservaView.as_view(), name='cancelar_reserva'),
    path('reservas/nueva/', ReservaCreateView.as_view(), name='crear_reserva'),

    # ----------------------
    # Cliente
    # ----------------------
    path('cliente/nuevo/', CrearClienteView.as_view(), name='crear_cliente'),

    # ----------------------
    # AJAX
    # ----------------------
    path('ajax/tipos-camarote/', ajax_tipos_camarote, name='ajax_tipos_camarote'),
    path('ajax/capacidades/', ajax_capacidades, name='ajax_capacidades'),
    path('ajax/camarotes/', ajax_camarotes, name='ajax_camarotes'),

    # ----------------------
    # Cruceros
    # ----------------------
    path('cruceros/', CrucerosView.as_view(), name='cruceros'),
    path('cruceros/<int:pk>/', NavioDetailView.as_view(), name='navio_detail'),
]
