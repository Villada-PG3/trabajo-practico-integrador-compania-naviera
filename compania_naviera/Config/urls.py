from django.contrib import admin
from django.urls import path, include
from compania_naviera import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    path('', views.main_view, name='home'),

    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('registro/', views.RegistroUsuario.as_view(), name='registro'),

    path('menu/', views.menu_user, name='menu_user'),
    path("pagos/", views.pagos_view, name="pagos"),

    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('cambiar_contrasenia/', views.cambiar_contrasenia, name='cambiar_contrasenia'),

    path('contacto/', views.contacto_view, name='contacto'),
    path('contacto_log/', views.contacto_log_view, name='contacto_log'),
    path('destinos/', views.destinos_view, name='destinos'),
    path("destinos/<int:pk>/", views.destino_detail_view, name="destino_detail"),

    path('mis-reservas/', views.mis_reservas_view, name='mis_reservas'),
    path('reservas/nueva/', views.crear_reserva_view, name='crear_reserva'),

    # Cruceros + detalle
    path('cruceros/', views.cruceros_view, name='cruceros'),
    path('cruceros/<int:pk>/', views.navio_detail_view, name='navio_detail'),
    path("cliente/nuevo/", views.crear_cliente_view, name="crear_cliente"),


    # Ofertas (usada por base.html)
    path('ofertas/', views.ofertas_view, name='ofertas'),
]
