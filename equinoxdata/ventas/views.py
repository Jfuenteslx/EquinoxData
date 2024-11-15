


# vistas.py

from django.db.models import F
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ventas.models import SesionDeTrabajo, Venta, Comanda, Cuenta
from . import models
from django.db.models import Sum
from .forms import ComandaForm, FiltroFechaForm
from .models import SesionDeTrabajo, Comanda, PresentacionProducto, Venta, Cuenta



from django import forms






@login_required
def iniciar_sesion(request):
    if SesionDeTrabajo.objects.filter(usuario_encargado=request.user, estado='abierta').exists():
        return redirect('ventas:error')  # Redirige a la URL 'error' si ya hay una sesión activa
    
    sesion = SesionDeTrabajo.objects.create(
        usuario_encargado=request.user,
        fecha_inicio=timezone.now(),
        estado='abierta'
    )
    return redirect('ventas:sesiones_activas')



@login_required
def sesiones_activas(request):
    # Mostrar tanto las sesiones abiertas como las cerradas
    sesiones = SesionDeTrabajo.objects.all()  # Obtenemos todas las sesiones (activas y cerradas)
    
    return render(request, 'ventas/sesiones_activas.html', {'sesiones': sesiones})


def cerrar_sesion(request, sesion_id):
    # Obtener la sesión de trabajo
    sesion = get_object_or_404(SesionDeTrabajo, id=sesion_id)
    
    # Verificar si la sesión está abierta
    if sesion.estado != 'abierta':
        return redirect('sesiones_activas')  # Redirigir si la sesión ya está cerrada
    
    # Calcular el total de ventas
    total_ventas = Venta.objects.filter(sesion_de_trabajo=sesion).aggregate(Sum('total'))['total__sum'] or 0
    
        # Actualizar la sesión con el total de ventas y la fecha de fin
    sesion.total_ventas = total_ventas
    sesion.estado = 'cerrada'
    sesion.fecha_fin = timezone.now()  # Registrar la fecha y hora de cierre
    sesion.save()  # Guardar los cambios

    return redirect('ventas:sesiones_activas')




@login_required
def detalle_sesion(request, sesion_id):
    sesion = get_object_or_404(SesionDeTrabajo, id=sesion_id)
    
    # Obtener las comandas de esa sesión
    comandas = Comanda.objects.filter(sesion_de_trabajo=sesion)

    # Calcula el total de ventas
    total_ventas = comandas.aggregate(total_sum=Sum('total'))['total_sum'] or 0
    
    # Pasar al contexto
    return render(request, 'ventas/detalle_sesion.html', {
        'sesion': sesion,
        'comandas': comandas,
        'total_ventas': total_ventas
    })

def error_view(request):
    return render(request, 'ventas/error.html', {'error': 'Ya tienes una sesión activa.'})  

# ---------------------------------------------------------------------------------------------------
# Vistas de Comandas
# ---------------------------------------------------------------------------------------------------


@login_required
def registrar_venta(request):
    # Buscar la sesión activa
    sesion_activa = SesionDeTrabajo.objects.filter(usuario_encargado=request.user, estado='abierta').first()

    if not sesion_activa:
        return redirect('ventas:sesiones_activas')  # Si no hay sesión activa, redirigir

    if request.method == 'POST':
        form = ComandaForm(request.POST)
        if form.is_valid():
            comanda = form.save(commit=False)
            comanda.sesion_de_trabajo = sesion_activa
            comanda.usuario = request.user  # Asignar el usuario que está registrando la venta

            # Calcular el total basado en la presentación seleccionada y la cantidad
            producto = comanda.producto
            cantidad = comanda.cantidad
            comanda.total = producto.precio * cantidad  # Calculamos el total

            comanda.save()
            return redirect('ventas:registrar_venta')  # Redirigir a la misma página para registrar más ventas
    else:
        form = ComandaForm()

    # Obtener el total acumulado de ventas de la sesión activa
    total_acumulado = sesion_activa.comandas.aggregate(total_sum=Sum('total'))['total_sum'] or 0
    
    # Obtener el resumen de todas las ventas de la sesión activa
    ventas_resumen = sesion_activa.comandas.all()

    # Obtener todos los productos disponibles
    productos = PresentacionProducto.objects.all()

    return render(request, 'ventas/registrar_venta.html', {
        'form': form,
        'sesion_activa': sesion_activa,
        'total_acumulado': total_acumulado,
        'ventas_resumen': ventas_resumen,
        'productos': productos,
    })
    
    # vista para el ordenamiento de la tabla
    

def listar_sesiones(request):
    sort = request.GET.get('sort', 'fecha_inicio')  # Default sort by fecha_inicio
    if sort.startswith('-'):
        order = sort
    else:
        order = F(sort).asc(nulls_last=True)  # Handle null values last in ascending

    sesiones = Sesion.objects.all().order_by(order)
    sesion_activa = Sesion.objects.filter(usuario_encargado=request.user, estado='abierta').first()

    return render(request, 'sesiones_activas.html', {
        'sesiones': sesiones,
        'sesion_activa': sesion_activa,
    })


