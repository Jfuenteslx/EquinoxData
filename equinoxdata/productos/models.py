from django.db import models

class ProductoBase(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre del producto (ejemplo: Fernet)
    medidas = models.IntegerField()  # Medidas por botella
    stock_botellas = models.IntegerField(default=0)  # Inventario de botellas enteras

    def __str__(self):
        return f"{self.nombre} - {self.medidas} medidas"

class PresentacionProducto(models.Model):
    TIPO_PRESENTACION = [
        ('Botella', 'Botella Entera'),
        ('Vaso', 'Vaso'),
        ('Jarra', 'Jarra'),
        ('Coctel', 'Cóctel Preparado'),
        ('Cerveza', 'Lata/Botellin')
        
    ]
    
    producto = models.ForeignKey(ProductoBase, on_delete=models.CASCADE, related_name='presentaciones')
    nombre_presentacion = models.CharField(max_length=255)  # Nombre de la presentación (ejemplo: "Vaso", "Jarra")
    tipo_presentacion = models.CharField(max_length=20, choices=TIPO_PRESENTACION)  # Tipo de presentación
    consumo_por_presentacion_medidas = models.IntegerField()  # Cantidad consumida por venta en medidas
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio de venta de esta presentación
    es_ingrediente = models.BooleanField(default=False)  # True si se usa como ingrediente en un cóctel

    def __str__(self):
        return f"{self.nombre_presentacion} ({self.tipo_presentacion}) - {self.consumo_por_presentacion_medidas} medidas"

    def calcular_stock_en_botellas(self):
        """
        Calcula el stock en función de la cantidad de botellas en inventario 
        y las medidas de cada botella.
        """
        if self.consumo_por_presentacion_medidas == 0:
            return 0
        return self.producto.stock_botellas * self.producto.medidas / self.consumo_por_presentacion_medidas

class Receta(models.Model):
    presentacion = models.ForeignKey(PresentacionProducto, on_delete=models.CASCADE, related_name='recetas')
    ingrediente = models.ForeignKey(PresentacionProducto, on_delete=models.CASCADE)
    cantidad_medidas = models.IntegerField()  # Cantidad de este ingrediente usada en la receta (en medidas)

    def __str__(self):
        return f"{self.presentacion.nombre_presentacion} - Ingrediente: {self.ingrediente.nombre_presentacion} ({self.cantidad_medidas} medidas)"
