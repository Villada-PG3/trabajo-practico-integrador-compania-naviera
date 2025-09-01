from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# --- ROL ---
@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

# --- USUARIO PERSONALIZADO ---
@admin.register(UsuarioPersonalizado)
class UsuarioPersonalizadoAdmin(admin.ModelAdmin):
    list_display = ('username', 'nombre', 'apellido', 'email', 'rol', 'is_staff', 'is_active')
    list_filter = ('rol', 'is_staff', 'is_active')
    search_fields = ('username', 'nombre', 'apellido', 'email')
    ordering = ('username',)

# --- CLIENTE ---
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'dni', 'usuario', 'nacionalidad', 'genero')
    search_fields = ('nombre', 'apellido', 'dni', 'usuario__username')
    list_filter = ('nacionalidad', 'genero')

# --- ESTADO PASAJERO ---
@admin.register(EstadoPasajero)
class EstadoPasajeroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

# --- PASAJERO INLINE PARA RESERVA ---
class PasajeroInline(admin.TabularInline):
    model = Pasajero
    extra = 1

# --- RESERVA ---
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'viaje_navio', 'estado_reserva', 'created_at', 'updated_at')
    list_filter = ('estado_reserva', 'created_at', 'updated_at')
    search_fields = ('cliente__nombre', 'cliente__apellido', 'viaje_navio__viaje__nombre')
    inlines = [PasajeroInline]

# --- TIPO NAVIO ---
@admin.register(TipoNavio)
class TipoNavioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

# --- NAVIO ---
@admin.register(Navio)
class NavioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_navio', 'cantidad_maxima_de_pasajeros', 'cantidad_de_motores', 'imagen_miniatura')
    search_fields = ('nombre',)
    list_filter = ('tipo_navio',)

# --- CUBIERTA ---
@admin.register(Cubierta)
class CubiertaAdmin(admin.ModelAdmin):
    list_display = ('numero_de_cubierta', 'navio', 'encargado')
    search_fields = ('numero_de_cubierta', 'navio__nombre', 'encargado')
    list_filter = ('navio',)

# --- ESTADO CAMAROTE ---
@admin.register(EstadoCamarote)
class EstadoCamaroteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

# --- TIPO CAMAROTE ---
@admin.register(TipoCamarote)
class TipoCamaroteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

# --- CAMAROTE ---
@admin.register(Camarote)
class CamaroteAdmin(admin.ModelAdmin):
    list_display = ('numero_de_camarote', 'cubierta', 'tipo_camarote', 'estado_camarote', 'imagen_miniatura')
    search_fields = ('numero_de_camarote', 'cubierta__navio__nombre')
    list_filter = ('tipo_camarote', 'estado_camarote', 'cubierta__navio')

# --- ITINERARIO ---
@admin.register(Itinerario)
class ItinerarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'categoria', 'imagen_miniatura')
    search_fields = ('categoria__nombre',)
    list_filter = ('categoria',)

# --- ORDEN ---
@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden', 'itinerario')
    search_fields = ('nombre', 'itinerario__id')
    list_filter = ('itinerario',)

# --- PUERTO ---
@admin.register(Puerto)
class PuertoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'itinerario', 'orden')
    search_fields = ('nombre', 'itinerario__id')
    list_filter = ('itinerario',)

# --- UBICACION PUERTO ---
@admin.register(UbicacionPuerto)
class UbicacionPuertoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'puerto', 'nro_muelle')
    search_fields = ('nombre', 'puerto__nombre')
    list_filter = ('puerto',)

# --- ACTIVIDAD POSIBLE ---
@admin.register(ActividadPosible)
class ActividadPosibleAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

# --- PUERTO X ACTIVIDAD ---
@admin.register(PuertoxActividad)
class PuertoxActividadAdmin(admin.ModelAdmin):
    list_display = ('puerto', 'actividad')
    search_fields = ('puerto__nombre', 'actividad__nombre')
    list_filter = ('puerto',)

# --- VIAJE ---
@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_de_salida', 'fecha_fin', 'hora_salida', 'hora_llegada', 'lugar_destino', 'imagen_miniatura')
    search_fields = ('nombre', 'lugar_destino')
    list_filter = ('fecha_de_salida', 'fecha_fin')


# --- VIAJE X NAVIO ---
@admin.register(ViajeXNavio)
class ViajeXNavioAdmin(admin.ModelAdmin):
    list_display = ('viaje', 'navio')
    search_fields = ('viaje__nombre', 'navio__nombre')
    list_filter = ('viaje', 'navio')

# --- TRIPULANTE ---
@admin.register(Tripulante)
class TripulanteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'legajo', 'dni', 'nacionalidad', 'genero')
    search_fields = ('nombre', 'dni', 'legajo')
    list_filter = ('nacionalidad', 'genero')

# --- ASIGNACION TRIPULANTE VIAJE ---
@admin.register(AsignacionTripulanteViaje)
class AsignacionTripulanteViajeAdmin(admin.ModelAdmin):
    list_display = ('tripulante', 'viaje_navio', 'fecha_inicio', 'fecha_fin')
    search_fields = ('tripulante__nombre', 'viaje_navio__viaje__nombre')
    list_filter = ('fecha_inicio', 'fecha_fin')

# --- OCUPACION CAMAROTE ---
@admin.register(OcupacionCamarote)
class OcupacionCamaroteAdmin(admin.ModelAdmin):
    list_display = ('camarote', 'tripulante', 'pasajero', 'viaje_navio', 'fecha_inicio', 'fecha_fin')
    search_fields = ('camarote__numero_de_camarote', 'tripulante__nombre', 'pasajero__nombre')
    list_filter = ('viaje_navio',)

# --- ESTADO RESERVA ---
@admin.register(EstadoReserva)
class EstadoReservaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

# --- HISTORIAL RESERVA ---
@admin.register(HistorialReserva)
class HistorialReservaAdmin(admin.ModelAdmin):
    list_display = ('reserva', 'fecha_cambio', 'cambio_realizado')
    search_fields = ('reserva__id',)

# --- METODO PAGO ---
@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

# --- ESTADO PAGO ---
@admin.register(EstadoPago)
class EstadoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

# --- PAGO ---
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('reserva', 'fecha_pago', 'monto', 'metodo_pago', 'estado_pago', 'created_at', 'updated_at')
    search_fields = ('reserva__id',)
    list_filter = ('estado_pago', 'metodo_pago', 'fecha_pago')

# --- HISTORIAL PAGO ---
@admin.register(HistorialPago)
class HistorialPagoAdmin(admin.ModelAdmin):
    list_display = ('pago', 'fecha_cambio', 'estado_pago', 'usuario_responsable', 'cambio_realizado')
    search_fields = ('pago__reserva__id', 'usuario_responsable__username')
    list_filter = ('estado_pago',)
