from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date

from productos.models import ProductoMenu
from .forms import ComandaForm
from .models import SesionDeTrabajo, Comanda, Consolidacion


# ------------------------------------------------------------------
# Sesiones de trabajo
# ------------------------------------------------------------------

@login_required
def iniciar_sesion(request):
    if SesionDeTrabajo.objects.filter(usuario_encargado=request.user, estado='abierta').exists():
        messages.warning(request, 'Ya tiene una sesion de trabajo activa.')
        return redirect('ventas:sesiones_activas')

    SesionDeTrabajo.objects.create(
        usuario_encargado=request.user,
        estado='abierta'
    )
    messages.success(request, 'Sesion de trabajo iniciada correctamente.')
    return redirect('ventas:sesiones_activas')


@login_required
def sesiones_activas(request):
    if request.user.tiene_acceso_compras():
        sesiones = SesionDeTrabajo.objects.all().order_by('-fecha_inicio')
    else:
        sesiones = SesionDeTrabajo.objects.filter(
            usuario_encargado=request.user
        ).order_by('-fecha_inicio')

    return render(request, 'ventas/sesiones_activas.html', {'sesiones': sesiones})


@login_required
def cerrar_sesion(request, sesion_id):
    sesion = get_object_or_404(SesionDeTrabajo, id=sesion_id)

    if sesion.usuario_encargado != request.user and not request.user.es_administrador():
        messages.error(request, 'No tiene permisos para cerrar esta sesion.')
        return redirect('ventas:sesiones_activas')

    if sesion.estado != 'abierta':
        messages.warning(request, 'Esta sesion ya esta cerrada.')
        return redirect('ventas:sesiones_activas')

    sesion.cerrar()
    messages.success(request, 'Sesion de trabajo cerrada correctamente.')
    return redirect('ventas:sesiones_activas')


@login_required
def detalle_sesion(request, sesion_id):
    sesion = get_object_or_404(SesionDeTrabajo, id=sesion_id)
    comandas = Comanda.objects.filter(sesion_de_trabajo=sesion)
    total_ventas = comandas.aggregate(total_sum=Sum('total'))['total_sum'] or 0
    return render(request, 'ventas/detalle_sesion.html', {
        'sesion': sesion,
        'comandas': comandas,
        'total_ventas': total_ventas,
    })


@login_required
def error_view(request):
    return render(request, 'ventas/error.html', {
        'error': 'Ya tiene una sesion activa.'
    })


# ------------------------------------------------------------------
# Comandas
# ------------------------------------------------------------------

@login_required
def registrar_venta(request):
    sesion_activa = SesionDeTrabajo.objects.filter(
        usuario_encargado=request.user,
        estado='abierta'
    ).first()

    if not sesion_activa:
        messages.warning(request, 'No tiene una sesion de trabajo activa. Inicie una primero.')
        return redirect('ventas:sesiones_activas')

    if request.method == 'POST':
        form = ComandaForm(request.POST)
        if form.is_valid():
            comanda = form.save(commit=False)
            comanda.sesion_de_trabajo = sesion_activa
            comanda.usuario = request.user
            comanda.save()
            messages.success(request, f'Comanda registrada: {comanda.cantidad} x {comanda.producto.nombre}.')
            return redirect('ventas:registrar_venta')
        else:
            messages.error(request, 'Error al registrar la comanda. Revise los datos.')
    else:
        form = ComandaForm()

    total_acumulado = sesion_activa.comandas.aggregate(
        total_sum=Sum('total')
    )['total_sum'] or 0
    ventas_resumen = sesion_activa.comandas.select_related('producto').all()
    productos = ProductoMenu.objects.filter(habilitado=True)

    return render(request, 'ventas/registrar_venta.html', {
        'form': form,
        'sesion_activa': sesion_activa,
        'total_acumulado': total_acumulado,
        'ventas_resumen': ventas_resumen,
        'productos': productos,
    })


# ------------------------------------------------------------------
# Consolidacion de ventas
# ------------------------------------------------------------------

@login_required
def ventas_totales_del_dia(request):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene permisos para acceder a esta seccion.')
        return redirect('usuarios:inicio')

    fecha_str = request.GET.get('fecha', '')
    fecha_filtro = parse_date(fecha_str) if fecha_str else date.today()
    if not fecha_filtro:
        fecha_filtro = date.today()

    comandas_del_dia = Comanda.objects.filter(
        sesion_de_trabajo__fecha_inicio__date=fecha_filtro
    ).select_related('producto')

    resumen_ventas = {}
    for comanda in comandas_del_dia:
        nombre = comanda.producto.nombre
        if nombre not in resumen_ventas:
            resumen_ventas[nombre] = {
                'total_vendido': 0,
                'producto_id': comanda.producto.id,
                'tipo': comanda.producto.tipo,
                'total': Decimal('0.00'),
                'producto_objeto': comanda.producto,
            }
        resumen_ventas[nombre]['total_vendido'] += comanda.cantidad
        resumen_ventas[nombre]['total'] += comanda.total

    if request.method == 'POST' and 'consolidar_ventas' in request.POST:
        sesion_id = request.POST.get('sesion_id')
        sesion = get_object_or_404(SesionDeTrabajo, id=sesion_id)

        consolidacion, created = Consolidacion.objects.get_or_create(
            sesion=sesion,
            defaults={
                'fecha': fecha_filtro,
                'consolidado_por': request.user,
            }
        )
        consolidacion.generar_resumen()

        messages.success(request, f'Ventas del {fecha_filtro} consolidadas correctamente.')
        return redirect('ventas:revisar_consolidaciones')

    sesiones_del_dia = SesionDeTrabajo.objects.filter(
        fecha_inicio__date=fecha_filtro
    )

    return render(request, 'ventas/ventas_totales_del_dia.html', {
        'fecha_filtro': fecha_filtro,
        'resumen_ventas': resumen_ventas,
        'sesiones_del_dia': sesiones_del_dia,
    })


@login_required
def revisar_consolidaciones(request):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene permisos para acceder a esta seccion.')
        return redirect('usuarios:inicio')

    consolidaciones = Consolidacion.objects.select_related(
        'sesion', 'consolidado_por'
    ).all()

    return render(request, 'ventas/revisar_consolidaciones.html', {
        'consolidaciones': consolidaciones
    })