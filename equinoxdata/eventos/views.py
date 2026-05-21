from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils.timezone import now
from .models import Evento, Cover
from .forms import EventoForm, CoverForm


@login_required
def listar_eventos(request):
    query = request.GET.get('q', '')
    eventos_futuros = Evento.objects.filter(fecha__gte=now())
    eventos_pasados = Evento.objects.filter(fecha__lt=now())
    if query:
        eventos_futuros = eventos_futuros.filter(
            Q(nombre__icontains=query) | Q(banda__icontains=query)
        )
        eventos_pasados = eventos_pasados.filter(
            Q(nombre__icontains=query) | Q(banda__icontains=query)
        )
    eventos_futuros = eventos_futuros.order_by('-fecha')
    eventos_pasados = eventos_pasados.order_by('-fecha')
    return render(request, 'eventos/listar_eventos.html', {
        'eventos_futuros': eventos_futuros,
        'eventos_pasados': eventos_pasados,
        'query': query,
    })


@login_required
def crear_evento(request):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene  permisos para crear eventos.')
        return redirect('usuarios:inicio')
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento creado correctamente.')
            return redirect('eventos:listar_eventos')
        else:
            messages.error(request, 'Error al crear el evento. Revise los datos.')
    else:
        form = EventoForm()
    return render(request, 'eventos/crear_evento.html', {'form': form})


@login_required
def actualizar_evento(request, pk):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene  permisos para editar eventos.')
        return redirect('usuarios:inicio')
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento actualizado correctamente.')
            return redirect('eventos:listar_eventos')
        else:
            messages.error(request, 'Error al actualizar el evento. Revise los datos.')
    else:
        form = EventoForm(instance=evento)
    return render(request, 'eventos/actualizar_evento.html', {
        'form': form,
        'evento': evento
    })


@login_required
def eliminar_evento(request, pk):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene  permisos para eliminar eventos.')
        return redirect('usuarios:inicio')
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == 'POST':
        evento.delete()
        messages.success(request, 'Evento eliminado correctamente.')
        return redirect('eventos:listar_eventos')
    return render(request, 'eventos/eliminar_evento.html', {'evento': evento})


@login_required
def crear_cover(request, evento_id):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene  permisos para crear covers.')
        return redirect('usuarios:inicio')
    evento = get_object_or_404(Evento, pk=evento_id)
    if request.method == 'POST':
        form = CoverForm(request.POST)
        if form.is_valid():
            cover = form.save(commit=False)
            cover.save()
            messages.success(request, 'Cover creado correctamente.')
            return redirect('eventos:listar_eventos')
        else:
            messages.error(request, 'Error al crear el cover. Revise los datos.')
    else:
        form = CoverForm()
    return render(request, 'eventos/crear_cover.html', {
        'form': form,
        'evento': evento
    })


@login_required
def editar_cover(request, cover_id):
    if not request.user.tiene_acceso_compras():
        messages.error(request, 'No tiene  permisos para editar covers.')
        return redirect('usuarios:inicio')
    cover = get_object_or_404(Cover, pk=cover_id)
    if request.method == 'POST':
        form = CoverForm(request.POST, instance=cover)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cover actualizado correctamente.')
            return redirect('eventos:listar_eventos')
        else:
            messages.error(request, 'Error al actualizar el cover. Revise los datos.')
    else:
        form = CoverForm(instance=cover)
    return render(request, 'eventos/editar_cover.html', {
        'form': form,
        'cover': cover
    })