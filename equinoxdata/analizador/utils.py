import random
from analizador.models import Cuenta, Pedido, RegistroStock
from productos.models import ProductoBase
from .models import Evento


# Función para simular ventas
def simular_ventas(evento):
    # Supondrás un porcentaje de asistencia basado en el tipo de evento o género musical
    asistencia_estimado = random.randint(50, 200)  # Simular asistencia entre 50 y 200 personas

    ventas = {}
    productos = ProductoBase.objects.all()
    for producto in productos:
        # Generar ventas simuladas basadas en el tipo de evento
        cantidad_vendida = random.randint(0, 5) * asistencia_estimado  # Una cantidad de venta aleatoria
        ventas[producto.nombre] = cantidad_vendida

    # Crear un objeto Cuenta simulando las ventas
    cuenta = Cuenta.objects.create(fecha=evento.fecha, cuenta=ventas)
    return cuenta


# Función para simular compras
def simular_compras(evento, ventas):
    compras = {}

    # Verifica que ventas sea un diccionario
    if isinstance(ventas, dict):
        for producto_nombre, cantidad_vendida in ventas.items():
            # Generar compras basadas en las ventas (por ejemplo, reponer un 30% de las ventas)
            cantidad_comprada = int(cantidad_vendida * 0.3)
            compras[producto_nombre] = cantidad_comprada
    else:
        raise ValueError("El parámetro 'ventas' debe ser un diccionario.")

    # Crear un objeto Pedido simulando las compras
    pedido = Pedido.objects.create(fecha=evento.fecha, pedido=compras)
    return pedido


# Función para simular inventario
def simular_inventario(evento, compras, ventas):
    inventario_actual = {}
    productos = ProductoBase.objects.all()

    # Simulando un inventario inicial con 100 unidades para cada producto
    for producto in productos:
        inventario_actual[producto.nombre] = 100  # Inventario inicial

    # Si compras es un objeto Pedido, accedemos al diccionario de compras
    if isinstance(compras, Pedido):
        compras = compras.pedido  # Acceder al diccionario 'pedido' de compras

    # Si ventas es un objeto Cuenta, accedemos al diccionario de ventas
    if isinstance(ventas, Cuenta):
        ventas = ventas.cuenta  # Acceder al diccionario 'cuenta' de ventas

    # Restando las ventas al inventario (cada venta reduce el inventario)
    for producto_nombre, cantidad_vendida in ventas.items():
        if producto_nombre in inventario_actual:  # Asegurarse de que el producto esté en el inventario
            inventario_actual[producto_nombre] -= cantidad_vendida

    # Añadiendo las compras al inventario (cada compra aumenta el inventario)
    for producto_nombre, cantidad_comprada in compras.items():
        if producto_nombre in inventario_actual:  # Asegurarse de que el producto esté en el inventario
            inventario_actual[producto_nombre] += cantidad_comprada

    # Crear un objeto RegistroStock simulando el estado del inventario
    inventario_json = inventario_actual
    registro_stock = RegistroStock.objects.create(fecha=evento.fecha, inventario_json=inventario_json)
    
    return registro_stock


import random
from .models import Evento

def calcular_coeficiente(evento):
    # Aquí, evento es el objeto que se pasa a la función
    return random.uniform(0, 100)

# Aquí es donde lo llamas
evento = Evento.objects.get(id=1)  # O el evento correcto que desees
coeficiente_simulado = calcular_coeficiente(evento)

# En utils.py
def calcular_performance(evento):
    # Lógica para calcular el performance usando el argumento evento
    performance = 0  # Aquí va tu cálculo
    return performance
