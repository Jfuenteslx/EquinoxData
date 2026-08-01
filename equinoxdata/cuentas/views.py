from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal

from .models import (
    CierreDiario, OtroIngreso, MovimientoCajaChica, EgresoGrande,
    SueldoNoche, EntregaPuntoVenta, CierreBancario, ResumenSemanal,
    GastoFijo
)
from usuarios.models import Usuario


def solo_admin_jefe(user):
    return user.rol in ['administrador', 'jefe_barra']


# ------------------------------------------------------------------ #
# CIERRES DIARIOS                                                      #
# ------------------------------------------------------------------ #

@login_required
def lista_cierres(request):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')
    cierres = CierreDiario.objects.all().order_by('-fecha')
    return render(request, 'cuentas/lista_cierres.html', {'cierres': cierres})


@login_required
def crear_cierre(request):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('usuarios:inicio')

    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        evento_id = request.POST.get('evento') or None
        caja_inicial = request.POST.get('caja_inicial', 0) or 0
        observaciones = request.POST.get('observaciones', '')

        if CierreDiario.objects.filter(fecha=fecha).exists():
            messages.error(request, f'Ya existe un cierre para la fecha {fecha}.')
            return redirect('cuentas:crear_cierre')

        evento = None
        if evento_id:
            from eventos.models import Evento
            evento = get_object_or_404(Evento, pk=evento_id)

        cierre = CierreDiario.objects.create(
            fecha=fecha,
            evento=evento,
            caja_inicial=caja_inicial,
            observaciones=observaciones,
        )
        messages.success(request, f'Cierre del {fecha} creado correctamente.')
        return redirect('cuentas:detalle_cierre', pk=cierre.pk)

    from eventos.models import Evento
    eventos = Evento.objects.all().order_by('-fecha')
    return render(request, 'cuentas/crear_cierre.html', {'eventos': eventos})


@login_required
def detalle_cierre(request, pk):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')

    cierre = get_object_or_404(CierreDiario, pk=pk)
    usuarios_sistema = Usuario.objects.filter(rol__in=['mesero', 'bartender'])
    personal_sistema = Usuario.objects.filter(rol__in=['administrador', 'jefe_barra', 'bartender'])

    # Pedidos extraordinarios de esta noche
    try:
        from compras.models import Pedido
        pedidos_ext = Pedido.objects.filter(
            cierre_diario=cierre,
            tipo='extraordinario'
        ).prefetch_related('compras__detalles__producto', 'gastos_operativos')
    except Exception:
        pedidos_ext = []

    context = {
        'cierre': cierre,
        'otros_ingresos': cierre.otros_ingresos.all(),
        'movimientos_caja': cierre.movimientos_caja_chica.all().order_by('id'),
        'egresos_grandes': cierre.egresos_grandes.all(),
        'sueldos': cierre.sueldos.all(),
        'entregas': cierre.entregas_punto_venta.all(),
        'cierres_bancarios': cierre.cierres_bancarios.all(),
        'pedidos_ext': pedidos_ext,
        'usuarios_sistema': usuarios_sistema,
        'personal_sistema': personal_sistema,
    }
    return render(request, 'cuentas/detalle_cierre.html', context)


@login_required
def cerrar_cierre(request, pk):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('usuarios:inicio')

    cierre = get_object_or_404(CierreDiario, pk=pk)
    if request.method == 'POST':
        cierre.estado = 'cerrado'
        cierre.save()
        messages.success(request, f'Cierre del {cierre.fecha} cerrado correctamente.')
    return redirect('cuentas:detalle_cierre', pk=pk)


# ------------------------------------------------------------------ #
# OTROS INGRESOS                                                       #
# ------------------------------------------------------------------ #

@login_required
def agregar_otro_ingreso(request, cierre_pk):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos.')
        return redirect('usuarios:inicio')
    cierre = get_object_or_404(CierreDiario, pk=cierre_pk)
    if request.method == 'POST':
        OtroIngreso.objects.create(
            cierre=cierre,
            concepto=request.POST.get('concepto'),
            concepto_otro=request.POST.get('concepto_otro', ''),
            monto=request.POST.get('monto'),
        )
        messages.success(request, 'Ingreso agregado.')
    return redirect('cuentas:detalle_cierre', pk=cierre_pk)


