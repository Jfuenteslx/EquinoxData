from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal


class Evento(models.Model):
    nombre = models.CharField(max_length=255)
    flyer = models.ImageField(upload_to='flyers/', null=True, blank=True)
    banda = models.CharField(max_length=150, null=True, blank=True)
    fecha = models.DateTimeField()
    descripcion = models.TextField(null=True, blank=True)
    porcentaje_grupo = models.DecimalField(
        max_digits=5, decimal_places=2, default=80.00,
        help_text="Porcentaje de recaudación cover que va al grupo/artista."
    )
    porcentaje_bar = models.DecimalField(
        max_digits=5, decimal_places=2, default=20.00,
        help_text="Porcentaje de recaudación cover que va al bar."
    )

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.nombre} - {self.fecha.strftime('%d/%m/%Y')}"

    @property
    def pax_total(self):
        return sum(e.cantidad for e in self.entradas_cover.all())

    @property
    def recaudacion_cover(self):
        return sum(e.subtotal for e in self.entradas_cover.all())

    @property
    def saldo_grupo(self):
        return self.recaudacion_cover * (self.porcentaje_grupo / Decimal('100'))

    @property
    def saldo_bar(self):
        return self.recaudacion_cover * (self.porcentaje_bar / Decimal('100'))


class EntradaCover(models.Model):
    TIPO_CHOICES = [
        ('general', 'General'),
        ('preventa', 'Preventa'),
        ('promo', 'Promoción'),
        ('gratis', 'Chicas gratis'),
        ('dos_x_uno', '2x1'),
        ('vip', 'VIP'),
        ('invitado', 'Invitado'),
    ]

    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='entradas_cover'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.IntegerField(default=0)
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    class Meta:
        verbose_name = "Entrada Cover"
        verbose_name_plural = "Entradas Cover"
        unique_together = [['evento', 'tipo']]

    def __str__(self):
        return f"{self.get_tipo_display()} × {self.cantidad} — {self.evento.nombre}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario