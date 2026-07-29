from django.http import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import GastoOperativo
from cuentas.models import CierreDiario
from .models import Compra, DetalleCompra, Pedido, ItemPedido
from productos.models import ProductoBase
from inventarios.models import Inventario, MovimientoInventario


# ------------------------------------------------------------------ #
# PEDIDOS                                                              #
# ------------------------------------------------------------------ #

@login_required
def lista_pedidos(request):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')

    tipo_filtro = request.GET.get('tipo', '')
    estado_filtro = request.GET.get('estado', '')

    pedidos = Pedido.objects.select_related('solicitado_por').all()

    if tipo_filtro:
        pedidos = pedidos.filter(tipo=tipo_filtro)
    if estado_filtro:
        pedidos = pedidos.filter(estado=estado_filtro)

    return render(request, 'compras/lista_pedidos.html', {
        'pedidos': pedidos,
        'tipo_filtro': tipo_filtro,
        'estado_filtro': estado_filtro,
        'tipos': Pedido.TIPO_CHOICES,
        'estados': Pedido.ESTADO_CHOICES,
    })


@login_required
def crear_pedido(request):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('usuarios:inicio')

    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        fecha_requerida = request.POST.get('fecha_requerida') or None
        monto_aprobado = request.POST.get('monto_aprobado') or 0
        observaciones = request.POST.get('observaciones', '')
        cierre_id = request.POST.get('cierre_diario') or None

        cierre = None
        if tipo == 'extraordinario' and cierre_id:
            from cuentas.models import CierreDiario
            cierre = get_object_or_404(CierreDiario, pk=cierre_id)

        pedido = Pedido.objects.create(
            tipo=tipo,
            fecha_solicitud=timezone.now().date(),
            fecha_requerida=fecha_requerida,
            solicitado_por=request.user,
            monto_aprobado=0,
            cierre_diario=cierre,
            observaciones=observaciones,
            estado='borrador',
        )

        # Procesar items
        proveedores = request.POST.getlist('proveedor')
        productos_ids = request.POST.getlist('producto_id')
        cantidades = request.POST.getlist('cantidad_solicitada')
        precios = request.POST.getlist('precio_referencial')
        metodos = request.POST.getlist('metodo_pago')

        for proveedor, producto_id, cantidad, precio, metodo in zip(
            proveedores, productos_ids, cantidades, precios, metodos
        ):
            try:
                producto = ProductoBase.objects.get(id=producto_id)
                cantidad = int(cantidad)
                precio = float(precio)
                if cantidad <= 0:
                    continue
                ItemPedido.objects.create(
                    pedido=pedido,
                    proveedor=proveedor,
                    producto=producto,
                    cantidad_solicitada=cantidad,
                    precio_referencial=precio,
                    metodo_pago=metodo,
                )
            except (ProductoBase.DoesNotExist, ValueError):
                continue
            
        # Calcular monto aprobado automáticamente
        pedido.monto_aprobado = pedido.total_referencial
        pedido.save()

        messages.success(request, f'Pedido #{pedido.id} creado correctamente.')
        return redirect('compras:detalle_pedido', pedido_id=pedido.id)

    productos = ProductoBase.objects.filter(habilitado=True).order_by('categoria', 'nombre')

    

    # Agrupar por categoría para el selector
    from itertools import groupby
    grupos = {}
    for p in productos:
        cat = p.get_categoria_display() if p.categoria else 'Sin categoría'
        if cat not in grupos:
            grupos[cat] = []
        grupos[cat].append(p)

    # Cierres disponibles para extraordinarios
    from cuentas.models import CierreDiario
    cierres = CierreDiario.objects.filter(estado='borrador').order_by('-fecha')

    return render(request, 'compras/crear_pedido.html', {
        'grupos_productos': grupos,
        'cierres': cierres,
        'tipos': Pedido.TIPO_CHOICES,
        'metodos': ItemPedido.METODO_PAGO_CHOICES,
    })