# ------------------------------------------------------------------
# Vistas de ventas
# ------------------------------------------------------------------

# Formulario para el filtro de fecha
class FiltroFechaForm(forms.Form):
    fecha = forms.DateField(
        initial=timezone.now().date(), 
        widget=forms.DateInput(attrs={'type': 'date'}), 
        label="Fecha"
    )

def ventas_totales_del_dia(request):
    # Obtener la fecha actual (día de trabajo) o la fecha proporcionada por el usuario
    if request.method == 'GET' and 'fecha' in request.GET:
        fecha_filtro = request.GET['fecha']
        fecha_filtro = timezone.datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
    else:
        fecha_filtro = timezone.now().date()

    # Filtrar las sesiones cerradas para la fecha seleccionada
    sesiones_cerradas = SesionDeTrabajo.objects.filter(
        estado='cerrada', 
        fecha_inicio__date=fecha_filtro  # Asegurarse de que las sesiones son de la fecha seleccionada
    )

    # Obtener todas las comandas relacionadas con las sesiones cerradas
    comandas = Comanda.objects.filter(
        sesion_de_trabajo__in=sesiones_cerradas
    )
    
    # Obtener el total vendido de cada producto en las comandas, incluyendo la fecha de la venta
    productos_totales = comandas.values('producto__nombre_presentacion', 'sesion_de_trabajo__fecha_inicio').annotate(
        total_vendido=Sum('cantidad')
    ).order_by('producto__nombre_presentacion')

    # Recuperar todos los productos disponibles para mostrar los que no tienen ventas
    productos_disponibles = PresentacionProducto.objects.all()
    
    # Crear un diccionario con el nombre del producto, la fecha y la cantidad total (inicialmente 0)
    resumen_ventas = {}
    for producto in productos_disponibles:
        resumen_ventas[producto.nombre_presentacion] = {
            'total_vendido': 0,
            'fecha_venta': None  # Inicializa la fecha como None
        }

    # Llenar el diccionario con las ventas y la fecha correspondiente
    for item in productos_totales:
        producto_nombre = item['producto__nombre_presentacion']
        fecha_venta = item['sesion_de_trabajo__fecha_inicio']
        total_vendido = item['total_vendido']

        # Si el producto ya tiene ventas, acumulamos
        if producto_nombre in resumen_ventas:
            resumen_ventas[producto_nombre]['total_vendido'] += total_vendido
            # Si la fecha de la venta es más reciente, actualizamos
            if resumen_ventas[producto_nombre]['fecha_venta'] is None or fecha_venta > resumen_ventas[producto_nombre]['fecha_venta']:
                resumen_ventas[producto_nombre]['fecha_venta'] = fecha_venta

    # Solo guardar los registros si se recibe un POST con la acción de guardar
    if request.method == 'POST' and 'guardar_ventas' in request.POST:
        # Guardar los registros de ventas totales en la base de datos (utilizando el modelo Venta)
        for producto_nombre, datos in resumen_ventas.items():
            if datos['total_vendido'] > 0:  # Solo guardamos si se vendió algo
                producto = PresentacionProducto.objects.get(nombre_presentacion=producto_nombre)
                # Calcular el total de la venta (precio * cantidad vendida)
                total_venta = producto.precio * datos['total_vendido']
                # Registrar la venta total en la base de datos
                Venta.objects.create(
                    presentacion_producto=producto,
                    fecha=fecha_filtro,
                    cantidad_total=datos['total_vendido'],
                    total=total_venta  # Agregar el total calculado
                )

    # Crear el formulario de fecha para que el usuario lo pueda seleccionar
    filtro_fecha_form = FiltroFechaForm(initial={'fecha': fecha_filtro})

    return render(request, 'ventas/ventas_totales_del_dia.html', {
        'resumen_ventas': resumen_ventas,
        'filtro_fecha_form': filtro_fecha_form,
        'fecha_filtro': fecha_filtro
    })
    
    # ------------------------------------------------------------------
    # Vistas de cuentas (consolidacion a json)
    # ------------------------------------------------------------------
    
    
    from django.shortcuts import render, redirect

def revisar_cuentas(request):
    # Obtener todas las cuentas ya consolidadas
    cuentas = Cuenta.objects.all().order_by('fecha')

    return render(request, 'ventas/revisar_cuentas.html', {
        'cuentas': cuentas,
    })

def consolidar_cuenta(request, fecha):
    # Consolidar la cuenta para una fecha específica
    if request.method == 'POST':
        # Verificar si ya existe una cuenta para esa fecha
        cuenta, created = Cuenta.objects.get_or_create(fecha=fecha)
        
        if created:
            cuenta.consolidar_ventas()  # Consolidamos las ventas de la fecha
            cuenta.save()  # Guardamos la cuenta consolidada
            return redirect('ventas:revisar_cuentas')  # Redirigimos al listado de cuentas

    return redirect('ventas:revisar_cuentas')