@login_required
def eliminar_otro_ingreso(request, pk):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos.')
        return redirect('usuarios:inicio')
    ingreso = get_object_or_404(OtroIngreso, pk=pk)
    cierre_pk = ingreso.cierre.pk
    ingreso.delete()
    messages.success(request, 'Ingreso eliminado.')
    return redirect('cuentas:detalle_cierre', pk=cierre_pk)


# ------------------------------------------------------------------ #
# MOVIMIENTOS CAJA CHICA                                               #
# ------------------------------------------------------------------ #

@login_required
def agregar_movimiento_caja(request, cierre_pk):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos.')
        return redirect('usuarios:inicio')
    cierre = get_object_or_404(CierreDiario, pk=cierre_pk)
    if request.method == 'POST':
        MovimientoCajaChica.objects.create(
            cierre=cierre,
            tipo=request.POST.get('tipo', 'egreso'),
            concepto=request.POST.get('concepto'),
            monto=request.POST.get('monto'),
            registrado_por=request.user,
        )
        messages.success(request, 'Movimiento de caja chica registrado.')
    return redirect('cuentas:detalle_cierre', pk=cierre_pk)


@login_required
def eliminar_movimiento_caja(request, pk):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos.')
        return redirect('usuarios:inicio')
    mov = get_object_or_404(MovimientoCajaChica, pk=pk)
    cierre_pk = mov.cierre.pk
    mov.delete()
    messages.success(request, 'Movimiento eliminado.')
    return redirect('cuentas:detalle_cierre', pk=cierre_pk)


# ------------------------------------------------------------------ #
# EGRESOS GRANDES                                                      #
# ------------------------------------------------------------------ #

@login_required
def agregar_egreso_grande(request, cierre_pk):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos.')
        return redirect('usuarios:inicio')
    cierre = get_object_or_404(CierreDiario, pk=cierre_pk)
    if request.method == 'POST':
        EgresoGrande.objects.create(
            cierre=cierre,
            concepto=request.POST.get('concepto'),
            concepto_otro=request.POST.get('concepto_otro', ''),
            monto=request.POST.get('monto'),
            metodo_pago=request.POST.get('metodo_pago', 'efectivo'),
            observacion=request.POST.get('observacion', ''),
        )
        messages.success(request, 'Egreso agregado.')
    return redirect('cuentas:detalle_cierre', pk=cierre_pk)


@login_required
def eliminar_egreso_grande(request, pk):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos.')
        return redirect('usuarios:inicio')
    egreso = get_object_or_404(EgresoGrande, pk=pk)
    cierre_pk = egreso.cierre.pk
    egreso.delete()
    messages.success(request, 'Egreso eliminado.')
    return redirect('cuentas:detalle_cierre', pk=cierre_pk)


# ------------------------------------------------------------------ #
# SUELDOS                                                              #
# ------------------------------------------------------------------ #

@login_required
def agregar_sueldo(request, cierre_pk):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos.')
        return redirect('usuarios:inicio')
    cierre = get_object_or_404(CierreDiario, pk=cierre_pk)
    if request.method == 'POST':
        tipo_persona = request.POST.get('tipo_persona', 'sistema')
        tipo = request.POST.get('tipo')
        caja_mesero = request.POST.get('caja_mesero') or None
        porcentaje = request.POST.get('porcentaje') or None
        monto_fijo = request.POST.get('monto_fijo') or None
        descuento = request.POST.get('descuento') or 0
        observacion = request.POST.get('observacion', '')

        if tipo_persona == 'sistema':
            empleado_id = request.POST.get('empleado')
            empleado = get_object_or_404(Usuario, pk=empleado_id)
            sueldo, created = SueldoNoche.objects.get_or_create(
                cierre=cierre,
                empleado=empleado,
                defaults={
                    'tipo': tipo,
                    'caja_mesero': caja_mesero,
                    'porcentaje': porcentaje,
                    'monto_fijo': monto_fijo,
                    'descuento': descuento,
                    'observacion': observacion,
                }
            )
            if not created:
                sueldo.tipo = tipo
                sueldo.caja_mesero = caja_mesero
                sueldo.porcentaje = porcentaje
                sueldo.monto_fijo = monto_fijo
                sueldo.descuento = descuento
                sueldo.observacion = observacion
                sueldo.save()
            nombre = empleado.get_full_name() or empleado.username
        else:
            nombre_libre = request.POST.get('nombre_libre', '')
            puesto = request.POST.get('puesto', '')
            sueldo = SueldoNoche.objects.create(
                cierre=cierre,
                nombre_libre=nombre_libre,
                puesto=puesto,
                tipo=tipo,
                caja_mesero=caja_mesero,
                porcentaje=porcentaje,
                monto_fijo=monto_fijo,
                descuento=descuento,
                observacion=observacion,
            )
            nombre = nombre_libre

        messages.success(request, f'Sueldo de {nombre} registrado.')
    return redirect('cuentas:detalle_cierre', pk=cierre_pk)


