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
        from ventas.models import Venta  # Importación dentro del método para evitar circularidad
        ventas = Venta.objects.filter(sesion_de_trabajo=self)
        self.total_ventas = sum(venta.total for venta in ventas)
        self.save()



class Comanda(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Usuario que realiza la venta (mesero, bartender)
    producto = models.ForeignKey(PresentacionProducto, on_delete=models.CASCADE)  # Producto vendido
    cantidad = models.IntegerField()  # Cantidad vendida
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Precio total de la venta
    sesion_de_trabajo = models.ForeignKey(SesionDeTrabajo, on_delete=models.CASCADE, related_name='comandas')  # Relación con la sesión de trabajo

    def __str__(self):
        return f"Comanda de {self.producto.nombre} - {self.cantidad} unidades"
    
class Comanda(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    producto = models.ForeignKey(PresentacionProducto, on_delete=models.CASCADE)  # Relación con PresentacionProducto
    cantidad = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    sesion_de_trabajo = models.ForeignKey(SesionDeTrabajo, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} unidades"



class Venta(models.Model):
    presentacion_producto = models.ForeignKey(PresentacionProducto, on_delete=models.CASCADE, related_name='ventas')
    cantidad_total = models.PositiveIntegerField(default=0)  # Cantidad total vendida
    fecha = models.DateField(auto_now_add=True)  # Fecha de la venta
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Total de la venta

    def __str__(self):
        return f"Venta de {self.cantidad_total} unidades de {self.presentacion_producto} el {self.fecha}"


from django.db import models
from django.apps import apps

class Cuenta(models.Model):
    fecha = models.DateField(unique=True)  # Aseguramos que no haya duplicados por fecha
    cuenta = models.JSONField()  # Detalles consolidados de la cuenta en formato JSON

    def __str__(self):
        return f"Cuenta del {self.fecha}"

    def consolidar_ventas(self):
        """Consolidar las ventas de la fecha de la cuenta, generando un JSON con los productos y cantidades"""
        Venta = apps.get_model('ventas', 'Venta')  # Obtiene el modelo Venta dinámicamente
        ventas = Venta.objects.filter(fecha=self.fecha)  # Filtrar ventas por la fecha de la cuenta
        detalles = {}

        for venta in ventas:
            producto_nombre = venta.presentacion_producto.producto.nombre  # Nombre del producto relacionado
            cantidad = venta.cantidad_total  # Cantidad vendida
            total = venta.total  # Total de la venta

            # Si el producto ya existe en el JSON, acumulamos la cantidad y el total
            if producto_nombre in detalles:
                detalles[producto_nombre]['cantidad'] += cantidad
                detalles[producto_nombre]['total'] += total
            else:
                detalles[producto_nombre] = {
                    'cantidad': cantidad,
                    'total': total
                }

        # Asignamos los detalles consolidados al campo 'cuenta'
        self.cuenta = detalles

    def save(self, *args, **kwargs):
        """Sobrescribimos el método save para consolidar ventas antes de guardar la cuenta"""
        if not self.pk:
            # Verificar si ya existe una cuenta para esa fecha
            if Cuenta.objects.filter(fecha=self.fecha).exists():
                raise ValueError(f"Ya existe una cuenta para la fecha {self.fecha}.")
            self.consolidar_ventas()  # Consolidamos las ventas antes de guardar la cuenta
        super().save(*args, **kwargs)  # Llamamos al save original para guardar el modelo
