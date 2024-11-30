from django.core.exceptions import ValidationError
from django.db import models

class PresentacionProducto(models.Model):
    nombre = models.CharField(max_length=255)  # Nombre para identificar la presentación
    presentacion = models.CharField(
        max_length=255,
        choices=[
            ('Botella', 'Botella'),
            ('Vaso', 'Vaso'),
            ('Jarra', 'Jarra'),
            ('Cóctel', 'Cóctel'),
            ('Lata', 'Lata'),
            ('Sin Alcohol', 'Bebida sin alcohol'),
        ]
    )  # Tipo de presentación
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio de venta al cliente
    receta = models.ManyToManyField(
        'Receta',
        blank=True,
        related_name='presentaciones'
    )  # Recetas asociadas a la presentación (opcional)
    activo = models.BooleanField(default=True)  # Indica si está disponible para la venta

    def __str__(self):
        return f"{self.nombre} - {self.presentacion} (${self.precio})"

    class Meta:
        verbose_name = "Presentación de Producto"
        verbose_name_plural = "Presentaciones de Productos"


class ProductoBase(models.Model):
    nombre = models.CharField(max_length=100)
    presentacion = models.CharField(max_length=100)  # Por ejemplo: botella de licor, lata de cerveza
    categoria = models.BooleanField(default=False)  # True para insumo, False para producto final
    medidas = models.CharField(max_length=100, blank=True, null=True)  # Medidas solo si es insumo
    cantidad = models.IntegerField()

    def __str__(self):
        return self.nombre





class Receta(models.Model):
    producto_final = models.CharField(
        max_length=255,
        help_text="Nombre del producto final asociado a esta receta",
        null=True,  # Permitir valores nulos temporalmente
        blank=True
    )
    insumo = models.ForeignKey(
        'ProductoBase',  # Asegúrate de importar este modelo si está en otro archivo
        on_delete=models.CASCADE,
        help_text="Insumo utilizado en la receta"
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Cantidad del insumo requerida para esta receta"
    )

    def __str__(self):
        return f"Receta de {self.producto_final} - {self.insumo.nombre}"

    def clean(self):
        """
        Valida que la cantidad del insumo sea mayor a cero.
        """
        if self.cantidad <= 0:
            raise ValidationError("La cantidad del insumo debe ser mayor a cero.")

    class Meta:
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"
        constraints = [
            models.UniqueConstraint(
                fields=['producto_final', 'insumo'],
                name='unique_receta_insumo'
            )
        ]