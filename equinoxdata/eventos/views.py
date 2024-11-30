


from django.shortcuts import render, redirect, get_object_or_404
from .models import Evento, Cover
from .forms import EventoForm, CoverForm
from django.contrib import messages

# Vista para crear un evento
def crear_evento(request):
    if request.method == 'POST':
        evento_form = EventoForm(request.POST, request.FILES)  # Incluir archivos (imagen)
        if evento_form.is_valid():
            evento_form.save()
            return redirect('eventos:listar_eventos')  # Redirigir a la lista de eventos
    else:
        evento_form = EventoForm()

    return render(request, 'eventos/crear_evento.html', {'form': evento_form})


# Vista para listar todos los eventos

from django.db.models import Q
from django.utils.timezone import now

def listar_eventos(request):
    query = request.GET.get('q', '')  # Capturar el texto del buscador
    eventos_futuros = Evento.objects.filter(fecha__gte=now())  # Eventos que aún no se realizan
    eventos_pasados = Evento.objects.filter(fecha__lt=now())  # Eventos ya realizados

    # Filtrar los eventos según la búsqueda
    if query:
        eventos_futuros = eventos_futuros.filter(
            Q(nombre__icontains=query) | Q(banda__icontains=query)
        )
        eventos_pasados = eventos_pasados.filter(
            Q(nombre__icontains=query) | Q(banda__icontains=query)
        )

    # Ordenar por fecha descendente
    eventos_futuros = eventos_futuros.order_by('-fecha')
    eventos_pasados = eventos_pasados.order_by('-fecha')

    context = {
        'eventos_futuros': eventos_futuros,
        'eventos_pasados': eventos_pasados,
        'query': query,  # Para mantener el valor del buscador
    }
    return render(request, 'eventos/listar_eventos.html', context)



# Vista para actualizar un evento
def actualizar_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == 'POST':
        evento_form = EventoForm(request.POST, request.FILES, instance=evento)
        if evento_form.is_valid():
            evento_form.save()
            return redirect('eventos:listar_eventos')  # Redirigir a la lista de eventos
    else:
        evento_form = EventoForm(instance=evento)

    return render(request, 'eventos/actualizar_evento.html', {'form': evento_form, 'evento': evento})



# Vista para eliminar un evento


def eliminar_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == 'POST':
        evento.delete()
        return redirect('eventos:listar_eventos')  # Redirigir a la lista de eventos
    return render(request, 'eventos/eliminar_evento.html', {'evento': evento})




# covers aca estan las vistas
# --------------------

# Vista para crear un cover


def crear_cover(request, evento_id):
    # Obtener el evento asociado al cover
    evento = get_object_or_404(Evento, pk=evento_id)

    if request.method == 'POST':
        form = CoverForm(request.POST)
        if form.is_valid():
            cover = form.save(commit=False)
            cover.evento = evento  # Asociar el cover con el evento
            cover.save()
            messages.success(request, "¡El cover se creó correctamente!")
            return redirect('eventos:listar_eventos')  # Cambia esta URL si es necesario
    else:
        form = CoverForm()

    return render(request, 'eventos/crear_cover.html', {'form': form, 'evento': evento})

def editar_cover(request, cover_id):
    # Obtener el cover a editar
    cover = get_object_or_404(Cover, pk=cover_id)

    if request.method == 'POST':
        form = CoverForm(request.POST, instance=cover)
        if form.is_valid():
            form.save()
            messages.success(request, "¡El cover se actualizó correctamente!")
            return redirect('eventos:listar_eventos')  # Cambia esta URL si es necesario
    else:
        form = CoverForm(instance=cover)

    return render(request, 'eventos/editar_cover.html', {'form': form, 'cover': cover})