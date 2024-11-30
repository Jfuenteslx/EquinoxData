




from django.utils.dateparse import parse_datetime

from datetime import datetime, date






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
from django.contrib import messages

from datetime import date



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
        return redirect('ventas:sesiones_activas')  # Redirigir si la sesión ya está cerrada
    
    # Calcular el total de ventas sumando los totales de las comandas
    total_ventas = Comanda.objects.filter(sesion_de_trabajo=sesion).aggregate(Sum('total'))['total__sum'] or 0
    
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

            # Depuración: Mostrar el total de ventas antes de la actualización
            print(f"Total ventas antes de actualizar: {sesion_activa.total_ventas}")

            # Actualizar el total de ventas de la sesión después de guardar la comanda
            sesion_activa.calcular_total_ventas()

            # Depuración: Mostrar el total de ventas después de la actualización
            print(f"Total ventas después de actualizar: {sesion_activa.total_ventas}")

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







from decimal import Decimal
from datetime import date
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_date
from .models import Comanda, Cuenta, Venta, SesionDeTrabajo
from inventarios.models import Inventario

def ventas_totales_del_dia(request):
    # Obtener la fecha del filtro desde los parámetros de la URL
    fecha_str = request.GET.get('fecha', '')

    if not fecha_str:
        fecha_filtro = date.today()
    else:
        fecha_filtro = parse_date(fecha_str)
        if not fecha_filtro:
            fecha_filtro = date.today()

    # Filtrar las ventas de la fecha seleccionada
    ventas_del_dia = Comanda.objects.filter(sesion_de_trabajo__fecha_inicio__date=fecha_filtro)

    # Resumen de ventas: Agrupar por producto y calcular la cantidad total vendida
    resumen_ventas = {}
    for venta in ventas_del_dia:
        producto_nombre = venta.producto.nombre
        if producto_nombre not in resumen_ventas:
            # Inicializa el resumen de ventas para este producto
            resumen_ventas[producto_nombre] = {
                'total_vendido': 0,
                'producto_id': venta.producto.id,
                'total': Decimal('0.00'),  # Usa Decimal en lugar de float
                'producto_objeto': venta.producto,
            }

        resumen_ventas[producto_nombre]['total_vendido'] += venta.cantidad
        resumen_ventas[producto_nombre]['total'] += Decimal(venta.cantidad * venta.producto.precio)

    # Si el formulario se envía (Consolidar Ventas)
    if request.method == 'POST' and 'consolidar_ventas' in request.POST:
        # Consolidar las ventas para la fecha seleccionada
        cuenta, created = Cuenta.objects.get_or_create(fecha=fecha_filtro)

        # Obtener o crear una sesión de trabajo para esa fecha
        sesion = SesionDeTrabajo.objects.filter(fecha_inicio__date=fecha_filtro).first()
        if not sesion:
            sesion = SesionDeTrabajo.objects.create(
                fecha_inicio=fecha_filtro,
                estado="Abierta",
                usuario_encargado=request.user,
            )

        # Registrar cada venta en la tabla Venta
        for producto_nombre, datos in resumen_ventas.items():
            if datos['total_vendido'] > 0:
                # Verificar si ya existe una venta registrada para este producto en la fecha y sesión
                existing_venta = Venta.objects.filter(
                    presentacion_producto=datos['producto_objeto'],
                    fecha=fecha_filtro,
                    sesion_de_trabajo=sesion
                ).first()

                if existing_venta:
                    # Si existe, actualizar la venta existente
                    existing_venta.cantidad_total += datos['total_vendido']
                    existing_venta.total += datos['total']
                    existing_venta.save()
                else:
                    # Si no existe, crear una nueva venta
                    Venta.objects.create(
                        presentacion_producto=datos['producto_objeto'],
                        fecha=fecha_filtro,
                        cantidad_total=datos['total_vendido'],
                        total=datos['total'],
                        sesion_de_trabajo=sesion,
                    )

                # Actualizar el inventario después de la venta
                producto_base = datos['producto_objeto'].receta.first().insumo  # Obtiene el insumo relacionado (ProductoBase)
                inventario_producto = Inventario.objects.filter(producto=producto_base).first()

                if inventario_producto:
                    # Restamos del campo medidas_restantes
                    inventario_producto.medidas_restantes -= datos['total_vendido']

                    # Si medidas_restantes llega a 0 o es negativo, descontamos de saldo_bodega
                    if inventario_producto.medidas_restantes <= 0:
                        inventario_producto.saldo_bodega -= 1
                        # Si medidas_restantes es negativo, calculamos el sobrante
                        sobrante = abs(inventario_producto.medidas_restantes)
                        # Reiniciamos medidas_restantes considerando el sobrante, si hay stock disponible
                        if inventario_producto.saldo_bodega > 0:
                            inventario_producto.medidas_restantes += sobrante
                        else:
                            inventario_producto.medidas_restantes = 0  # Sin stock restante

                    # Guardar los cambios
                    inventario_producto.save()
                else:
                    print(f"El inventario para el producto {producto_base} no existe.")

        # Guardar la cuenta consolidada
        cuenta.resumen_ventas = {
            producto_nombre: {
                'total_vendido': datos['total_vendido'],
                'total': str(datos['total']),  # Convertir Decimal a string si es necesario
            }
            for producto_nombre, datos in resumen_ventas.items()
        }
        cuenta.save()

        # Redirigir al listado de cuentas consolidadas
        return redirect('ventas:revisar_cuentas')

    # Pasar datos a la plantilla para renderizar
    return render(request, 'ventas/ventas_totales_del_dia.html', {
        'fecha_filtro': fecha_filtro,
        'resumen_ventas': resumen_ventas,
    })


    # ------------------------------------------------------------------
    # Vistas de cuentas (consolidacion a json)
    # ------------------------------------------------------------------
    
    


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
        else:
            messages.error(request, f"Ya existe una cuenta consolidada para la fecha {fecha}.")
        
        return redirect('ventas:revisar_cuentas')

    # En caso de GET o métodos no permitidos, redirigir al listado
    return redirect('ventas:revisar_cuentas')
