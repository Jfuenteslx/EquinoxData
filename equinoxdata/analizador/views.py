from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from eventos.models import Evento
from .models import CasoHistorico, ParametrosEntrada
from .forms import ParametrosForm, BusquedaForm
from .inferencia import reglas_inferencia


@login_required
def recibir_y_obtener_recomendacion(request):
    if not request.user.tiene_acceso_analizador():
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')

    if request.method == 'POST':
        form = ParametrosForm(request.POST)
        if form.is_valid():
            aforo = form.cleaned_data['aforo']
            ventas = form.cleaned_data['ventas']
            consumo = form.cleaned_data['consumo']

            form.save()

            recomendacion = reglas_inferencia(aforo, ventas, consumo)

            return render(request, 'analizador/resultados.html', {
                'recomendacion': recomendacion,
                'resumen': {
                    'aforo': aforo,
                    'ventas': ventas,
                    'consumo': consumo,
                },
                'busqueda_form': BusquedaForm(),
            })
    else:
        form = ParametrosForm()

    return render(request, 'analizador/entrada_parametros.html', {'form': form})


@login_required
def mostrar_resultados(request):
    if not request.user.tiene_acceso_analizador():
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')

    return render(request, 'analizador/resultados.html', {
        'recomendacion': request.GET.get('recomendacion'),
        'resumen': request.GET.get('resumen'),
    })


@login_required
def evaluar_casos_similares_view(request):
    if not request.user.tiene_acceso_analizador():
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')

    form = BusquedaForm()

    if request.method == 'POST':
        tipo_evento = request.POST.get('tipo_evento')
        genero_musical = request.POST.get('genero_musical')
        promociones = request.POST.get('promociones')

        filtros = Q()
        if tipo_evento:
            filtros &= Q(tipo_evento=tipo_evento)
        if genero_musical:
            filtros &= Q(genero_musical=genero_musical)
        if promociones:
            filtros &= Q(promociones=promociones)

        casos_similares = CasoHistorico.objects.filter(filtros).select_related('evento')

        casos_con_info = []
        for caso in casos_similares:
            casos_con_info.append({
                'caso': caso,
                'banda': caso.evento.banda,
                'fecha': caso.evento.fecha,
            })

        return render(request, 'analizador/casos_similares.html', {
            'form': form,
            'casos_con_artista': casos_con_info,
        })

    return render(request, 'analizador/casos_similares.html', {'form': form})


@login_required
def buscar_casos_similares(request):
    if not request.user.tiene_acceso_analizador():
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')

    if request.method == 'POST':
        form = BusquedaForm(request.POST)
        if form.is_valid():
            tipo_evento = form.cleaned_data.get('tipo_evento')
            genero_musical = form.cleaned_data.get('genero_musical')
            promociones = form.cleaned_data.get('promociones')

            condiciones = []
            if tipo_evento:
                condiciones.append(Q(tipo_evento=tipo_evento))
            if genero_musical:
                condiciones.append(Q(genero_musical=genero_musical))
            if promociones:
                condiciones.append(Q(promociones=promociones))

            if len(condiciones) < 2:
                messages.error(request, 'Debe proporcionar al menos dos parametros para la busqueda.')
                return redirect('analizador:buscar_casos')

            query = condiciones.pop()
            for condicion in condiciones:
                query |= condicion

            casos = CasoHistorico.objects.filter(query)
            resultados = sorted(casos, key=lambda c: c.performance, reverse=True)

            return render(request, 'analizador/resultados_busqueda.html', {
                'casos_similares': resultados,
                'form': form,
            })

    return render(request, 'analizador/error.html', {'mensaje': 'Metodo no permitido.'})


@login_required
def consultar_casos(request):
    if not request.user.tiene_acceso_analizador():
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')

    casos = CasoHistorico.objects.select_related('evento').all()

    tipo_evento = request.GET.get('tipo_evento')
    genero_musical = request.GET.get('genero_musical')

    if tipo_evento:
        casos = casos.filter(tipo_evento=tipo_evento)
    if genero_musical:
        casos = casos.filter(genero_musical=genero_musical)

    return render(request, 'analizador/consultar_casos.html', {'casos': casos})


@login_required
def generar_casos_historicos(request):
    if not request.user.es_administrador():
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('usuarios:inicio')

    eventos = Evento.objects.all()
    if not eventos.exists():
        return render(request, 'analizador/error.html', {
            'mensaje': 'No hay eventos disponibles para generar casos históricos.'
        })

    return render(request, 'analizador/casos_historicos_generados.html', {'eventos': eventos})


@login_required
def generar_recomendacion(request):
    if not request.user.tiene_acceso_analizador():
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')

    from productos.models import ProductoBase
    import random

    productos = ProductoBase.objects.filter(habilitado=True)
    recomendacion = []
    for producto in productos:
        cantidad = random.randint(1, 15)
        recomendacion.append({
            'producto': producto.nombre,
            'cantidad': cantidad,
            'costo_unitario': float(producto.precio_costo),
            'costo_total': round(cantidad * float(producto.precio_costo), 2),
        })

    return render(request, 'analizador/recomendacion_compra.html', {
        'recomendacion': recomendacion
    })