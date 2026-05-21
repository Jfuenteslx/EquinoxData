from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import ProductoBase, ProductoMenu, RecetaItem
from .forms import ProductoBaseForm, ProductoMenuForm, RecetaItemFormSet


# ------------------------------------------------------------------
# Vista principal
# ------------------------------------------------------------------

@login_required
def productos_view(request):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene permisos para acceder a esta seccion.')
        return redirect('usuarios:inicio')
    total_insumos = ProductoBase.objects.filter(habilitado=True).count()
    total_menu = ProductoMenu.objects.filter(habilitado=True).count()
    return render(request, 'productos/productos.html', {
        'total_insumos': total_insumos,
        'total_menu': total_menu,
    })


# ------------------------------------------------------------------
# CRUD ProductoBase (Insumos)
# ------------------------------------------------------------------

@method_decorator(login_required, name='dispatch')
class ProductoBaseListView(ListView):
    model = ProductoBase
    template_name = 'productos/producto_base_list.html'
    context_object_name = 'productos_base'
    ordering = ['nombre']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.tiene_acceso_compras():
            messages.error(request, 'No tiene permisos para acceder a esta seccion.')
            return redirect('usuarios:inicio')
        return super().dispatch(request, *args, **kwargs)

@login_required
def producto_base_create(request):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene permisos para realizar esta accion.')
        return redirect('usuarios:inicio')
    if request.method == 'POST':
        form = ProductoBaseForm(request.POST)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Insumo "{producto.nombre}" creado correctamente.')
            return redirect('productos:producto-base-list')
    else:
        form = ProductoBaseForm()
    return render(request, 'productos/producto_base_form.html', {'form': form})


@login_required
def producto_base_update(request, pk):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene permisos para realizar esta accion.')
        return redirect('usuarios:inicio')
    producto = get_object_or_404(ProductoBase, pk=pk)
    if request.method == 'POST':
        form = ProductoBaseForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Insumo "{producto.nombre}" actualizado correctamente.')
            return redirect('productos:producto-base-list')
    else:
        form = ProductoBaseForm(instance=producto)
    return render(request, 'productos/producto_base_form.html', {
        'form': form,
        'object': producto
    })

@method_decorator(login_required, name='dispatch')
class ProductoBaseDeleteView(DeleteView):
    model = ProductoBase
    template_name = 'productos/producto_base_confirm_delete.html'
    success_url = reverse_lazy('productos:producto-base-list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.es_administrador():
            messages.error(request, 'Solo el administrador puede eliminar insumos.')
            return redirect('usuarios:inicio')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Insumo eliminado correctamente.')
        return super().form_valid(form)


# ------------------------------------------------------------------
# CRUD ProductoMenu
# ------------------------------------------------------------------

@method_decorator(login_required, name='dispatch')
class ProductoMenuListView(ListView):
    model = ProductoMenu
    template_name = 'productos/producto_menu_list.html'
    context_object_name = 'productos_menu'
    ordering = ['tipo', 'nombre']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.tiene_acceso_compras():
            messages.error(request, 'No tiene permisos para acceder a esta seccion.')
            return redirect('usuarios:inicio')
        return super().dispatch(request, *args, **kwargs)


@login_required
def producto_menu_create(request):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene permisos para realizar esta accion.')
        return redirect('usuarios:inicio')

    if request.method == 'POST':
        form = ProductoMenuForm(request.POST)
        formset = RecetaItemFormSet(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)
            if producto.tipo == 'coctel_jarra':
                formset = RecetaItemFormSet(request.POST, instance=producto)
                if formset.is_valid():
                    producto.save()
                    formset.save()
                    messages.success(request, f'Producto "{producto.nombre}" creado con receta.')
                    return redirect('productos:producto-menu-list')
            else:
                producto.save()
                messages.success(request, f'Producto "{producto.nombre}" creado correctamente.')
                return redirect('productos:producto-menu-list')
    else:
        form = ProductoMenuForm()
        formset = RecetaItemFormSet()

    return render(request, 'productos/producto_menu_form.html', {
        'form': form,
        'formset': formset,
    })


@login_required
def producto_menu_update(request, pk):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene permisos para realizar esta accion.')
        return redirect('usuarios:inicio')

    producto = get_object_or_404(ProductoMenu, pk=pk)

    if request.method == 'POST':
        form = ProductoMenuForm(request.POST, instance=producto)
        formset = RecetaItemFormSet(request.POST, instance=producto)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado correctamente.')
            return redirect('productos:producto-menu-list')
    else:
        form = ProductoMenuForm(instance=producto)
        formset = RecetaItemFormSet(instance=producto)

    return render(request, 'productos/producto_menu_form.html', {
        'form': form,
        'formset': formset,
        'producto': producto,
    })


@method_decorator(login_required, name='dispatch')
class ProductoMenuDeleteView(DeleteView):
    model = ProductoMenu
    template_name = 'productos/producto_menu_confirm_delete.html'
    success_url = reverse_lazy('productos:producto-menu-list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.es_administrador():
            messages.error(request, 'Solo el administrador puede eliminar productos del menu.')
            return redirect('usuarios:inicio')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Producto eliminado correctamente.')
        return super().form_valid(form)