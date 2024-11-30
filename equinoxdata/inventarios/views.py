
from django.shortcuts import render
from .models import Inventario
from ventas.models import Venta
from ventas.models import Venta


# inventarios/views.py
from django.db.models import Sum

from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from compras.models import Compra
from productos.models import ProductoBase
from inventarios.models import Inventario, inicializar_inventarios_con_compras
from inventarios.models import Inventario



from .models import Inventario
from django.http import JsonResponse


# vista que solo se utiliza si se inicializan inventarios
# --------------------------------------------------------------------------------------------------

from django.shortcuts import render, redirect
from django.contrib import messages
from inventarios.models import Inventario
from compras.models import Compra
from productos.models import ProductoBase

def inicializar_inventarios(request):
    """
    Verifica si existen inventarios. Si no existen, pregunta al usuario si desea importar las compras
    para inicializar el inventario. Si el usuario acepta, se crea el inventario inicial.
    """
    # Verificar si ya existen inventarios
    if Inventario.objects.exists():
        messages.info(request, "Los inventarios ya han sido inicializados.")
        return redirect('inventarios:inventario_list')  # Redirigir al listado de inventarios

    if request.method == 'POST':
        # Si el usuario decide inicializar inventarios con las compras
        inicializar_inventarios_con_compras()
        messages.success(request, "Inventarios inicializados con las compras exitosamente.")
        return redirect('inventarios:inventario_list')  # Redirigir al listado de inventarios

    # Si no existen inventarios y la solicitud es GET, mostramos la opción para importar
    return render(request, 'inventarios/inicializar_inventarios.html')

def inicializar_inventarios_con_compras():
    """
    Inicializa los inventarios utilizando los registros de compras.
    """
    # Obtener todos los productos base registrados en compras
    productos_comprados = Compra.objects.values_list('producto', flat=True).distinct()

    for producto_id in productos_comprados:
        # Obtener el producto base
        producto = ProductoBase.objects.get(id=producto_id)

        # Calcular la cantidad total comprada para este producto
        total_comprado = Compra.objects.filter(producto=producto).aggregate(
            total=Sum('cantidad')
        )['total'] or 0

        # Crear el inventario inicial con los datos calculados
        Inventario.objects.create(
            producto=producto,
            saldo_bodega=total_comprado,  # Saldo inicial basado en compras
            medidas_restantes=0  # O cualquier valor inicial que sea adecuado
        )



# vistas de inventarios
# --------------------------------------------------------------------------------------------------

# inventarios/views.py





def inventario_list(request):
    inventarios = Inventario.objects.all()
    for inventario in inventarios:
        inventario.calcular_stock_final()  # Asegúrate de que el método esté definido en el modelo
    return render(request, 'inventarios/inventario_list.html', {'inventarios': inventarios})





from django.shortcuts import get_object_or_404
from ventas.models import Venta
from compras.models import Compra
from productos.models import PresentacionProducto
from .models import Inventario

def inventario_historial(request, id):
    # Obtén el inventario correspondiente al ID
    inventario = get_object_or_404(Inventario, id=id)
    
    # Obtén las compras relacionadas con el producto del inventario
    compras = Compra.objects.filter(producto=inventario.producto)
    
    # Filtra las ventas relacionadas con las presentaciones del producto
    ventas = Venta.objects.filter(presentacion_producto__nombre=inventario.producto.nombre)
    
    return render(request, 'inventarios/inventario_historial.html', {
        'inventario': inventario,
        'compras': compras,
        'ventas': ventas,
    })




def actualizar_inventario(request, producto_id, cantidad, tipo):
    """
    Actualiza el inventario de un producto según el tipo (entrada o salida).
    """
    inventario = get_object_or_404(Inventario, producto_id=producto_id)
    try:
        inventario.actualizar_inventario(cantidad, tipo)
        return JsonResponse({'status': 'success', 'stock_final': inventario.stock_final})
    except ValueError as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def productos_bajo_stock(request):
    """
    Muestra una lista de productos cuyo inventario está por debajo de un nivel crítico.
    """
    nivel_critico = 10  # Umbral definido
    productos_bajo_stock = Inventario.objects.filter(stock_final__lt=nivel_critico)
    return render(request, 'inventarios/productos_bajo_stock.html', {'productos': productos_bajo_stock})

