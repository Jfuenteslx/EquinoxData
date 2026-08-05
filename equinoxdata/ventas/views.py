from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from productos.models import ProductoMenu
from .models import SesionTrabajo, Comanda, ItemComanda, Consolidacion
from .forms import ComandaForm, ItemComandaForm


# ------------------------------------------------------------------ #
# SESIONES DE TRABAJO                                                  #
# ------------------------------------------------------------------ #

@login_required
def lista_sesiones(request):
    """Lista de sesiones del usuario actual."""
    sesiones = SesionTrabajo.objects.filter(
        usuario=request.user
    ).select_related('evento').order_by('-fecha_apertura')
    return render(request, 'ventas/lista_sesiones.html', {'sesiones': sesiones})


@login_required
def abrir_sesion(request):
    """Abre una nueva sesión de trabajo para el usuario."""
    if request.method == 'POST':
        evento_id = request.POST.get('evento')
        es_barra = request.POST.get('es_barra') == '1'

        from eventos.models import Evento
        evento = get_object_or_404(Evento, pk=evento_id)

        # Verificar que no existe sesión activa para este evento
        sesion_existente = SesionTrabajo.objects.filter(
            usuario=request.user,
            evento=evento
        ).first()

        if sesion_existente:
            if sesion_existente.estado == 'abierta':
                messages.warning(request, f'Ya tiene una sesión abierta para este evento.')
                return redirect('ventas:sesion_activa', pk=sesion_existente.pk)
            else:
                messages.error(request, f'Ya existe una sesión cerrada para este evento.')
                return redirect('ventas:lista_sesiones')

        sesion = SesionTrabajo.objects.create(
            usuario=request.user,
            evento=evento,
            es_barra=es_barra,
        )
        messages.success(request, f'Sesión abierta para {evento.nombre}.')
        return redirect('ventas:sesion_activa', pk=sesion.pk)

    from eventos.models import Evento
    # Solo mostrar eventos del día actual
    from datetime import date
    eventos = Evento.objects.filter(fecha=date.today()).order_by('nombre')
    return render(request, 'ventas/abrir_sesion.html', {
        'eventos': eventos,
    })


@login_required
def sesion_activa(request, pk):
    """Vista principal de la sesión de trabajo activa."""
    sesion = get_object_or_404(SesionTrabajo, pk=pk)

    # Solo el dueño de la sesión puede verla
    if sesion.usuario != request.user:
        messages.error(request, 'No tiene permisos para acceder a esta sesión.')
        return redirect('ventas:lista_sesiones')

    if sesion.estado == 'cerrada':
        return redirect('ventas:detalle_consolidacion', pk=sesion.consolidacion.pk)

    comandas = sesion.comandas.exclude(estado='anulada').order_by('-creada_en')
    productos = ProductoMenu.objects.filter(habilitado=True).order_by('tipo', 'nombre')

    # Agrupar productos por tipo
    grupos_productos = {}
    for p in productos:
        tipo = p.get_tipo_display()
        if tipo not in grupos_productos:
            grupos_productos[tipo] = []
        grupos_productos[tipo].append(p)

    return render(request, 'ventas/sesion_activa.html', {
        'sesion': sesion,
        'comandas': comandas,
        'grupos_productos': grupos_productos,
    })


@login_required
@require_POST
def cerrar_sesion(request, pk):
    """Cierra la sesión y genera la consolidación."""
    sesion = get_object_or_404(SesionTrabajo, pk=pk)

    if sesion.usuario != request.user:
        messages.error(request, 'No tiene permisos para cerrar esta sesión.')
        return redirect('ventas:lista_sesiones')

    if sesion.estado == 'cerrada':
        messages.warning(request, 'Esta sesión ya está cerrada.')
        return redirect('ventas:lista_sesiones')