@login_required
def detalle_pedido(request, pedido_id):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')

    pedido = get_object_or_404(Pedido, id=pedido_id)
    items = pedido.items.select_related('producto').all()
    compras = pedido.compras.prefetch_related('detalles__producto').all()

    # Agrupar items por proveedor
    proveedores = {}
    for item in items:
        if item.proveedor not in proveedores:
            proveedores[item.proveedor] = []
        proveedores[item.proveedor].append(item)

    # Calcular contraste pedido vs compra por producto
    comprado_por_producto = {}
    for compra in compras:
        for detalle in compra.detalles.all():
            pid = detalle.producto.id
            if pid not in comprado_por_producto:
                comprado_por_producto[pid] = {
                    'cantidad': 0,
                    'precio_real': detalle.precio_unitario,
                }
            comprado_por_producto[pid]['cantidad'] += detalle.cantidad_botellas

    # Enriquecer items con datos de contraste
    items_contraste = []
    for item in items:
        comprado = comprado_por_producto.get(item.producto.id, {})
        cantidad_comprada = comprado.get('cantidad', 0)
        cantidad_pendiente = max(item.cantidad_solicitada - cantidad_comprada, 0)

        if cantidad_comprada == 0:
            estado_item = 'pendiente'
        elif cantidad_comprada >= item.cantidad_solicitada:
            estado_item = 'completo'
        else:
            estado_item = 'parcial'

        items_contraste.append({
            'item': item,
            'cantidad_comprada': cantidad_comprada,
            'cantidad_pendiente': cantidad_pendiente,
            'precio_real': comprado.get('precio_real', None),
            'estado': estado_item,
        })

    # Progreso general
    total_items = sum(i['item'].cantidad_solicitada for i in items_contraste)
    total_comprado_unidades = sum(i['cantidad_comprada'] for i in items_contraste)
    progreso_pct = int((total_comprado_unidades / total_items * 100) if total_items > 0 else 0)

    return render(request, 'compras/detalle_pedido.html', {
        'pedido': pedido,
        'proveedores': proveedores,
        'compras': compras,
        'items_contraste': items_contraste,
        'progreso_pct': progreso_pct,
        'total_items': total_items,
        'total_comprado_unidades': total_comprado_unidades,
    })

@login_required
def cambiar_estado_pedido(request, pedido_id):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('usuarios:inicio')

    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        monto_aprobado = request.POST.get('monto_aprobado')
        if nuevo_estado in dict(Pedido.ESTADO_CHOICES):
            pedido.estado = nuevo_estado
            if monto_aprobado:
                pedido.monto_aprobado = monto_aprobado
            pedido.save()
            messages.success(request, f'Pedido #{pedido.id} actualizado a {pedido.get_estado_display()}.')

    return redirect('compras:detalle_pedido', pedido_id=pedido_id)


# ------------------------------------------------------------------ #
# COMPRAS                                                              #
# ------------------------------------------------------------------ #

@login_required
def crear_compra(request):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')

    if request.method == 'POST':

        pedido_id = request.POST.get('pedido_id') or None
        proveedor = request.POST.get('proveedor', '')
        metodo_pago = request.POST.get('metodo_pago', 'efectivo')
        observaciones = request.POST.get('observaciones', '')

        pedido = None
        if pedido_id:
            pedido = get_object_or_404(Pedido, id=pedido_id)

        compra = Compra.objects.create(
            personal=request.user,
            pedido=pedido,
            proveedor=proveedor,
            metodo_pago=metodo_pago,
            observaciones=observaciones,
        )

        
        productos_ids = request.POST.getlist('producto_id[]')
        cantidades = request.POST.getlist('cantidad[]')
        precios = request.POST.getlist('precio_unitario[]')
        tipos_fila = request.POST.getlist('tipo_fila[]')
        descripciones_op = request.POST.getlist('descripcion_op[]')
        categorias_op = request.POST.getlist('categoria_op[]')

        idx_op = 0

        for i in range(len(cantidades)):
            cantidad = cantidades[i]
            precio = precios[i]
            operativo = i < len(tipos_fila) and tipos_fila[i] == 'operativo'

            try:
                cantidad = float(cantidad)
                precio = float(precio)
                if cantidad <= 0 or precio <= 0:
                    continue
            except (ValueError, TypeError):
                continue

            if operativo:
                # Buscar la siguiente descripción no vacía
                descripcion = ''
                while idx_op < len(descripciones_op):
                    descripcion = descripciones_op[idx_op]
                    categoria = categorias_op[idx_op] if idx_op < len(categorias_op) else 'otro'
                    idx_op += 1
                    if descripcion:
                        break

                if not descripcion:
                    continue

                from .models import GastoOperativo
                GastoOperativo.objects.create(
                    fecha=timezone.now().date(),
                    categoria=categoria,
                    proveedor=proveedor,
                    descripcion=descripcion,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    metodo_pago=metodo_pago,
                    pedido=pedido,
                    compra=compra,          
                    registrado_por=request.user,
                )
            else:
                # Insumo — toca inventario
                producto_id = productos_ids[i] if i < len(productos_ids) else ''
                if not producto_id:
                    continue
                try:
                    producto = ProductoBase.objects.get(id=producto_id)
                except ProductoBase.DoesNotExist:
                    continue

                DetalleCompra.objects.create(
                    compra=compra,
                    producto=producto,
                    cantidad_botellas=int(cantidad),
                    precio_unitario=precio,
                )

                inventario, _ = Inventario.objects.get_or_create(producto=producto)
                inventario.botellas += int(cantidad)
                inventario.save()

                MovimientoInventario.objects.create(
                    tipo='compra',
                    producto=producto,
                    botellas=int(cantidad),
                    referencia=f'Compra #{compra.id}' + (f' — Pedido #{pedido.id}' if pedido else ''),
                    registrado_por=request.user,
                )


        compra.calcular_total()

        # Si el pedido está en borrador, pasarlo a en_proceso
        if pedido and pedido.estado == 'borrador':
            pedido.estado = 'en_proceso'
            pedido.save()

        messages.success(request, f'Compra #{compra.id} registrada correctamente.')

        if pedido:
            return redirect('compras:detalle_pedido', pedido_id=pedido.id)
        return redirect('compras:crear_compra')

    # Pedidos disponibles (aprobados o en proceso)
    pedidos_activos = Pedido.objects.filter(
        estado__in=['aprobado', 'en_proceso', 'borrador']
    ).order_by('-fecha_solicitud')

    productos = ProductoBase.objects.filter(habilitado=True).order_by('categoria', 'nombre')

    grupos = {}
    for p in productos:
        cat = p.get_categoria_display() if p.categoria else 'Sin categoría'
        if cat not in grupos:
            grupos[cat] = []
        grupos[cat].append(p)

    compras_recientes = Compra.objects.filter(
        fecha__date=timezone.now().date()
    ).prefetch_related('detalles__producto').select_related('pedido')

    return render(request, 'compras/crear_compra.html', {
        'grupos_productos': grupos,
        'pedidos_activos': pedidos_activos,
        'compras_recientes': compras_recientes,
        'metodos': Compra.METODO_PAGO_CHOICES,
        'fecha_actual': timezone.now().date(),
    })