@login_required
def eliminar_sueldo(request, pk):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos.')
        return redirect('usuarios:inicio')
    sueldo = get_object_or_404(SueldoNoche, pk=pk)
    cierre_pk = sueldo.cierre.pk
    sueldo.delete()
    messages.success(request, 'Sueldo eliminado.')
    return redirect('cuentas:detalle_cierre', pk=cierre_pk)


# ------------------------------------------------------------------ #
# ENTREGAS PUNTO DE VENTA                                              #
# ------------------------------------------------------------------ #

@login_required
def agregar_entrega(request, cierre_pk):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos.')
        return redirect('usuarios:inicio')
    cierre = get_object_or_404(CierreDiario, pk=cierre_pk)
    if request.method == 'POST':
        es_barra = request.POST.get('es_barra') == '1'
        usuario_id = request.POST.get('usuario') or None
        efectivo = request.POST.get('efectivo') or 0
        qr = request.POST.get('qr') or 0
        voucher_banco = request.POST.get('voucher_banco') or 0
        total_talonario = request.POST.get('total_talonario') or None
        observacion = request.POST.get('observacion', '')
        comprobante = request.FILES.get('comprobante')

        usuario = get_object_or_404(Usuario, pk=usuario_id) if usuario_id else None

        entrega, created = EntregaPuntoVenta.objects.get_or_create(
            cierre=cierre,
            usuario=usuario,
            es_barra=es_barra,
            defaults={
                'efectivo': efectivo,
                'qr': qr,
                'voucher_banco': voucher_banco,
                'total_talonario': total_talonario,
                'observacion': observacion,
            }
        )
        if not created:
            entrega.efectivo = efectivo
            entrega.qr = qr
            entrega.voucher_banco = voucher_banco
            entrega.total_talonario = total_talonario
            entrega.observacion = observacion
            if comprobante:
                entrega.comprobante = comprobante
            entrega.save()
            messages.success(request, 'Entrega actualizada.')
        else:
            if comprobante:
                entrega.comprobante = comprobante
                entrega.save()
            messages.success(request, 'Entrega registrada.')
    return redirect('cuentas:detalle_cierre', pk=cierre_pk)


@login_required
def editar_entrega(request, pk):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos.')
        return redirect('usuarios:inicio')
    entrega = get_object_or_404(EntregaPuntoVenta, pk=pk)
    cierre = entrega.cierre
    if request.method == 'POST':
        entrega.efectivo = request.POST.get('efectivo') or 0
        entrega.qr = request.POST.get('qr') or 0
        entrega.voucher_banco = request.POST.get('voucher_banco') or 0
        entrega.total_talonario = request.POST.get('total_talonario') or None
        entrega.observacion = request.POST.get('observacion', '')
        if request.FILES.get('comprobante'):
            entrega.comprobante = request.FILES.get('comprobante')
        entrega.save()
        messages.success(request, 'Entrega actualizada correctamente.')
        return redirect('cuentas:detalle_cierre', pk=cierre.pk)
    return render(request, 'cuentas/editar_entrega.html', {
        'entrega': entrega,
        'cierre': cierre,
    })


@login_required
def eliminar_entrega(request, pk):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos.')
        return redirect('usuarios:inicio')
    entrega = get_object_or_404(EntregaPuntoVenta, pk=pk)
    cierre_pk = entrega.cierre.pk
    entrega.delete()
    messages.success(request, 'Entrega eliminada.')
    return redirect('cuentas:detalle_cierre', pk=cierre_pk)


# ------------------------------------------------------------------ #
# CIERRES BANCARIOS                                                    #
# ------------------------------------------------------------------ #

