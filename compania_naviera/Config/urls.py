from django.contrib import admin
from django.urls import path, include
from compania_naviera import views
from django.contrib.auth import views as auth_views
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('contacto/', views.contacto_view, name='contacto'),
    path('cruceros/', views.cruceros_view, name='cruceros'),
    path('reservas/', views.reservas_view, name='reservas'),
    path('ofertas/', views.ofertas_view, name='ofertas'),
    path('login/', views.login_view, name='login'),
    path('menu/', views.menu_user, name='menu_user'),
    path('registro/', views.RegistroUsuario.as_view(), name='registro'),
    path('', views.main_view, name='home'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]