def detalle_producto(request, producto_id):
    """
    Muestra los movimientos de inventario para un producto específico.
    """
    producto = ProductoBase.objects.get(id=producto_id)
    inventario = Inventario.objects.get(producto=producto)
    compras = Compra.objects.filter(producto=producto)
    ventas = inventario.ventas()  # Si has implementado un método para obtener ventas relacionadas
    return render(request, 'inventarios/detalle_producto.html', {
        'producto': producto,
        'inventario': inventario,
        'compras': compras,
        'ventas': ventas,
    })



# vistas de saldos
# --------------------------------------------------------------------------------------------------

from django.shortcuts import render, redirect
from .models import Saldo
from .forms import SaldoForm
from django.http import HttpResponse

# Vista para listar los saldos
def saldo_list(request):
    saldos = Saldo.objects.all()
    return render(request, 'inventarios/saldo_list.html', {'saldos': saldos})

# Vista para crear un nuevo saldo
def saldo_create(request):
    if request.method == 'POST':
        form = SaldoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventarios:saldo_list')  # Redirigir a la lista de saldos
    else:
        form = SaldoForm()
    return render(request, 'inventarios/saldo_form.html', {'form': form})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Saldo
from .forms import SaldoForm

# Vista para editar un saldo existente
def saldo_edit(request, id):
    saldo = get_object_or_404(Saldo, id=id)  # Obtener el saldo a editar
    if request.method == 'POST':
        form = SaldoForm(request.POST, instance=saldo)  # Rellenamos el formulario con el saldo actual
        if form.is_valid():
            form.save()  # Guardamos el saldo actualizado
            return redirect('inventarios:saldo_list')  # Redirigimos a la lista de saldos
    else:
        form = SaldoForm(instance=saldo)  # Si es GET, mostramos el formulario con los datos actuales

    return render(request, 'inventarios/saldo_form.html', {'form': form})

from django.shortcuts import get_object_or_404, redirect
from .models import Saldo

# Vista para eliminar un saldo
def saldo_delete(request, id):
    saldo = get_object_or_404(Saldo, id=id)  # Obtener el saldo a eliminar
    saldo.delete()  # Eliminamos el saldo
    return redirect('inventarios:saldo_list')  # Redirigimos a la lista de saldos


# Vista para confirmar la eliminación de un saldo
def saldo_confirm_delete(request, id):
    saldo = get_object_or_404(Saldo, id=id)  # Obtener el saldo a eliminar

    if request.method == 'POST':
        saldo.delete()  # Eliminar el saldo
        return redirect('inventarios:saldo_list')  # Redirigir al listado de saldos

    return render(request, 'inventarios/saldo_confirm_delete.html', {'saldo': saldo})

# consolidar inventarios
# --------------------------------------------------------------------------------------------------

from django.shortcuts import render, redirect
from .models import RegistroStock
from inventarios.models import Inventario

def consolidar_inventario(request):
    # Obtener los datos del inventario y generar el JSON
    inventarios = Inventario.objects.all()
    inventario_data = {
        inventario.producto.nombre: {
            "saldo_bodega": inventario.saldo_bodega,
        }
        for inventario in inventarios
    }

    if request.method == 'POST':
        # Guardar los datos en el modelo RegistroStock
        registro = RegistroStock.objects.create(inventario_json=inventario_data)
        return redirect('inventarios:consolidar_inventario')  # Redirigir después del guardado

    # Renderizar la previsualización
    return render(request, 'inventarios/consolidar_inventario.html', {
        'inventario_data': inventario_data,
    })
