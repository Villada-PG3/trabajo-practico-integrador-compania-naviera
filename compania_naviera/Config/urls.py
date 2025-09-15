from django.contrib import admin
from django.urls import path, include
from compania_naviera import views
from django.contrib.auth import views as auth_views
from django.urls import path

from compania_naviera.views import DestinosListView
urlpatterns = [ 
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('contacto/', views.contacto_view, name='contacto'),
    path('cruceros/', views.cruceros_view, name='cruceros'),
    path("cruceros/<int:pk>/", views.navio_detail_view, name="navio_detail"),


    path("ofertas/", views.ofertas_view, name="ofertas"),

    path('login/', views.login_view, name='login'),
    path('menu/', views.menu_user, name='menu_user'),
    path('registro/', views.RegistroUsuario.as_view(), name='registro'),
    path('', views.main_view, name='home'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('contacto_log/', views.contacto_log_view, name='contacto_log'),
    path('cambiar_contrasenia/', views.cambiar_contrasenia, name='cambiar_contrasenia'),
     path("destinos/", DestinosListView.as_view(), name="destinos"),

    path('reservas/nueva/', views.crear_reserva, name='crear_reserva'),
    path('reservas/mis/', views.mis_reservas, name='mis_reservas')

]
