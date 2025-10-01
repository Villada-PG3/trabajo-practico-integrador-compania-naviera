# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django_countries.fields import CountryField

class Rol(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class UsuarioPersonalizado(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, related_name='usuarios', null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        related_name="usuario_personalizado_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="usuario_personalizado_permissions_set",
        blank=True
    )

    def __str__(self):
        return self.username


class Cliente(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200)
    fecha_nacimiento = models.DateField()
    nacionalidad = CountryField(blank_label='Selecciona un país', blank=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    usuario = models.ForeignKey(UsuarioPersonalizado, on_delete=models.PROTECT, related_name='clientes')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
class EstadoPasajero(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class Pasajero(models.Model):
    reserva = models.ForeignKey('Reserva', on_delete=models.CASCADE, related_name='pasajeros')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado_pasajero = models.ForeignKey(EstadoPasajero, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
class TipoNavio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    

class Navio(models.Model):
    codigo_de_navio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    altura = models.FloatField()
    eslora = models.FloatField()
    manga = models.FloatField()
    desplazamiento = models.FloatField()
    autonomia_de_viaje = models.IntegerField()
    cantidad_maxima_de_pasajeros = models.IntegerField()
    cantidad_de_motores = models.IntegerField()
    tipo_navio = models.ForeignKey(TipoNavio, on_delete=models.PROTECT)
    imagen = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Cubierta(models.Model):
    numero_de_cubierta = models.IntegerField()
    navio = models.ForeignKey(Navio, on_delete=models.CASCADE, related_name='cubiertas')
    descripcion = models.TextField()
    encargado = models.CharField(max_length=100)

    def __str__(self):
        return f"Cubierta {self.numero_de_cubierta} - {self.navio.nombre}"
    
class EstadoCamarote(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.descripcion
    
class TipoCamarote(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class Camarote(models.Model):
    numero_de_camarote = models.IntegerField()
    cubierta = models.ForeignKey(Cubierta, on_delete=models.CASCADE, related_name='camarotes')
    estado_camarote = models.ForeignKey(EstadoCamarote, on_delete=models.PROTECT)
    tipo_camarote = models.ForeignKey(TipoCamarote, on_delete=models.PROTECT)
    imagen = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Camarote {self.numero_de_camarote} - {self.cubierta.navio.nombre}"
    
class TipoItinerario(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    


class Itinerario(models.Model):
    categoria = models.ForeignKey(TipoItinerario, on_delete=models.PROTECT)
    imagen = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Itinerario {self.id}"
    
class Orden(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    orden = models.IntegerField()
    itinerario = models.ForeignKey(Itinerario, on_delete=models.CASCADE, related_name='ordenes')

    def __str__(self):
        return self.nombre
    

class Puerto(models.Model):
    nombre = models.CharField(max_length=100)
    itinerario = models.ForeignKey(Itinerario, on_delete=models.CASCADE, related_name='puertos')
    orden = models.IntegerField()
    
    def __str__(self):
        return self.nombre

class UbicacionPuerto(models.Model):
    puerto = models.ForeignKey(Puerto, on_delete=models.CASCADE, related_name='ubicaciones')
    nro_muelle = models.IntegerField()
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.nombre} - Muelle {self.nro_muelle}"
    
class ActividadPosible(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    
    def __str__(self):
        return self.nombre
    
class PuertoxActividad(models.Model):
    puerto = models.ForeignKey(Puerto, on_delete=models.CASCADE, related_name='actividades')
    actividad = models.ForeignKey(ActividadPosible, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.puerto.nombre} - {self.actividad.nombre}"
    
class Viaje(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_de_salida = models.DateField()
    fecha_fin = models.DateField()
    hora_salida = models.TimeField()
    hora_llegada = models.TimeField()
    lugar_destino = CountryField(blank_label='Selecciona un país', blank=True)
    fecha_actual = models.DateField()
    imagen = models.URLField(blank=True, null=True)

    def __str__(self):  
        return self.nombre
    
class ViajeXNavio(models.Model):
    navio = models.ForeignKey(Navio, on_delete=models.PROTECT)
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE)
    precio = models.IntegerField(default=0)  

    def __str__(self):  
        return f"{self.precio}"  

    def __str__(self):
        return f"{self.viaje.nombre} - {self.navio.nombre}"
    
class ItinerarioViaje(models.Model):
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE)
    itinerario = models.ForeignKey(Itinerario, on_delete=models.CASCADE)

class Tripulante(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    nombre = models.CharField(max_length=100)
    legajo = models.CharField(max_length=50)
    dni = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200)
    fecha_nacimiento = models.DateField()
    nacionalidad = CountryField(blank_label='Selecciona un país', blank=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)

    def __str__(self):
        return self.nombre
    
class AsignacionTripulanteViaje(models.Model):
    tripulante = models.ForeignKey(Tripulante, on_delete=models.CASCADE)
    viaje_navio = models.ForeignKey(ViajeXNavio, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

class OcupacionCamarote(models.Model):
    camarote = models.ForeignKey(Camarote, on_delete=models.CASCADE)
    tripulante = models.ForeignKey(Tripulante, on_delete=models.SET_NULL, null=True, blank=True)
    pasajero = models.ForeignKey(Pasajero, on_delete=models.SET_NULL, null=True, blank=True)
    viaje_navio = models.ForeignKey(ViajeXNavio, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

class EstadoReserva(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class Reserva(models.Model):
    descripcion = models.TextField()
    viaje_navio = models.ForeignKey(ViajeXNavio, on_delete=models.CASCADE)
    estado_reserva = models.ForeignKey(EstadoReserva, on_delete=models.PROTECT)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class HistorialReserva(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    fecha_cambio = models.DateField()
    cambio_realizado = models.TextField()

class MetodoPago(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self): 
        return self.nombre

class EstadoPago(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class Pago(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='pagos')
    fecha_pago = models.DateField()
    monto = models.FloatField()
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT)
    estado_pago = models.ForeignKey(EstadoPago, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class HistorialPago(models.Model):
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE)
    fecha_cambio = models.DateField()
    cambio_realizado = models.TextField()
    estado_pago = models.ForeignKey(EstadoPago, on_delete=models.PROTECT)
    usuario_responsable = models.ForeignKey(UsuarioPersonalizado, on_delete=models.PROTECT)