@login_required
def eliminar_compra(request, compra_id):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('usuarios:inicio')

    compra = get_object_or_404(Compra, id=compra_id)
    pedido = compra.pedido

    for detalle in compra.detalles.all():
        inventario = Inventario.objects.filter(producto=detalle.producto).first()
        if inventario:
            inventario.botellas -= detalle.cantidad_botellas
            inventario.save()

        MovimientoInventario.objects.create(
            tipo='ajuste',
            producto=detalle.producto,
            botellas=-detalle.cantidad_botellas,
            referencia=f'Eliminación Compra #{compra.id}',
            registrado_por=request.user,
        )

    compra.delete()
    messages.success(request, 'Compra eliminada y stock revertido correctamente.')

    if pedido:
        return redirect('compras:detalle_pedido', pedido_id=pedido.id)
    return redirect('compras:crear_compra')

@login_required
def crear_gasto_operativo(request):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('usuarios:inicio')

    if request.method == 'POST':
        from .models import GastoOperativo
        from cuentas.models import CierreDiario

        categoria = request.POST.get('categoria')
        proveedor = request.POST.get('proveedor', '')
        descripcion = request.POST.get('descripcion')
        cantidad = request.POST.get('cantidad', 1)
        precio_unitario = request.POST.get('precio_unitario')
        metodo_pago = request.POST.get('metodo_pago')
        pedido_id = request.POST.get('pedido_id') or None
        cierre_id = request.POST.get('cierre_diario') or None
        observaciones = request.POST.get('observaciones', '')

        pedido = get_object_or_404(Pedido, id=pedido_id) if pedido_id else None
        cierre = get_object_or_404(CierreDiario, id=cierre_id) if cierre_id else None

        GastoOperativo.objects.create(
            fecha=request.POST.get('fecha') or timezone.now().date(),
            categoria=categoria,
            proveedor=proveedor,
            descripcion=descripcion,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            metodo_pago=metodo_pago,
            pedido=pedido,
            cierre_diario=cierre,
            registrado_por=request.user,
            observaciones=observaciones,
        )

        messages.success(request, 'Gasto operativo registrado.')

        if pedido:
            return redirect('compras:detalle_pedido', pedido_id=pedido.id)
        return redirect('compras:lista_gastos_operativos')


    pedidos_activos = Pedido.objects.filter(
        estado__in=['borrador', 'aprobado', 'en_proceso']
    ).order_by('-fecha_solicitud')
    cierres = CierreDiario.objects.filter(estado='borrador').order_by('-fecha')

    return render(request, 'compras/crear_gasto_operativo.html', {
        'categorias': GastoOperativo.CATEGORIA_CHOICES,
        'metodos': GastoOperativo.METODO_PAGO_CHOICES,
        'pedidos_activos': pedidos_activos,
        'cierres': cierres,
        'fecha_actual': timezone.now().date(),
    })


@login_required
def lista_gastos_operativos(request):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')

    from .models import GastoOperativo
    gastos = GastoOperativo.objects.select_related(
        'pedido', 'cierre_diario', 'registrado_por'
    ).all()

    return render(request, 'compras/lista_gastos_operativos.html', {
        'gastos': gastos,
    })