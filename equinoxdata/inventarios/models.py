from django.db import models
from productos.models import ProductoBase  # Cambiado de Producto a ProductoBase


    
class Inventario(models.Model):
    producto = models.ForeignKey(ProductoBase, on_delete=models.CASCADE)  # Relación con ProductoBase
    stock_actual = models.IntegerField()

    def __str__(self):
        return f"Inventario de {self.producto_base.nombre} - {self.stock_actual} unidades"

class RegistroStock(models.Model):
    fecha = models.DateField()
    stock = models.JSONField()  # Aquí podrías almacenar detalles del stock por presentación
    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE)

    def __str__(self):
        return f"Registro de stock para {self.inventario.producto_base.nombre} - Fecha: {self.fecha}"
