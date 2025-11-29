from django.contrib import admin
from django.urls import path

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
    CrearClienteView,
    CrucerosView,
    NavioDetailView,
    MainView,
    LoginView,
    LogoutViewWithMessage,
    ReservaWizardStep1View,
    ReservaWizardStep2View,
    ReservaWizardConfirmView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Home
    path('', MainView.as_view(), name='home'),
    path('contacto/', ContactoView.as_view(), name='contacto'),
    path('destinos/', DestinosView.as_view(), name='destinos'),
    path('destino/<int:pk>/', DestinoDetailView.as_view(), name='destino_detail'),
    path('ofertas/', OfertasView.as_view(), name='ofertas'),

    # Oferta → detalle
    path('ofertas/<int:pk>/', DetalleOfertaView.as_view(), name='detalle_oferta'),

    # Login / Registro
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutViewWithMessage.as_view(), name='logout'),
    path('registro/', RegistroUsuario.as_view(), name='registro'),

    # Perfil
    path('perfil/editar/', EditarPerfilView.as_view(), name='editar_perfil'),
    path('perfil/cambiar-contrasenia/', CambiarContraseniaView.as_view(), name='cambiar_contrasenia'),

    # Reservas Wizard
    path('reservas/nueva/', ReservaWizardStep1View.as_view(), name='reserva_step1'),
    path('reservas/nueva/step2/', ReservaWizardStep2View.as_view(), name='reserva_step2'),
    
    path('reservas/nueva/confirmar/', ReservaWizardConfirmView.as_view(), name='reserva_confirm'),
    
    # Panel usuario
    path('menu/', MenuUserView.as_view(), name='menu_user'),
    path('mis-reservas/', MisReservasView.as_view(), name='mis_reservas'),
    path('reserva/<int:reserva_id>/cancelar/', CancelarReservaView.as_view(), name='cancelar_reserva'),

    # Cliente (CRM)
    path('cliente/nuevo/', CrearClienteView.as_view(), name='crear_cliente'),

    # Cruceros
    path('cruceros/', CrucerosView.as_view(), name='cruceros'),
    path('cruceros/<int:pk>/', NavioDetailView.as_view(), name='navio_detail'),
]
