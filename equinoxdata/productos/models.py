from django.db import models
from django.core.exceptions import ValidationError


class ProductoBase(models.Model):
    """Insumo físico que se almacena en inventario."""

    UNIDAD_CHOICES = [
        ('botella', 'Botella'),
        ('unidad', 'Unidad'),
    ]

    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.CharField(
        max_length=20,
        choices=UNIDAD_CHOICES,
        default='botella'
    )
    contenido_neto_ml = models.IntegerField(
        help_text="Contenido neto en ml (ej: 750, 1000). Solo para botellas.",
        null=True,
        blank=True
    )
    medidas_por_unidad = models.IntegerField(
        help_text="Cantidad de medidas por botella/unidad (ej: 16 para 750ml).",
        default=1
    )
    precio_costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Precio de costo unitario (por botella o unidad)."
    )
    habilitado = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Insumo Base"
        verbose_name_plural = "Insumos Base"
        ordering = ['nombre']

    def __str__(self):
        if self.unidad_medida == 'botella':
            return f"{self.nombre} ({self.contenido_neto_ml}ml - {self.medidas_por_unidad} medidas)"
        return f"{self.nombre} (unidad)"


class ProductoMenu(models.Model):
    """Producto que aparece en la carta y se vende al cliente."""

    TIPO_CHOICES = [
        ('botella', 'Botella entera'),
        ('vaso', 'Vaso / Medida suelta'),
        ('coctel_jarra', 'Coctel / Jarra'),
        ('extra', 'Extra (cerveza, refresco, etc.)'),
    ]

    nombre = models.CharField(max_length=255, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    habilitado = models.BooleanField(default=True)

    # Para botella y vaso: insumo directo
    insumo_base = models.ForeignKey(
        ProductoBase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_menu',
        help_text="Insumo base asociado. No aplica para extras ni cocteles con receta."
    )

    # Para vaso: cuántas medidas descuenta
    medidas_por_venta = models.IntegerField(
        default=1,
        help_text="Medidas que se descuentan al vender. Solo para tipo vaso."
    )

    class Meta:
        verbose_name = "Producto del Menu"
        verbose_name_plural = "Productos del Menu"
        ordering = ['tipo', 'nombre']

    def __str__(self):
        return f"{self.nombre} - Bs. {self.precio} ({self.get_tipo_display()})"

    def clean(self):
        if self.tipo in ['botella', 'vaso'] and not self.insumo_base:
            raise ValidationError(
                f"Un producto de tipo '{self.get_tipo_display()}' debe tener un insumo base asociado."
            )
        if self.tipo == 'extra' and self.insumo_base:
            raise ValidationError(
                "Un producto de tipo 'Extra' no debe tener insumo base asociado."
            )


class RecetaItem(models.Model):
    """Ingrediente de un coctel o jarra."""

    producto_menu = models.ForeignKey(
        ProductoMenu,
        on_delete=models.CASCADE,
        related_name='receta',
        limit_choices_to={'tipo': 'coctel_jarra'}
    )
    insumo = models.ForeignKey(
        ProductoBase,
        on_delete=models.CASCADE,
        related_name='usado_en_recetas'
    )
    cantidad_medidas = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        help_text="Cantidad de medidas de este insumo en la receta."
    )

    class Meta:
        verbose_name = "Item de Receta"
        verbose_name_plural = "Items de Receta"
        unique_together = ['producto_menu', 'insumo']

    def __str__(self):
        return f"{self.cantidad_medidas} medidas de {self.insumo.nombre} en {self.producto_menu.nombre}"

    def clean(self):
        if self.cantidad_medidas <= 0:
            raise ValidationError("La cantidad de medidas debe ser mayor a cero.")

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=ProductoBase)
def crear_inventario(sender, instance, created, **kwargs):
    if created:
        from inventarios.models import Inventario
        Inventario.objects.get_or_create(producto=instance)