# Verificar que no hay comandas pendientes o en proceso
    comandas_pendientes = sesion.comandas.filter(
        estado__in=['pendiente', 'lista']
    ).count()

    if comandas_pendientes > 0:
        messages.error(
            request,
            f'No puede cerrar la sesión con {comandas_pendientes} comanda(s) sin cobrar.'
        )
        return redirect('ventas:sesion_activa', pk=pk)

    # Actualizar inventario al cerrar sesión
    _actualizar_inventario_sesion(sesion)

    # Cerrar sesión
    sesion.estado = 'cerrada'
    sesion.fecha_cierre = timezone.now()
    sesion.save()

    # Buscar cierre diario del día
    cierre_diario = None
    try:
        from cuentas.models import CierreDiario
        from datetime import date
        cierre_diario = CierreDiario.objects.filter(
            fecha=date.today(),
            estado='borrador'
        ).first()
    except Exception:
        pass

    # Crear consolidación
    consolidacion = Consolidacion.crear_desde_sesion(sesion, cierre_diario)

    messages.success(request, f'Sesión cerrada. Total de ventas: {consolidacion.total_ventas} bs.')
    return redirect('ventas:detalle_consolidacion', pk=consolidacion.pk)


def _actualizar_inventario_sesion(sesion):
    """Actualiza el inventario basado en las comandas cobradas de la sesión."""
    from inventarios.models import Inventario, MovimientoInventario
    from decimal import Decimal

    items_cobrados = ItemComanda.objects.filter(
        comanda__sesion=sesion,
        comanda__estado='cobrada'
    ).select_related('producto__insumo_base', 'producto')

    for item in items_cobrados:
        producto_menu = item.producto

        if producto_menu.tipo == 'botella':
            # Descuenta 1 botella completa
            _descontar_inventario(
                producto_menu.insumo_base,
                botellas=item.cantidad,
                medidas=0,
                referencia=f'Venta sesión #{sesion.id}',
                usuario=sesion.usuario
            )

        elif producto_menu.tipo == 'vaso':
            # Descuenta medidas
            medidas_totales = item.cantidad * producto_menu.medidas_por_venta
            _descontar_inventario(
                producto_menu.insumo_base,
                botellas=0,
                medidas=medidas_totales,
                referencia=f'Venta sesión #{sesion.id}',
                usuario=sesion.usuario
            )

        elif producto_menu.tipo == 'coctel_jarra':
            # Descuenta según receta
            for receta_item in producto_menu.receta.all():
                medidas_totales = item.cantidad * float(receta_item.cantidad_medidas)
                _descontar_inventario(
                    receta_item.insumo,
                    botellas=0,
                    medidas=medidas_totales,
                    referencia=f'Venta sesión #{sesion.id}',
                    usuario=sesion.usuario
                )

        elif producto_menu.tipo == 'extra':
            # Descuenta 1 unidad por item
            if producto_menu.insumo_base:
                _descontar_inventario(
                    producto_menu.insumo_base,
                    botellas=item.cantidad,
                    medidas=0,
                    referencia=f'Venta sesión #{sesion.id}',
                    usuario=sesion.usuario
                )


