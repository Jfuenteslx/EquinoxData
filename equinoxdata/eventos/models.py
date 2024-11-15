from django.db import models

class Cover(models.Model):
    precio = models.IntegerField()  # Precio del cover (entrada)
    promo = models.CharField(max_length=30, null=True, blank=True)  # Promoción asociada al cover (si existe)
    total = models.IntegerField()  # Total de ingresos por cover
    etario = models.CharField(max_length=30, null=True, blank=True)  # Público objetivo del evento (ej. mayor de 18 años)

    class Meta:
        verbose_name = 'Cover'
        verbose_name_plural = 'Covers'

    def __str__(self):
        return f"Cover de {self.promo} - {self.total} personas"

class Evento(models.Model):
    nombre = models.CharField(max_length=255)  # Nombre del evento (ej. concierto, show)
    tipo = models.CharField(max_length=50, null=True, blank=True)  # Tipo del evento (ej. concierto, fiesta, etc.)
    grupo = models.CharField(max_length=150, null=True, blank=True)  # Grupo o artista asociado al evento (si aplica)
    fecha = models.DateTimeField()  # Fecha y hora del evento
    aforo = models.IntegerField(null=True, blank=True)  # Capacidad máxima del evento (aforo)
    
    # Relación con 'Cover' (si un evento tiene asociado un cover)
    cover = models.ForeignKey(Cover, null=True, blank=True, on_delete=models.SET_NULL)

    # Atributos adicionales para describir el evento
    descripcion = models.TextField(null=True, blank=True)  # Descripción más detallada del evento
    capacidad = models.IntegerField(null=True, blank=True)  # Capacidad del evento
    asistentes_estimados = models.IntegerField(null=True, blank=True)  # Estimación de asistentes

    # Relación con el personal que gestionó el evento
    personal = models.ForeignKey('usuarios.Usuario', null=True, blank=True, on_delete=models.SET_NULL, related_name='eventos')

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        return self.nombre

    def get_caso(self):
        from analizador.models import Caso  # Importación dentro del método para evitar el ciclo de importación
        return Caso.objects.filter(evento=self).first()  # Devuelve el caso asociado si existe
