from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from usuarios.models import Usuario
from productos.models import ProductoBase


class Compra(models.Model):
    """Cabecera de una compra de insumos."""
    fecha = models.DateTimeField(default=timezone.now)
    personal = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='compras'
    )
    observaciones = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ['-fecha']

    def __str__(self):
        return f"Compra #{self.id} — {self.fecha.strftime('%d/%m/%Y')} por {self.personal.username}"

    def calcular_total(self):
        """Recalcula el total sumando todos los detalles."""
        self.total = sum(
            item.subtotal for item in self.detalles.all()
        )
        self.save()


class DetalleCompra(models.Model):
    """Detalle de cada insumo comprado."""
    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        ProductoBase,
        on_delete=models.CASCADE,
        related_name='compras'
    )
    cantidad_botellas = models.IntegerField(
        help_text="Cantidad de botellas o unidades compradas."
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Precio por botella o unidad."
    )

    class Meta:
        verbose_name = "Detalle de Compra"
        verbose_name_plural = "Detalles de Compra"

    @property
    def subtotal(self):
        return self.cantidad_botellas * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad_botellas} x {self.producto.nombre} @ Bs.{self.precio_unitario}"

    def clean(self):
        if self.cantidad_botellas <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")
        if self.precio_unitario <= 0:
            raise ValidationError("El precio debe ser mayor que cero.")
