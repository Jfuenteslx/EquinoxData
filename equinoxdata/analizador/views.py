from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from eventos.models import Evento
from .models import CasoHistorico, ParametrosEntrada
from .forms import ParametrosForm, BusquedaForm
from .inferencia import reglas_inferencia
from .evaluacion import (
    buscar_casos_similares,
    calcular_performance_promedio,
    generar_recomendacion_compra,
)

from inventarios.models import Inventario


@login_required
def recibir_y_obtener_recomendacion(request):
    if not request.user.tiene_acceso_analizador():
        messages.error(request, 'No tiene permisos para acceder a esta seccion.')
        return redirect('usuarios:inicio')

    if request.method == 'POST':
        form = ParametrosForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            aforo   = data['aforo']
            ventas  = data['ventas']
            consumo = data['consumo']

            form.save()

            coeficiente = reglas_inferencia(aforo, ventas, consumo)

            parametros_nuevo = {
                'banda':          data['evento'].banda if hasattr(data['evento'], 'banda') else '',
                'tipo_evento':    data.get('tipo_evento', ''),
                'genero_musical': data.get('genero_musical', ''),
                'promociones':    data.get('promociones', ''),
                'aforo_esperado': aforo,
            }
            casos_similares = buscar_casos_similares(parametros_nuevo)
            performance = calcular_performance_promedio(casos_similares)
            recomendacion = generar_recomendacion_compra(coeficiente, casos_similares)
            costo_total = sum(r['costo_estimado'] for r in recomendacion)

            return render(request, 'analizador/resultados.html', {
                'coeficiente': coeficiente,
                'performance': performance,
                'casos_similares': [c for c, p in casos_similares],
                'recomendacion': recomendacion,
                'costo_total': costo_total,
                'resumen': {
                    'evento': data['evento'],
                    'aforo': aforo,
                    'ventas': ventas,
                    'consumo': consumo,
                    'tipo_evento': data.get('tipo_evento'),
                    'genero_musical': data.get('genero_musical'),
                    'promociones': data.get('promociones'),
                },
                'total_casos': len(casos_similares),
            })
        else:
            messages.error(request, 'Revise los datos ingresados.')
    else:
        form = ParametrosForm()

    return render(request, 'analizador/entrada_parametros.html', {'form': form})


@login_required
def consultar_casos(request):
    if not request.user.tiene_acceso_analizador():
        messages.error(request, 'No tiene permisos para acceder a esta seccion.')
        return redirect('usuarios:inicio')

    casos = CasoHistorico.objects.select_related('evento').all()

    tipo_evento = request.GET.get('tipo_evento')
    genero_musical = request.GET.get('genero_musical')

    if tipo_evento:
        casos = casos.filter(tipo_evento=tipo_evento)
    if genero_musical:
        casos = casos.filter(genero_musical=genero_musical)

    return render(request, 'analizador/consultar_casos.html', {
        'casos': casos,
        'form': BusquedaForm(request.GET or None),
    })


@login_required
def evaluar_casos_similares_view(request):
    if not request.user.tiene_acceso_analizador():
        messages.error(request, 'No tiene permisos para acceder a esta seccion.')
        return redirect('usuarios:inicio')

    form = BusquedaForm()
    casos_con_artista = []

    if request.method == 'POST':
        form = BusquedaForm(request.POST)
        if form.is_valid():
            parametros = {
                'banda':          '',
                'tipo_evento':    form.cleaned_data.get('tipo_evento', ''),
                'genero_musical': form.cleaned_data.get('genero_musical', ''),
                'promociones':    form.cleaned_data.get('promociones', ''),
                'aforo_esperado': 0,
            }
            casos_similares = buscar_casos_similares(parametros)
            casos_con_artista = [
                {
                    'caso': caso,
                    'puntaje': round(puntaje * 100, 1),
                    'banda': caso.evento.banda if hasattr(caso.evento, 'banda') else '—',
                    'fecha': caso.evento.fecha,
                }
                for caso, puntaje in casos_similares
            ]

    return render(request, 'analizador/casos_similares.html', {
        'form': form,
        'casos_con_artista': casos_con_artista,
    })


@login_required
def buscar_casos_similares_view(request):
    return redirect('analizador:evaluar_casos')


@login_required
def generar_recomendacion(request):
    if not request.user.tiene_acceso_analizador():
        messages.error(request, 'No tiene permisos para acceder a esta seccion.')
        return redirect('usuarios:inicio')

    coeficiente = float(request.GET.get('coeficiente', 50))
    recomendacion = generar_recomendacion_compra(coeficiente, [])
    costo_total = sum(r['costo_estimado'] for r in recomendacion)

    return render(request, 'analizador/recomendacion_compra.html', {
        'recomendacion': recomendacion,
        'coeficiente': coeficiente,
        'costo_total': costo_total,
    })


