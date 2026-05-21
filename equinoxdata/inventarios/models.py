from django.db import models
from django.utils import timezone
from productos.models import ProductoBase


class Inventario(models.Model):
    """Registro de stock por insumo base."""
    producto = models.OneToOneField(
        ProductoBase,
        on_delete=models.CASCADE,
        related_name='inventario'
    )
    botellas = models.IntegerField(default=0)
    medidas_sueltas = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"

    def __str__(self):
        return f"Inventario: {self.producto.nombre} — {self.botellas} botellas, {self.medidas_sueltas} medidas"


class AperturaDiaria(models.Model):
    """Conteo físico manual al inicio del turno."""
    fecha = models.DateField(default=timezone.now)
    producto = models.ForeignKey(
        ProductoBase,
        on_delete=models.CASCADE,
        related_name='aperturas'
    )
    botellas_contadas = models.IntegerField(default=0)
    medidas_contadas = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    registrado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = "Apertura Diaria"
        verbose_name_plural = "Aperturas Diarias"
        unique_together = ['fecha', 'producto']

    def __str__(self):
        return f"Apertura {self.fecha} — {self.producto.nombre}"


class MovimientoInventario(models.Model):
    """Log de cada cambio en el inventario."""
    TIPO_CHOICES = [
        ('compra', 'Compra'),
        ('venta', 'Consolidacion de ventas'),
        ('ajuste', 'Ajuste manual'),
        ('apertura', 'Apertura diaria'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    producto = models.ForeignKey(
        ProductoBase,
        on_delete=models.CASCADE,
        related_name='movimientos'
    )
    botellas = models.IntegerField(default=0)
    medidas = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    fecha = models.DateTimeField(default=timezone.now)
    referencia = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Referencia al documento origen (compra, sesion, etc.)"
    )
    registrado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.producto.nombre} ({self.fecha.strftime('%d/%m/%Y')})"
    