@login_required
def agregar_cierre_bancario(request, cierre_pk):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos.')
        return redirect('usuarios:inicio')
    cierre = get_object_or_404(CierreDiario, pk=cierre_pk)
    if request.method == 'POST':
        CierreBancario.objects.create(
            cierre=cierre,
            cuenta=request.POST.get('cuenta'),
            lote=request.POST.get('lote'),
            monto=request.POST.get('monto'),
        )
        messages.success(request, 'Cierre bancario agregado.')
    return redirect('cuentas:detalle_cierre', pk=cierre_pk)


@login_required
def eliminar_cierre_bancario(request, pk):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos.')
        return redirect('usuarios:inicio')
    cierre_b = get_object_or_404(CierreBancario, pk=pk)
    cierre_pk = cierre_b.cierre.pk
    cierre_b.delete()
    messages.success(request, 'Cierre bancario eliminado.')
    return redirect('cuentas:detalle_cierre', pk=cierre_pk)


# ------------------------------------------------------------------ #
# GASTOS FIJOS                                                         #
# ------------------------------------------------------------------ #

@login_required
def lista_gastos_fijos(request):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')
    gastos = GastoFijo.objects.all().order_by('-fecha_pago')
    return render(request, 'cuentas/lista_gastos_fijos.html', {'gastos': gastos})


@login_required
def agregar_gasto_fijo(request):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos.')
        return redirect('usuarios:inicio')
    if request.method == 'POST':
        from datetime import date
        fecha_pago = request.POST.get('fecha_pago')
        fecha_obj = date.fromisoformat(fecha_pago)
        GastoFijo.objects.create(
            concepto=request.POST.get('concepto'),
            concepto_otro=request.POST.get('concepto_otro', ''),
            descripcion=request.POST.get('descripcion', ''),
            monto=request.POST.get('monto'),
            fecha_pago=fecha_pago,
            periodo_mes=fecha_obj.month,
            periodo_anio=fecha_obj.year,
            metodo_pago=request.POST.get('metodo_pago', 'transferencia'),
            registrado_por=request.user,
        )
        messages.success(request, 'Gasto fijo registrado.')
        return redirect('cuentas:lista_gastos_fijos')

    return render(request, 'cuentas/agregar_gasto_fijo.html', {
        'concepto_choices': GastoFijo.CONCEPTO_CHOICES,
        'metodo_choices': GastoFijo.METODO_PAGO_CHOICES,
    })


@login_required
def eliminar_gasto_fijo(request, pk):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos.')
        return redirect('usuarios:inicio')
    gasto = get_object_or_404(GastoFijo, pk=pk)
    gasto.delete()
    messages.success(request, 'Gasto fijo eliminado.')
    return redirect('cuentas:lista_gastos_fijos')


# ------------------------------------------------------------------ #
# RESUMEN SEMANAL                                                      #
# ------------------------------------------------------------------ #

@login_required
def lista_resumenes(request):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')
    resumenes = ResumenSemanal.objects.all().order_by('-fecha_inicio')
    return render(request, 'cuentas/lista_resumenes.html', {'resumenes': resumenes})


@login_required
def crear_resumen(request):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos.')
        return redirect('usuarios:inicio')
    if request.method == 'POST':
        resumen = ResumenSemanal.objects.create(
            fecha_inicio=request.POST.get('fecha_inicio'),
            fecha_fin=request.POST.get('fecha_fin'),
            nombre=request.POST.get('nombre', ''),
        )
        cierre_ids = request.POST.getlist('cierres')
        if cierre_ids:
            resumen.cierres.set(CierreDiario.objects.filter(pk__in=cierre_ids))
        messages.success(request, 'Resumen semanal creado.')
        return redirect('cuentas:detalle_resumen', pk=resumen.pk)
    cierres = CierreDiario.objects.filter(estado='cerrado').order_by('-fecha')
    return render(request, 'cuentas/crear_resumen.html', {'cierres': cierres})


@login_required
def detalle_resumen(request, pk):
    if not solo_admin_jefe(request.user):
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')
    resumen = get_object_or_404(ResumenSemanal, pk=pk)
    return render(request, 'cuentas/detalle_resumen.html', {
        'resumen': resumen,
        'totales': resumen.calcular_totales(),
        'cierres': resumen.cierres.all().order_by('fecha'),
    })