@login_required
def generar_casos_historicos(request):
    if not request.user.es_administrador():
        messages.error(request, 'No tiene permisos para realizar esta accion.')
        return redirect('usuarios:inicio')

    eventos = Evento.objects.all()
    return render(request, 'analizador/casos_historicos_generados.html', {
        'eventos': eventos
    })


@login_required
def mostrar_resultados(request):
    return redirect('analizador:entrada')


@login_required
def crear_caso_historico(request, consolidacion_id):
    if not request.user.es_administrador():
        messages.error(request, 'No tiene permisos para realizar esta accion.')
        return redirect('usuarios:inicio')

    consolidacion = get_object_or_404(Consolidacion, id=consolidacion_id)


    evento_temp = consolidacion.sesion.evento
    if evento_temp and CasoHistorico.objects.filter(evento=evento_temp).exists():
        messages.warning(request, 'Ya existe un caso historico para este evento.')
        return redirect('ventas:revisar_consolidaciones')    



    from .forms import TIPO_EVENTO_CHOICES, GENERO_MUSICAL_CHOICES, PROMOCIONES_CHOICES

    # Obtener evento
    evento = consolidacion.sesion.evento
    if not evento:
        evento_id = request.POST.get('evento_id') if request.method == 'POST' else None
        if evento_id:
            evento = Evento.objects.filter(id=evento_id).first()

    if request.method == 'POST':
        if not evento:
            evento_id = request.POST.get('evento_id')
            if evento_id:
                evento = Evento.objects.filter(id=evento_id).first()

        if not evento:
            messages.error(request, 'Debe seleccionar un evento para crear el caso historico.')
            return redirect('ventas:revisar_consolidaciones')

        tipo_evento      = request.POST.get('tipo_evento', '')
        genero_musical   = request.POST.get('genero_musical', '')
        promociones      = request.POST.get('promociones', 'No aplica')
        aforo_esperado   = int(request.POST.get('aforo_esperado', 0))
        ventas_esperadas = int(request.POST.get('ventas_esperadas', 2000))
        consumo_esperado = int(request.POST.get('consumo_esperado', 30))

        # Sumar ventas de TODAS las consolidaciones del mismo evento
        consolidaciones_evento = Consolidacion.objects.filter(sesion__evento=evento)
        resumen_ventas_total = {}
        total_ventas_real = 0

        for cons in consolidaciones_evento:
            total_ventas_real += float(cons.sesion.total_ventas)
            for nombre, datos in (cons.resumen or {}).items():
                if nombre not in resumen_ventas_total:
                    resumen_ventas_total[nombre] = {
                        'cantidad_total': 0,
                        'total_bs': 0,
                    }
                resumen_ventas_total[nombre]['cantidad_total'] += datos.get('cantidad_total', 0)
                resumen_ventas_total[nombre]['total_bs'] += float(str(datos.get('total_bs', 0)))

        # Performance: ventas reales totales del evento / ventas esperadas
        if ventas_esperadas > 0:
            performance = round((total_ventas_real / ventas_esperadas) * 100, 2)
        else:
            performance = 0

        # Coeficiente con lógica difusa
        coeficiente = reglas_inferencia(aforo_esperado, ventas_esperadas, consumo_esperado)

        # Snapshot del inventario actual
        inventarios = Inventario.objects.select_related('producto').all()
        resumen_inventario = {
            inv.producto.nombre: {
                'botellas': inv.botellas,
                'medidas_sueltas': float(inv.medidas_sueltas),
            }
            for inv in inventarios
        }

        CasoHistorico.objects.create(
            evento=evento,
            sesion=consolidacion,
            tipo_evento=tipo_evento,
            genero_musical=genero_musical,
            promociones=promociones,
            aforo_esperado=aforo_esperado,
            ventas_esperadas=total_ventas_real,
            consumo_per_capita=consumo_esperado,
            coeficiente=coeficiente,
            performance=performance,
            resumen_ventas=resumen_ventas_total,
            resumen_inventario=resumen_inventario,
        )

        messages.success(
            request,
            f'Caso historico creado. Ventas totales del evento: Bs. {total_ventas_real:.2f} | Coeficiente: {coeficiente}% | Performance: {performance}%'
        )
        return redirect('analizador:consultar_casos')

    # Total de ventas de TODAS las sesiones del evento para precargar
    if evento:
        total_evento = sum(
            float(c.sesion.total_ventas)
            for c in Consolidacion.objects.filter(sesion__evento=evento)
        )
    else:
        total_evento = float(consolidacion.sesion.total_ventas)

    eventos_disponibles = Evento.objects.all().order_by('-fecha')

    return render(request, 'analizador/crear_caso_historico.html', {
        'consolidacion': consolidacion,
        'total_ventas': total_evento,
        'evento': evento,
        'eventos': eventos_disponibles,
        'tipo_evento_choices': TIPO_EVENTO_CHOICES,
        'genero_musical_choices': GENERO_MUSICAL_CHOICES,
        'promociones_choices': PROMOCIONES_CHOICES,
    })