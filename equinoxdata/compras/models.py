from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from usuarios.models import Usuario
from productos.models import ProductoBase  # Asumiendo que el ProductoBase está en la app productos


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


class Pedido(models.Model):
    fecha = models.DateField()
    pedido = models.JSONField()  # Información del pedido (detalles de los productos y cantidades)


    def __str__(self):
        return f"Pedido realizado el {self.fecha} relacionado con la compra {self.compra.id}"



def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    inventario = Inventario.objects.get(producto=self.producto)
    inventario.calcular_stock_final()
