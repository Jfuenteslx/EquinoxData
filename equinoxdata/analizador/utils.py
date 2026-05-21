import random
from productos.models import ProductoBase


def simular_ventas(evento):
    asistencia_estimada = random.randint(50, 200)
    ventas = {}
    productos = ProductoBase.objects.all()
    for producto in productos:
        cantidad_vendida = random.randint(0, 5) * asistencia_estimada
        ventas[producto.nombre] = cantidad_vendida
    return ventas


def simular_compras(ventas):
    if not isinstance(ventas, dict):
        raise ValueError("El parámetro 'ventas' debe ser un diccionario.")
    compras = {}
    for producto_nombre, cantidad_vendida in ventas.items():
        compras[producto_nombre] = int(cantidad_vendida * 0.3)
    return compras


def simular_inventario(compras, ventas):
    inventario_actual = {}
    productos = ProductoBase.objects.all()
    for producto in productos:
        inventario_actual[producto.nombre] = 100
    for producto_nombre, cantidad_vendida in ventas.items():
        if producto_nombre in inventario_actual:
            inventario_actual[producto_nombre] -= cantidad_vendida
    for producto_nombre, cantidad_comprada in compras.items():
        if producto_nombre in inventario_actual:
            inventario_actual[producto_nombre] += cantidad_comprada
    return inventario_actual


def calcular_coeficiente(evento):
    return random.uniform(0, 100)


def calcular_performance(evento):
    return 0