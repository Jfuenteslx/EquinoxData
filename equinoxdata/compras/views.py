from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Compra, Pedido, ProductoBase
from productos.models import ProductoBase
from django.utils import timezone
import json

# Vista para registrar una compra
@login_required
def crear_compra(request):
    fecha_actual = timezone.now().date()  # Asegúrate de usar timezone.now()

    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad'))
        precio = float(request.POST.get('precio'))
        usuario = request.user

        # Validaciones
        if cantidad <= 0:
            messages.error(request, "La cantidad debe ser un número positivo.")
            return redirect('compras:crear_compra')
        if precio <= 0:
            messages.error(request, "El precio debe ser un número positivo.")
            return redirect('compras:crear_compra')

        try:
            producto = ProductoBase.objects.get(id=producto_id)

            # Crear y guardar la compra
            compra = Compra.objects.create(
                producto=producto,
                personal=usuario,
                cantidad=cantidad,
                precio=precio,
                fecha=timezone.now()  # Asegúrate de usar timezone.now() para la fecha
            )


            # Mensaje de éxito
            messages.success(request, f"Compra registrada con éxito. {cantidad} unidades de {producto.nombre} adquiridas.")
            return redirect('compras:crear_compra')

        except ProductoBase.DoesNotExist:
            messages.error(request, "El producto seleccionado no existe.")
            return redirect('compras:crear_compra')

    else:
        # Consultar las compras del día
        compras_del_dia = Compra.objects.filter(fecha__date=fecha_actual).select_related('producto')
        productos = ProductoBase.objects.all()

        return render(request, 'compras/crear_compra.html', {
            'productos': productos,
            'compras_del_dia': compras_del_dia,
            'fecha_actual': fecha_actual
        })


@login_required
def eliminar_compra(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id)
    compra.delete()
    messages.success(request, f"La compra de {compra.producto.nombre} ha sido eliminada.")
    return redirect('compras:crear_compra')

# vistas para consolidar compras
# importante!!!!

# Vista para consolidar pedidos con paso intermedio
@login_required
def consolidar_pedido(request):
    if request.method == "POST":
        # Paso 1: Generar los datos del pedido
        compras_hoy = Compra.objects.filter(
            fecha__date=timezone.now().date()  # Usa timezone.now() para la fecha actual
        ).select_related('producto')
        
        pedido_data = [
            {
                "producto": compra.producto.nombre,
                "cantidad": compra.cantidad,
                "precio": float(compra.precio),
            }
            for compra in compras_hoy
        ]
        
        print("Pedido Data:", pedido_data)  # Debug: Verifica que los datos estén presentes

        if pedido_data:
            # Almacena los datos del pedido temporalmente en la sesión para confirmar después
            request.session['pedido_data'] = pedido_data
            return redirect('compras:confirmar_consolidacion')  # Redirige a la vista de confirmación
        else:
            messages.warning(request, "No hay compras registradas para hoy para consolidar.")
            return redirect('compras:consolidar_pedido')

    return render(request, 'compras/consolidar_pedido.html')

# Vista para confirmar la consolidación del pedido
@login_required
def confirmar_consolidacion(request):
    # Recuperar los datos del pedido desde la sesión
    pedido_data = request.session.get('pedido_data', None)
    
    if not pedido_data:
        messages.error(request, "No se encontró información de pedido para confirmar.")
        return redirect('compras:consolidar_pedido')  # Regresar si no hay datos
    
    if request.method == "POST":
        # Paso 2: Confirmar la consolidación y guardar el pedido en la base de datos
        nuevo_pedido = Pedido.objects.create(
            fecha=timezone.now(),
            pedido=pedido_data
        )

        if nuevo_pedido.pk:
            messages.success(request, "Pedido consolidado y registrado exitosamente.")
            # Redirige a la vista de confirmación final
            return redirect('compras:registro_exitoso')
        else:
            messages.error(request, "Error al registrar el pedido.")
            return redirect('compras:consolidar_pedido')

    return render(request, 'compras/confirmar_consolidacion.html', {'pedido_data': pedido_data})

# Vista para mostrar mensaje de éxito después de la consolidación
@login_required
def registro_exitoso(request):
    # Se muestra el mensaje de éxito y los detalles del pedido
    return render(request, 'compras/registro_exitoso.html')