def _descontar_inventario(insumo, botellas, medidas, referencia, usuario):
    """Descuenta del inventario y registra el movimiento."""
    from inventarios.models import Inventario, MovimientoInventario

    if not insumo:
        return

    inventario, _ = Inventario.objects.get_or_create(producto=insumo)

    # Convertir medidas a botellas si es necesario
    if medidas > 0 and insumo.medidas_por_unidad > 0:
        botellas_adicionales = int(medidas // insumo.medidas_por_unidad)
        medidas_restantes = medidas % insumo.medidas_por_unidad

        inventario.botellas = max(0, inventario.botellas - botellas - botellas_adicionales)
        inventario.medidas_sueltas = max(0, float(inventario.medidas_sueltas) - medidas_restantes)
    else:
        inventario.botellas = max(0, inventario.botellas - botellas)

    inventario.save()

    MovimientoInventario.objects.create(
        tipo='venta',
        producto=insumo,
        botellas=-botellas if botellas else 0,
        medidas=-medidas if medidas else 0,
        referencia=referencia,
        registrado_por=usuario,
    )


# ------------------------------------------------------------------ #
# COMANDAS                                                             #
# ------------------------------------------------------------------ #

@login_required
@require_POST
def crear_comanda(request, sesion_pk):
    """Crea una nueva comanda en la sesión activa."""
    sesion = get_object_or_404(SesionTrabajo, pk=sesion_pk)

    if sesion.usuario != request.user or sesion.estado == 'cerrada':
        messages.error(request, 'No puede crear comandas en esta sesión.')
        return redirect('ventas:lista_sesiones')

    referencia = request.POST.get('referencia', '')

    # Recopilar items del POST
    producto_ids = request.POST.getlist('producto_id[]')
    cantidades = request.POST.getlist('cantidad[]')

    if not producto_ids:
        messages.error(request, 'Debe agregar al menos un producto.')
        return redirect('ventas:sesion_activa', pk=sesion_pk)

    # Estado inicial según tipo de sesión
    estado_inicial = 'cobrada' if sesion.es_barra else 'pendiente'

    comanda = Comanda.objects.create(
        sesion=sesion,
        referencia=referencia,
        estado=estado_inicial,
    )

    total = 0
    for producto_id, cantidad in zip(producto_ids, cantidades):
        try:
            producto = ProductoMenu.objects.get(id=producto_id, habilitado=True)
            cantidad = int(cantidad)
            if cantidad <= 0:
                continue

            ItemComanda.objects.create(
                comanda=comanda,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio,
            )
            total += cantidad * float(producto.precio)
        except (ProductoMenu.DoesNotExist, ValueError):
            continue

    comanda.total = total
    comanda.save()

    if sesion.es_barra:
        messages.success(request, f'Venta registrada: {total:.2f} bs.')
    else:
        messages.success(request, 'Comanda enviada a barra.')

    return redirect('ventas:sesion_activa', pk=sesion_pk)


@login_required
@require_POST
def marcar_lista(request, comanda_pk):
    """Barra marca la comanda como lista para recoger."""
    comanda = get_object_or_404(Comanda, pk=comanda_pk)

    if comanda.estado != 'pendiente':
        return JsonResponse({'error': 'Estado inválido.'}, status=400)

    comanda.estado = 'lista'
    comanda.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'estado': 'lista'})
    return redirect('ventas:vista_barra')


@login_required
@require_POST
def marcar_entregada(request, comanda_pk):
    """Mesero marca la comanda como entregada al cliente."""
    comanda = get_object_or_404(Comanda, pk=comanda_pk)

    if comanda.estado != 'lista':
        messages.error(request, 'La comanda debe estar lista para marcarla como entregada.')
        return redirect('ventas:sesion_activa', pk=comanda.sesion.pk)

    comanda.estado = 'entregada'
    comanda.save()
    return redirect('ventas:sesion_activa', pk=comanda.sesion.pk)



@login_required
@require_POST
def anular_comanda(request, comanda_pk):
    """Anula una comanda. Requiere autorización de barra o admin."""
    comanda = get_object_or_404(Comanda, pk=comanda_pk)

    # Solo barra o admin puede autorizar anulación
    if request.user.rol not in ['bartender', 'jefe_barra', 'administrador']:
        messages.error(request, 'Solo barra o administración puede autorizar anulaciones.')
        return redirect('ventas:sesion_activa', pk=comanda.sesion.pk)

    if comanda.estado == 'cobrada':
        messages.error(request, 'No se puede anular una comanda ya cobrada.')
        return redirect('ventas:sesion_activa', pk=comanda.sesion.pk)

    motivo = request.POST.get('motivo', '')
    comanda.estado = 'anulada'
    comanda.anulada_por = request.user
    comanda.motivo_anulacion = motivo
    comanda.save()

    messages.success(request, f'Comanda #{comanda.id} anulada.')
    return redirect('ventas:sesion_activa', pk=comanda.sesion.pk)

