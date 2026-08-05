from django.db import models
from django.utils import timezone
from decimal import Decimal


class SesionTrabajo(models.Model):
    """
    Sesión de trabajo de un mesero o bartender durante un evento.
    Un usuario solo puede tener una sesión por evento.
    """
    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('cerrada', 'Cerrada'),
    ]

    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='sesiones_trabajo'
    )
    evento = models.ForeignKey(
        'eventos.Evento',
        on_delete=models.PROTECT,
        related_name='sesiones_trabajo'
    )
    es_barra = models.BooleanField(
        default=False,
        help_text="True si esta sesión corresponde a la barra."
    )
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='abierta'
    )
    fecha_apertura = models.DateTimeField(default=timezone.now)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Sesión de trabajo"
        verbose_name_plural = "Sesiones de trabajo"
        unique_together = [['usuario', 'evento']]
        ordering = ['-fecha_apertura']

    def __str__(self):
        tipo = "Barra" if self.es_barra else "Mesero"
        return f"{self.usuario.username} — {self.evento.nombre} ({tipo})"

    @property
    def total_ventas(self):
        return self.comandas.filter(
            estado='entregada'
        ).aggregate(
            total=models.Sum('total')
        )['total'] or Decimal('0')

    @property
    def total_comandas(self):
        return self.comandas.filter(estado='entregada').count()

    @property
    def total_anuladas(self):
        return self.comandas.filter(estado='anulada').count()


class Comanda(models.Model):
    """
    Orden de productos de un mesero o barra.
    Mesero: sigue el flujo pendiente → lista → entregada → cobrada
    Barra: comanda registrada = cobrada directamente
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('lista', 'Lista'),
        ('entregada', 'Entregada'),
        ('cobrada', 'Cobrada'),
        ('anulada', 'Anulada'),
    ]

    sesion = models.ForeignKey(
        SesionTrabajo,
        on_delete=models.PROTECT,
        related_name='comandas'
    )
    referencia = models.CharField(
        max_length=100,
        blank=True,
        help_text="Referencia libre opcional (ej: Mesa 3, Cumpleañero, etc.)"
    )
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0
    )
    creada_en = models.DateTimeField(default=timezone.now)
    actualizada_en = models.DateTimeField(auto_now=True)
    anulada_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='comandas_anuladas',
        help_text="Usuario que autorizó la anulación (debe ser bartender o admin)."
    )
    motivo_anulacion = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Comanda"
        verbose_name_plural = "Comandas"
        ordering = ['-creada_en']

    def __str__(self):
        ref = f" — {self.referencia}" if self.referencia else ""
        return f"Comanda #{self.id}{ref} ({self.get_estado_display()})"

    def calcular_total(self):
        self.total = self.items.aggregate(
            total=models.Sum(
                models.F('cantidad') * models.F('precio_unitario'),
                output_field=models.DecimalField()
            )
        )['total'] or Decimal('0')
        self.save(update_fields=['total'])


class ItemComanda(models.Model):
    """Producto individual dentro de una comanda."""

    comanda = models.ForeignKey(
        Comanda,
        on_delete=models.CASCADE,
        related_name='items'
    )
    producto = models.ForeignKey(
        'productos.ProductoMenu',
        on_delete=models.PROTECT,
        related_name='items_comanda'
    )
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Precio al momento de la venta."
    )

    class Meta:
        verbose_name = "Item de comanda"
        verbose_name_plural = "Items de comanda"

    def __str__(self):
        return f"{self.cantidad} × {self.producto.nombre} @ {self.precio_unitario} bs"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
