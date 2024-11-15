from django.shortcuts import render, get_object_or_404, redirect
from .forms import InventarioForm, RegistrarStockForm # Asegúrate de tener un formulario para crear o agregar inventarios
from .models import Inventario  # Asegúrate de que el modelo Inventario esté correctamente importado

def listar_inventarios(request):
    inventarios = Inventario.objects.all()
    return render(request, 'inventarios/listar_inventarios.html', {'inventarios': inventarios})


def agregar_inventario(request):
    if request.method == 'POST':
        form = InventarioForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda el nuevo inventario
            return redirect('inventarios:listar_inventarios')  # Redirige a la lista de inventarios
    else:
        form = InventarioForm()
    return render(request, 'inventarios/agregar_inventario.html', {'form': form})


def actualizar_inventario(request, inventario_id):
    inventario = get_object_or_404(Inventario, id=inventario_id)
    if request.method == 'POST':
        form = InventarioForm(request.POST, instance=inventario)
        if form.is_valid():
            form.save()  # Actualiza el inventario
            return redirect('listar_inventarios')  # Redirige después de actualizar
    else:
        form = InventarioForm(instance=inventario)  # Carga el formulario con los datos existentes

    return render(request, 'inventarios/actualizar_inventario.html', {'form': form, 'inventario': inventario})

def eliminar_inventario(request, inventario_id):
    inventario = get_object_or_404(Inventario, id=inventario_id)
    inventario.delete()  # Elimina el inventario
    return redirect('listar_inventarios')  # Redirige a la lista de inventarios

def registrar_stock(request):
    if request.method == 'POST':
        form = RegistrarStockForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda el nuevo stock en la base de datos
            return redirect('listar_inventarios')  # Redirige a la lista de inventarios
    else:
        form = RegistrarStockForm()
    return render(request, 'inventarios/registrar_stock.html', {'form': form})