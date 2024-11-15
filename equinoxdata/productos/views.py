# productos/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from .models import ProductoBase, PresentacionProducto, Receta
from .forms import ProductoBaseForm, PresentacionProductoForm, RecetaForm


def listar_productos(request):
    productos = ProductoBase.objects.all()
    return render(request, 'productos/listar_productos.html', {'productos': productos})

def crear_producto(request):
    if request.method == 'POST':
        form = ProductoBaseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productos:listar_productos')  # Redirige a la lista de productos
    else:
        form = ProductoBaseForm()
    return render(request, 'productos/crear_producto.html', {'form': form})


def editar_producto(request, pk):
    producto = get_object_or_404(ProductoBase, pk=pk)
    if request.method == 'POST':
        form = ProductoBaseForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('productos:listar_productos')  # Redirige a la lista de productos
    else:
        form = ProductoBaseForm(instance=producto)
    return render(request, 'productos/editar_producto.html', {'form': form, 'producto': producto})

def eliminar_producto(request, pk):
    producto = get_object_or_404(ProductoBase, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('productos:listar_productos')  # Redirige a la lista de productos
    return render(request, 'productos/eliminar_producto.html', {'producto': producto})

# menu interno debo implementarlo para entrar despues

def productos_view(request):
    return render(request, 'productos/productos.html')
    return HttpResponseForbidden("Método no permitido.")

# modelo PresentacionProducto

# Vista para listar todas las presentaciones de productos
def listar_presentaciones(request):
    presentaciones = PresentacionProducto.objects.all()
    return render(request, 'productos/listar_presentaciones.html', {'presentaciones': presentaciones})

# Vista para crear una nueva presentación de producto
def crear_presentacion(request):
    if request.method == 'POST':
        form = PresentacionProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productos:listar_presentaciones')
    else:
        form = PresentacionProductoForm()
    return render(request, 'productos/crear_presentacion.html', {'form': form})

# Vista para editar una presentación de producto
def editar_presentacion(request, pk):
    presentacion = get_object_or_404(PresentacionProducto, pk=pk)
    if request.method == 'POST':
        form = PresentacionProductoForm(request.POST, instance=presentacion)
        if form.is_valid():
            form.save()
            return redirect('productos:listar_presentaciones')
    else:
        form = PresentacionProductoForm(instance=presentacion)
    return render(request, 'productos/editar_presentacion.html', {'form': form})

# Vista para eliminar una presentación de producto
def eliminar_presentacion(request, pk):
    presentacion = get_object_or_404(PresentacionProducto, pk=pk)
    if request.method == 'POST':
        presentacion.delete()
        return redirect('productos:listar_presentaciones')
    return render(request, 'productos/eliminar_presentacion.html', {'presentacion': presentacion})


# modelo Receta

# Listar recetas
def listar_recetas(request):
    recetas = Receta.objects.all()
    return render(request, 'productos/listar_recetas.html', {'recetas': recetas})

# Crear receta
def crear_receta(request):
    if request.method == 'POST':
        form = RecetaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productos:listar_recetas')
    else:
        form = RecetaForm()
    return render(request, 'productos/crear_receta.html', {'form': form})

# Editar receta
def editar_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    if request.method == 'POST':
        form = RecetaForm(request.POST, instance=receta)
        if form.is_valid():
            form.save()
            return redirect('productos:recetas_listar')
    else:
        form = RecetaForm(instance=receta)
    return render(request, 'productos/editar_receta.html', {'form': form})

# Eliminar receta
def eliminar_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    if request.method == 'POST':
        receta.delete()
        return redirect('productos:listar_recetas')
    return render(request, 'productos/eliminar_receta.html', {'receta': receta})