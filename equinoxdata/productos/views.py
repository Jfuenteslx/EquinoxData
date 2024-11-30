
from django.http import JsonResponse

from .forms import PresentacionProductoForm

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages

from .models import ProductoBase, PresentacionProducto, Receta
from .forms import ProductoBaseForm, RecetaForm, PresentacionProductoForm


def productosview(request):
    return render(request, 'productos/productos.html')



# Vista para listar productos base
def listar_producto_base(request):
    productos = ProductoBase.objects.all()
    return render(request, 'productos/lista_producto_base.html', {'productos': productos})

# Vista para crear un nuevo producto base
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoBaseForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda el nuevo producto
            return redirect('productos:listar_base')
    else:
        form = ProductoBaseForm()
    return render(request, 'productos/crear_producto.html', {'form': form})

# Vista para editar un producto base
def editar_producto(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        producto = ProductoBase.objects.get(id=producto_id)
        form = ProductoBaseForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('productos:listar_base')
    return redirect('productos:listar_base')

# Vista para eliminar un producto base
def eliminar_producto(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        producto = ProductoBase.objects.get(id=producto_id)
        producto.delete()
        return redirect('productos:listar_base')
    return redirect('productos:listar_base')

# vistas para recetas
# ---------------------------------

def listar_recetas(request):
    # Filtrar ProductoBase para mostrar solo aquellos que son insumos
    insumos = ProductoBase.objects.filter(categoria=True)  # Suponiendo que hay un campo 'es_insumo'

    # Pasar las recetas y los insumos filtrados
    recetas = Receta.objects.all()
    return render(request, 'productos/listar_recetas.html', {'recetas': recetas, 'insumos': insumos})

def crear_receta(request):
    if request.method == 'POST':
        form = RecetaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Receta creada exitosamente.")
            return redirect('productos:listar_recetas')
    else:
        form = RecetaForm()
    return render(request, 'productos/crear_receta.html', {'form': form})

def editar_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)

    if request.method == 'POST':
        form = RecetaForm(request.POST, instance=receta)

        if form.is_valid():
            form.save()

            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                # Si es una solicitud AJAX, puedes devolver una respuesta JSON
                return JsonResponse({'message': 'Receta actualizada exitosamente'})
            else:
                # Si no es AJAX, redirige a la vista adecuada
                return redirect('productos:listar_recetas')  # O el nombre de la vista de tu elección
    else:
        form = RecetaForm(instance=receta)

    return render(request, 'productos/editar_receta.html', {'form': form})



def eliminar_receta(request, receta_id):
    receta = get_object_or_404(Receta, id=receta_id)
    if request.method == 'POST':
        receta.delete()
        messages.success(request, "Receta eliminada exitosamente.")
        return redirect('productos:listar_recetas')
    return render(request, 'productos/eliminar_receta.html', {'receta': receta})

# ---------------------------------
# modelo presentacionproducto
# -------------------------------
# vistas

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import PresentacionProducto
from .forms import PresentacionProductoForm

# Listado de presentaciones
class PresentacionProductoListView(ListView):
    model = PresentacionProducto
    template_name = 'productos/presentacionproducto_list.html'
    context_object_name = 'presentaciones'

# Crear una nueva presentación
class PresentacionProductoCreateView(CreateView):
    model = PresentacionProducto
    form_class = PresentacionProductoForm
    template_name = 'productos/presentacionproducto_form.html'
    success_url = reverse_lazy('productos:listar_presentaciones')

# Editar una presentación existente
class PresentacionProductoUpdateView(UpdateView):
    model = PresentacionProducto
    form_class = PresentacionProductoForm
    template_name = 'productos/presentacionproducto_form.html'
    success_url = reverse_lazy('productos:listar_presentaciones')

# Eliminar una presentación
class PresentacionProductoDeleteView(DeleteView):
    model = PresentacionProducto
    template_name = 'productos/presentacionproducto_confirm_delete.html'
    success_url = reverse_lazy('productos:listar_presentaciones')
