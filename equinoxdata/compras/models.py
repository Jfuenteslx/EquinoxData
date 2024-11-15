from django.db import models
from django.core.exceptions import ValidationError
from usuarios.models import Usuario
from productos.models import ProductoBase  # Relación con ProductoBase
from django.utils import timezone

class Compra(models.Model):
    producto = models.ForeignKey(ProductoBase, on_delete=models.CASCADE)  # Relación con ProductoBase
    personal = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Usuario que registra la compra
    cantidad = models.IntegerField()  # Cantidad de botellas compradas
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio de compra por botella
    fecha = models.DateTimeField(default=timezone.now)  # Usando timezone.now()


    def __str__(self):
        return f"Compra de {self.cantidad} botellas de {self.producto.nombre} por {self.precio} cada una"

    def clean(self):
        """
        Validaciones personalizadas antes de guardar la compra.
        Asegura que la cantidad y el precio sean válidos.
        """
        # Validar que la cantidad no sea negativa
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")

        # Validar que el precio no sea negativo o cero
        if self.precio <= 0:
            raise ValidationError("El precio debe ser mayor que cero.")

    def save(self, *args, **kwargs):
        """
        Sobrescribimos el método `save` para realizar las siguientes acciones:
        1. Validar los datos antes de guardar.
        2. Actualizar el inventario de `ProductoBase` después de guardar la compra.
        """
        # Validamos los datos antes de guardar
        self.clean()

        # Guardamos la compra
        super().save(*args, **kwargs)

        # Actualizar el inventario de ProductoBase
        if self.cantidad > 0:
            self.producto.stock_botellas += self.cantidad  # Sumamos las botellas compradas al inventario
            self.producto.save()  # Guardamos el ProductoBase con el nuevo stock

class Pedido(models.Model):
    fecha = models.DateField()
    pedido = models.JSONField()  # Información del pedido (detalles de los productos y cantidades)


    def __str__(self):
        return f"Pedido realizado el {self.fecha} relacionado con la compra {self.compra.id}"