@login_required
def comandas_listas_json(request, sesion_pk):
    """Endpoint para polling de comandas listas en la sesión del mesero."""
    sesion = get_object_or_404(SesionTrabajo, pk=sesion_pk)
    
    if sesion.usuario != request.user:
        return JsonResponse({'comandas': []})
    
    comandas = Comanda.objects.filter(
        sesion=sesion,
        estado='lista'
    ).prefetch_related('items__producto')

    data = []
    for c in comandas:
        data.append({
            'id': c.id,
            'referencia': c.referencia or '—',
            'items': [
                {'producto': item.producto.nombre, 'cantidad': item.cantidad}
                for item in c.items.all()
            ],
            'total': str(c.total),
        })

    return JsonResponse({'comandas': data})


# ------------------------------------------------------------------ #
# VISTA DE BARRA                                                       #
# ------------------------------------------------------------------ #

@login_required
def vista_barra(request):
    """
    Pantalla dedicada para barra.
    Muestra comandas pendientes de todos los meseros en tiempo real.
    """
    if request.user.rol not in ['bartender', 'jefe_barra', 'administrador']:
        messages.error(request, 'No tiene permisos para acceder a esta vista.')
        return redirect('usuarios:inicio')

    from datetime import date
    from eventos.models import Evento

    # Evento del día
    evento_hoy = Evento.objects.filter(fecha=date.today()).first()

    comandas_pendientes = []
    if evento_hoy:
        comandas_pendientes = Comanda.objects.filter(
            sesion__evento=evento_hoy,
            sesion__es_barra=False,
            estado='pendiente'
        ).prefetch_related('items__producto').select_related('sesion__usuario').order_by('creada_en')

    return render(request, 'ventas/vista_barra.html', {
        'evento_hoy': evento_hoy,
        'comandas_pendientes': comandas_pendientes,
    })


@login_required
def comandas_pendientes_json(request):
    """Endpoint para polling de comandas pendientes desde la vista de barra."""
    from datetime import date
    from eventos.models import Evento

    evento_hoy = Evento.objects.filter(fecha=date.today()).first()
    if not evento_hoy:
        return JsonResponse({'comandas': []})

    comandas = Comanda.objects.filter(
        sesion__evento=evento_hoy,
        sesion__es_barra=False,
        estado='pendiente'
    ).prefetch_related('items__producto').select_related('sesion__usuario').order_by('creada_en')

    data = []
    for c in comandas:
        data.append({
            'id': c.id,
            'mesero': c.sesion.usuario.username,
            'referencia': c.referencia or '—',
            'items': [
                {
                    'producto': item.producto.nombre,
                    'cantidad': item.cantidad,
                }
                for item in c.items.all()
            ],
            'creada_en': c.creada_en.strftime('%H:%M'),
        })

    return JsonResponse({'comandas': data})


# ------------------------------------------------------------------ #
# CONSOLIDACION                                                        #
# ------------------------------------------------------------------ #

@login_required
def detalle_consolidacion(request, pk):
    """Resumen de ventas de una sesión cerrada."""
    consolidacion = get_object_or_404(Consolidacion, pk=pk)

    if consolidacion.sesion.usuario != request.user and \
       request.user.rol not in ['administrador', 'jefe_barra']:
        messages.error(request, 'No tiene permisos para ver esta consolidación.')
        return redirect('ventas:lista_sesiones')

    comandas = consolidacion.sesion.comandas.exclude(
        estado='anulada'
    ).prefetch_related('items__producto').order_by('-creada_en')

    return render(request, 'ventas/detalle_consolidacion.html', {
        'consolidacion': consolidacion,
        'comandas': comandas,
    })


@login_required
def lista_consolidaciones(request):
    """Lista de consolidaciones — vista para administración."""
    if request.user.rol not in ['administrador', 'jefe_barra']:
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')

    consolidaciones = Consolidacion.objects.select_related(
        'sesion__usuario', 'sesion__evento'
    ).order_by('-fecha_consolidacion')

    return render(request, 'ventas/lista_consolidaciones.html', {
        'consolidaciones': consolidaciones,
    })