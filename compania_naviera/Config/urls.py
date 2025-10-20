from django.contrib import admin
from django.urls import path, include
from compania_naviera import views
from django.contrib.auth import views as auth_views
from compania_naviera import views
from compania_naviera.views import (
    CambiarContraseniaView, 
    EditarPerfilView,
    ContactoView,
    DestinosView,
    DestinoDetailView,
    OfertasView,

    )
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    path('', views.main_view, name='home'),

    path("contacto/", ContactoView.as_view(), name="contacto"),
    path("destinos/", DestinosView.as_view(), name="destinos"),
    path("destino/<int:pk>/", DestinoDetailView.as_view(), name="destino_detail"),
    path("ofertas/", OfertasView.as_view(), name="ofertas"),

    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    path('registro/', views.RegistroUsuario.as_view(), name='registro'),

    path('menu/', views.menu_user, name='menu_user'),
    path("pagos/", views.pagos_view, name="pagos"),

    path("perfil/editar/", EditarPerfilView.as_view(), name="editar_perfil"),
    path("perfil/cambiar-contrasenia/", CambiarContraseniaView.as_view(), name="cambiar_contrasenia"),


    path('mis-reservas/', views.mis_reservas_view, name='mis_reservas'),
    
     path("reserva/<int:reserva_id>/cancelar/", views.cancelar_reserva_view, name="cancelar_reserva"),

    path('reservas/nueva/', views.ReservaCreateView.as_view(), name='crear_reserva'),

    # URLs AJAX
    path('ajax/tipos-camarote/', views.ajax_tipos_camarote, name='ajax_tipos_camarote'),
    path('ajax/capacidades/', views.ajax_capacidades, name='ajax_capacidades'),
    path('ajax/camarotes/', views.ajax_camarotes, name='ajax_camarotes'),

    # Cruceros + detalle
    path('cruceros/', views.cruceros_view, name='cruceros'),
    path('cruceros/<int:pk>/', views.navio_detail_view, name='navio_detail'),
    path("cliente/nuevo/", views.crear_cliente_view, name="crear_cliente"),


]
