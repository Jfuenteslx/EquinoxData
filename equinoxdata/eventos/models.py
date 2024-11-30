from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError

class Cover(models.Model):
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio del cover (entrada)
    promo = models.CharField(max_length=30, null=True, blank=True)  # Promoción asociada al cover (si existe)
    total_asistentes = models.IntegerField(default=0)  # Total de asistentes al evento
    ingresos = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Total de ingresos por cover
    grupo_etario = models.CharField(max_length=30, null=True, blank=True)  # Público objetivo (ej. mayores de 18 años)


    class Meta:
        verbose_name = 'Cover'
        verbose_name_plural = 'Covers'

    def __str__(self):
        return f"Cover: {self.promo or 'General'}, Precio: {self.precio}, Asistentes: {self.total_asistentes}"

    def clean(self):
        if self.precio < 0:
            raise ValidationError("El precio del cover no puede ser negativo.")
        if self.total_asistentes < 0:
            raise ValidationError("El número de asistentes no puede ser negativo.")

    @property
    def calcular_ingresos(self):
        return self.precio * self.total_asistentes
    
    

class Evento(models.Model):
    nombre = models.CharField(max_length=255)  # Nombre del evento
    flyer = models.ImageField(upload_to='flyers/', null=True, blank=True)  # Imagen promocional
    banda = models.CharField(max_length=150, null=True, blank=True)  # Artista o banda asociada
    fecha = models.DateTimeField()  # Fecha y hora del evento
    descripcion = models.TextField(null=True, blank=True)  # Descripción más detallada del evento
    cover = models.OneToOneField('eventos.Cover', on_delete=models.CASCADE, related_name='evento_cover', null=True, blank=True)  # Cover asociado

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        return f"{self.nombre} - {self.fecha.strftime('%d/%m/%Y')}"

    # def clean(self):
    #     # Validar que la fecha no sea en el pasado
    #     if self.fecha < timezone.now():
    #         raise ValidationError("La fecha del evento no puede estar en el pasado.")
