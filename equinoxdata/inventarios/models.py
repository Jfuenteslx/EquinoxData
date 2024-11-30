from compras.models import Compra

  #

from django.db import models
from productos.models import ProductoBase, PresentacionProducto, Receta  # Importar los modelos necesarios
from compras.models import Compra  # Relación con las compras
from ventas.models import Venta  # Relación con las ventas
from django.db.models import Sum
from django.utils import timezone

from django.db import models

  

# inventarios/models.py
from django.db.models import Sum
from ventas.models import Venta
from compras.models import Compra

class Inventario(models.Model):
    producto = models.ForeignKey(ProductoBase, on_delete=models.CASCADE)
    saldo_bodega = models.IntegerField(default=0)  # Valor inicial predeterminado
    medidas_restantes = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Valor inicial predeterminado
    fecha_ingreso = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inventario de {self.producto.nombre}"

    def actualizar_inventario(self, cantidad_vendida, medidas_por_unidad):
        """
        Actualiza el inventario según las cantidades vendidas.
        """
        if cantidad_vendida <= 0:
            raise ValueError("La cantidad vendida debe ser mayor que cero.")

        # Calcular las medidas consumidas
        medidas_consumidas = cantidad_vendida * medidas_por_unidad

        # Actualizar medidas restantes y saldo en bodega
        self.medidas_restantes -= medidas_consumidas
        if self.medidas_restantes < 0:
            unidades_a_restar = abs(self.medidas_restantes) // medidas_por_unidad
            self.saldo_bodega -= int(unidades_a_restar)
            self.medidas_restantes = medidas_por_unidad + (self.medidas_restantes % medidas_por_unidad)
        
        if self.saldo_bodega < 0:
            raise ValueError("El inventario no puede ser negativo.")
        
        self.save()


    def calcular_stock_final(self):
        """
        Calcula el stock final del inventario basado en compras y ventas.
        """
        from ventas.models import Venta
        from compras.models import Compra
        from productos.models import PresentacionProducto

        # Obtener las presentaciones del producto base
        # Cambié 'producto_base' por 'nombre' o el campo adecuado que conecte las presentaciones con el producto
        presentaciones = PresentacionProducto.objects.filter(nombre=self.producto.nombre)

        # Total de compras relacionadas con el producto
        total_compras = Compra.objects.filter(producto=self.producto).aggregate(
            total=Sum('cantidad')
        )['total'] or 0

        # Total de ventas relacionadas con las presentaciones del producto
        total_ventas = Venta.objects.filter(presentacion_producto__in=presentaciones).aggregate(
            total=Sum('cantidad_total')
        )['total'] or 0

        # Cálculo del stock final
        self.stock_final = self.saldo_bodega + total_compras - total_ventas
        self.save()




    def actualizar_estado(self):
        saldo = Saldo.objects.filter(producto=self.producto).first()
        if saldo:
            return "Suficiente" if self.stock_final >= saldo.cantidad else "Insuficiente"
        return "Saldo no definido"

    def __str__(self):
        return f"Inventario de {self.producto.nombre} - Stock final: {self.stock_final}"


class Saldo(models.Model):
    producto = models.ForeignKey(ProductoBase, on_delete=models.CASCADE)  # Relación con ProductoBase
    cantidad = models.IntegerField()  # Cantidad registrada (puede ser en unidades o medidas)
    medida = models.CharField(max_length=100)  # Medida (por ejemplo, "botellas", "medidas")
    fecha = models.DateField(default=timezone.now) 

    def __str__(self):
        return f"Saldo de {self.producto.nombre} - {self.cantidad} {self.medida} en {self.fecha}"

    class Meta:
        ordering = ['-fecha']  # Ordenar los registros por fecha descendente



def inicializar_inventarios_con_compras():
    """
    Esta función importa las compras de la base de datos y las utiliza para
    inicializar los inventarios correspondientes.
    """
    # Primero verificamos si ya existen inventarios
    if Inventario.objects.exists():
        return

    # Si no existen inventarios, entonces vamos a crearlos desde las compras
    compras = Compra.objects.values('producto').annotate(cantidad_total=Sum('cantidad'))
    
    for compra in compras:
        # Buscar el producto correspondiente en ProductoBase
        producto_base = ProductoBase.objects.get(id=compra['producto'])
        
        # Crear el inventario inicial con la cantidad comprada
        inventario = Inventario.objects.create(
            producto=producto_base,
            saldo_bodega=compra['cantidad_total'],
            stock_final=compra['cantidad_total']
        )






class RegistroStock(models.Model):
    fecha = models.DateField(auto_now_add=True)  # Fecha de consolidación
    inventario_json = models.JSONField()  # JSON consolidado del inventario

    def consolidar_inventario(self):
        """
        Consolida el inventario final en un JSON.
        """
        inventarios = Inventario.objects.all()
        inventario_data = {
            inventario.producto.nombre: {
                "saldo_bodega": inventario.saldo_bodega,
                "stock_final": inventario.stock_final
            }
            for inventario in inventarios
        }
        self.inventario_json = inventario_data
        self.save()

    def __str__(self):
        return f"Registro de stock - Fecha: {self.fecha}"

