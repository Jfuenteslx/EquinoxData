from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Compra, DetalleCompra
from productos.models import ProductoBase
from inventarios.models import Inventario, MovimientoInventario


@login_required
def crear_compra(request):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')

    if request.method == 'POST':
        # Crear cabecera de compra
        compra = Compra.objects.create(
            personal=request.user,
            observaciones=request.POST.get('observaciones', '')
        )

        # Procesar cada producto del formulario
        productos_ids = request.POST.getlist('producto_id')
        cantidades = request.POST.getlist('cantidad')
        precios = request.POST.getlist('precio_unitario')

        if not productos_ids:
            compra.delete()
            messages.error(request, 'Debe agregar al menos un producto a la compra.')
            return redirect('compras:crear_compra')

        for producto_id, cantidad, precio in zip(productos_ids, cantidades, precios):
            try:
                producto = ProductoBase.objects.get(id=producto_id)
                cantidad = int(cantidad)
                precio = float(precio)

                if cantidad <= 0 or precio <= 0:
                    continue

                DetalleCompra.objects.create(
                    compra=compra,
                    producto=producto,
                    cantidad_botellas=cantidad,
                    precio_unitario=precio
                )

                # Actualizar inventario
                inventario, _ = Inventario.objects.get_or_create(producto=producto)
                inventario.botellas += cantidad
                inventario.save()

                # Registrar movimiento
                MovimientoInventario.objects.create(
                    tipo='compra',
                    producto=producto,
                    botellas=cantidad,
                    referencia=f'Compra #{compra.id}',
                    registrado_por=request.user
                )

            except (ProductoBase.DoesNotExist, ValueError):
                continue

        compra.calcular_total()
        messages.success(request, f'Compra #{compra.id} registrada correctamente.')
        return redirect('compras:crear_compra')

    productos = ProductoBase.objects.filter(habilitado=True)
    compras_recientes = Compra.objects.filter(
        fecha__date=timezone.now().date()
    ).prefetch_related('detalles__producto')

    return render(request, 'compras/crear_compra.html', {
        'productos': productos,
        'compras_recientes': compras_recientes,
        'fecha_actual': timezone.now().date(),
    })


@login_required
def eliminar_compra(request, compra_id):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('usuarios:inicio')

    compra = get_object_or_404(Compra, id=compra_id)

    # Revertir el inventario
    for detalle in compra.detalles.all():
        inventario = Inventario.objects.filter(producto=detalle.producto).first()
        if inventario:
            inventario.botellas -= detalle.cantidad_botellas
            inventario.save()

        MovimientoInventario.objects.create(
            tipo='ajuste',
            producto=detalle.producto,
            botellas=-detalle.cantidad_botellas,
            referencia=f'Eliminacion Compra #{compra.id}',
            registrado_por=request.user
        )

    compra.delete()
    messages.success(request, 'Compra eliminada y stock revertido correctamente.')
    return redirect('compras:crear_compra')