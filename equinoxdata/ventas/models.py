from django.db import models
from django.apps import apps
from usuarios.models import Usuario
from productos.models import PresentacionProducto
from django.utils import timezone



class SesionDeTrabajo(models.Model):
    ESTADO_SESION = [
        ('abierta', 'Abierta'),
        ('cerrada', 'Cerrada'),
    ]
    
    usuario_encargado = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(auto_now_add=True)  # Fecha de inicio se asigna automáticamente al crear la sesión
    fecha_fin = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_SESION, default='abierta')
    total_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Sesión de trabajo de {self.usuario_encargado.username} - {self.estado}"

    def cerrar_sesion(self):
        """
        Cerrar la sesión marcándola como cerrada y registrando la fecha_fin.
        También asegura que el total de ventas esté calculado antes de cerrar.
        """
        if self.estado == 'abierta':
            self.estado = 'cerrada'
            self.fecha_fin = timezone.now()
            self.calcular_total_ventas()  # Calculamos el total antes de cerrar la sesión
            self.save()

    def calcular_total_ventas(self):
        """
        Calcular el total de ventas asociadas a esta sesión.
        Suma el total de todas las ventas que pertenecen a la sesión.
        """
        from ventas.models import Comanda  # Asegúrate de importar Comanda
        comandas = Comanda.objects.filter(sesion_de_trabajo=self)
        
        # Verifica si las comandas existen y calcula la suma
        if comandas.exists():
            self.total_ventas = sum(comanda.total for comanda in comandas)
            self.save()
        else:
            # Si no hay comandas, el total de ventas será 0
            self.total_ventas = 0
            self.save()

    
    
class Comanda(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Usuario que realiza la venta (mesero, bartender)
    producto = models.ForeignKey(PresentacionProducto, on_delete=models.CASCADE)  # Producto vendido
    cantidad = models.IntegerField()  # Cantidad vendida
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Precio total de la venta
    sesion_de_trabajo = models.ForeignKey(SesionDeTrabajo, on_delete=models.CASCADE, related_name='comandas')  # Relación con la sesión de trabajo

    def __str__(self):
        return f"Comanda de {self.producto.nombre} - {self.cantidad} unidades"

    def save(self, *args, **kwargs):
        """Sobrescribir el método save para actualizar el total de ventas en la sesión"""
        super().save(*args, **kwargs)  # Guarda la comanda
        self.sesion_de_trabajo.calcular_total_ventas()  # Actualiza el total de ventas de la sesión

    
class Venta(models.Model):
    presentacion_producto = models.ForeignKey(PresentacionProducto, on_delete=models.CASCADE)
    fecha = models.DateField()
    cantidad_total = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    sesion_de_trabajo = models.ForeignKey(SesionDeTrabajo, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return f"Venta de {self.cantidad_total} unidades de {self.presentacion_producto} el {self.fecha}"



    # def save(self, *args, **kwargs):
    #     """Sobrescribimos el método save para consolidar ventas antes de guardar la cuenta"""
    #     if not self.pk:
    #         # Verificar si ya existe una cuenta para esa fecha
    #         if Cuenta.objects.filter(fecha=self.fecha).exists():
    #             raise ValueError(f"Ya existe una cuenta para la fecha {self.fecha}.")
    #         self.consolidar_ventas()  # Consolidamos las ventas antes de guardar la cuenta
    #     super().save(*args, **kwargs)  # Llamamos al save original para guardar el modelo

from django.db import models
from django.apps import apps
from decimal import Decimal

def decimal_to_float(data):
    """Convierte los valores Decimal en un diccionario o lista a float."""
    if isinstance(data, dict):
        return {k: decimal_to_float(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [decimal_to_float(item) for item in data]
    elif isinstance(data, Decimal):
        return float(data)
    return data

class Cuenta(models.Model):
    fecha = models.DateField(unique=True)  # Fecha única para evitar duplicados
    cuenta = models.JSONField(default=dict)  # Almacena detalles consolidados en formato JSON

    def __str__(self):
        return f"Cuenta del {self.fecha}"

    def consolidar_ventas(self):
        """Consolidar las ventas de la fecha de la cuenta, generando un JSON con los productos y cantidades."""
        Venta = apps.get_model('ventas', 'Venta')  # Obtener el modelo Venta dinámicamente
        ventas = Venta.objects.filter(fecha=self.fecha)  # Filtrar las ventas por la fecha
        detalles = {}  # Diccionario para consolidar las ventas

        for venta in ventas:
            producto_nombre = venta.presentacion_producto.nombre  # Nombre del producto relacionado
            cantidad = venta.cantidad_total  # Cantidad total vendida
            total = venta.total  # Total de la venta

            # Si el producto ya existe en el JSON, acumular la cantidad y el total
            if producto_nombre in detalles:
                detalles[producto_nombre]['cantidad'] += cantidad
                detalles[producto_nombre]['total'] += total
            else:
                detalles[producto_nombre] = {
                    'cantidad': cantidad,
                    'total': total
                }

        # Convertir los valores Decimal a float para evitar errores al guardar
        self.cuenta = decimal_to_float(detalles)

    def save(self, *args, **kwargs):
        """Sobrescribimos el método save para consolidar ventas antes de guardar la cuenta."""
        if not self.pk:  # Solo consolidar si la cuenta es nueva
            if Cuenta.objects.filter(fecha=self.fecha).exists():
                raise ValueError(f"Ya existe una cuenta para la fecha {self.fecha}.")
            self.consolidar_ventas()  # Consolidamos las ventas antes de guardar la cuenta

        # Convertir el campo cuenta a un formato serializable antes de guardar
        if isinstance(self.cuenta, (dict, list)):
            self.cuenta = decimal_to_float(self.cuenta)

        super().save(*args, **kwargs)  # Llamar al método save original para guardar el modelo


def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    inventario = Inventario.objects.get(producto=self.producto.producto_base)
    inventario.calcular_stock_final()
