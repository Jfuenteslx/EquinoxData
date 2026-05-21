from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Inventario, AperturaDiaria, MovimientoInventario
from .forms import AperturaDiariaForm, AjusteInventarioForm
from productos.models import ProductoBase


@login_required
def inventario_list(request):
    if not request.user.tiene_acceso_inventarios():
        messages.error(request, 'No tiene permisos para acceder a esta seccion.')
        return redirect('usuarios:inicio')

    inventarios = Inventario.objects.select_related('producto').all().order_by('producto__nombre')

    # Calcular discrepancias con la ultima apertura
    hoy = timezone.now().date()
    for inv in inventarios:
        apertura = AperturaDiaria.objects.filter(
            producto=inv.producto,
            fecha=hoy
        ).first()
        inv.apertura_hoy = apertura
        if apertura:
            inv.disc_botellas = inv.botellas - apertura.botellas_contadas
            inv.disc_medidas = inv.medidas_sueltas - apertura.medidas_contadas
        else:
            inv.disc_botellas = None
            inv.disc_medidas = None

    return render(request, 'inventarios/inventario_list.html', {
        'inventarios': inventarios,
        'hoy': hoy,
    })


@login_required
def apertura_diaria(request):
    if not request.user.tiene_acceso_inventarios():
        messages.error(request, 'No tiene permisos para acceder a esta seccion.')
        return redirect('usuarios:inicio')

    hoy = timezone.now().date()
    productos = ProductoBase.objects.filter(habilitado=True).order_by('nombre')

    # Verificar si ya existe apertura hoy
    aperturas_hoy = AperturaDiaria.objects.filter(fecha=hoy)
    ya_apertura = aperturas_hoy.exists()

    # Preparar datos para mostrar apertura existente
    apertura_data = {}
    for ap in aperturas_hoy:
        apertura_data[ap.producto_id] = ap

    if request.method == 'POST':
        if ya_apertura:
            messages.warning(request, 'Ya existe una apertura registrada para hoy.')
            return redirect('inventarios:inventario_list')

        form = AperturaDiariaForm(request.POST, productos=productos)
        if form.is_valid():
            for producto in productos:
                botellas = form.cleaned_data.get(f'botellas_{producto.id}') or 0
                medidas = form.cleaned_data.get(f'medidas_{producto.id}') or 0

                AperturaDiaria.objects.create(
                    fecha=hoy,
                    producto=producto,
                    botellas_contadas=botellas,
                    medidas_contadas=medidas,
                    registrado_por=request.user
                )

                MovimientoInventario.objects.create(
                    tipo='apertura',
                    producto=producto,
                    botellas=botellas,
                    medidas=medidas,
                    referencia=f'Apertura diaria {hoy}',
                    registrado_por=request.user
                )

            messages.success(request, f'Apertura del {hoy} registrada correctamente.')
            return redirect('inventarios:inventario_list')
    else:
        form = AperturaDiariaForm(productos=productos)

    # Preparar filas para el template
    filas = []
    for producto in productos:
        inventario = Inventario.objects.filter(producto=producto).first()
        filas.append({
            'producto': producto,
            'inventario': inventario,
            'campo_botellas': form[f'botellas_{producto.id}'],
            'campo_medidas': form[f'medidas_{producto.id}'],
        })

    return render(request, 'inventarios/apertura_diaria.html', {
        'form': form,
        'filas': filas,
        'hoy': hoy,
        'ya_apertura': ya_apertura,
        'apertura_data': apertura_data,
    })


@login_required
def ajustar_inventario(request, producto_id):
    if not request.user.es_administrador():
        messages.error(request, 'Solo el administrador puede realizar ajustes de inventario.')
        return redirect('usuarios:inicio')

    producto = get_object_or_404(ProductoBase, id=producto_id)
    inventario, _ = Inventario.objects.get_or_create(producto=producto)

    if request.method == 'POST':
        form = AjusteInventarioForm(request.POST, instance=inventario)
        if form.is_valid():
            botellas_ant = inventario.botellas
            medidas_ant = inventario.medidas_sueltas
            inventario = form.save()

            MovimientoInventario.objects.create(
                tipo='ajuste',
                producto=producto,
                botellas=inventario.botellas - botellas_ant,
                medidas=inventario.medidas_sueltas - medidas_ant,
                referencia=f'Ajuste manual por {request.user.username}',
                registrado_por=request.user
            )

            messages.success(request, f'Inventario de {producto.nombre} ajustado correctamente.')
            return redirect('inventarios:inventario_list')
    else:
        form = AjusteInventarioForm(instance=inventario)

    return render(request, 'inventarios/ajustar_inventario.html', {
        'form': form,
        'producto': producto,
        'inventario': inventario,
    })


@login_required
def historial_movimientos(request, producto_id=None):
    if not request.user.tiene_acceso_inventarios():
        messages.error(request, 'No tiene permisos para acceder a esta seccion.')
        return redirect('usuarios:inicio')

    if producto_id:
        producto = get_object_or_404(ProductoBase, id=producto_id)
        movimientos = MovimientoInventario.objects.filter(
            producto=producto
        ).select_related('producto', 'registrado_por').order_by('-fecha')
    else:
        producto = None
        movimientos = MovimientoInventario.objects.select_related(
            'producto', 'registrado_por'
        ).order_by('-fecha')[:100]

    return render(request, 'inventarios/historial_movimientos.html', {
        'movimientos': movimientos,
        'producto': producto,
    })


@login_required
def registrar_saldos(request):
    return redirect('inventarios:apertura_diaria')