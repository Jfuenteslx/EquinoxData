# analizador/views.py


from .forms import ParametrosForm  # Formulario que crearemos para recibir los datos

import numpy as np
import skfuzzy as fuzz
from django.shortcuts import render, redirect
from .inferencia import reglas_inferencia  # Importa la función que define las reglas
from inventarios.models import RegistroStock
from .models import Evento



# definicion de variables de ingreso y calculo takagi sugeno
# -----------------------------------------------   --------------------------------------------------
def recibir_y_obtener_recomendacion(request):
    if request.method == 'POST':
        form = ParametrosForm(request.POST)
        if form.is_valid():
            # Obtener los datos del formulario
            aforo = form.cleaned_data['aforo']
            ventas = form.cleaned_data['ventas']
            consumo = form.cleaned_data['consumo']

            # Guardar los datos en la base de datos
            form.save()

            # Obtener la recomendación basada en los parámetros ingresados
            recomendacion = reglas_inferencia(aforo, ventas, consumo)

            # Recuperar el último registro de la tabla RegistroStock
            ultimo_registro = RegistroStock.objects.last()

            # Si no hay registros, establecer un mensaje predeterminado
            if not ultimo_registro:
                ultimo_registro = {"fecha": None, "inventario_json": "No hay registros en la tabla."}

            # Crear una instancia del formulario de búsqueda
            busqueda_form = BusquedaForm()

            # Renderizar directamente la plantilla de resultados
            return render(request, 'analizador/resultados.html', {
                'recomendacion': recomendacion,
                'ultimo_registro': ultimo_registro,
                'resumen': {
                    'aforo': aforo,
                    'ventas': ventas,
                    'consumo': consumo,
                },
                'busqueda_form': busqueda_form,
            })
    
    else:
        form = ParametrosForm()

    return render(request, 'analizador/entrada_parametros.html', {'form': form})



def mostrar_resultados(request):
    recomendacion = request.GET.get('recomendacion', None)
    resumen = request.GET.get('resumen', None)

    # Recuperar el último registro de RegistroStock
    ultimo_registro = RegistroStock.objects.last()
    if not ultimo_registro:
        ultimo_registro = "No hay registros en la tabla."

    return render(request, 'analizador/resultados.html', {
        'recomendacion': recomendacion,
        'ultimo_registro': ultimo_registro,
        'resumen': resumen
    })




# recuperacion de casos
# --------------------------------------------------------------------------------

from math import sqrt
from .models import CasoHistorico

def calcular_similitud(aforo, ventas, consumo, tipo_evento, show_presentado, genero_musical, promociones, caso):
    # Pesos para las variables difusas
    peso_aforo = 0.25
    peso_ventas = 0.25
    peso_consumo = 0.25
    
    # Pesos para las variables no difusas
    peso_tipo_evento = 0.1
    peso_show_presentado = 0.05
    peso_genero_musical = 0.05
    peso_promociones = 0.05
    
    # Calcular similitud para las variables difusas
    diferencia_aforo = abs(aforo - caso.aforo) * peso_aforo
    diferencia_ventas = abs(ventas - caso.ventas) * peso_ventas
    diferencia_consumo = abs(consumo - caso.consumo) * peso_consumo
    
    # Calcular similitud para las variables no difusas (1 si son diferentes, 0 si son iguales)
    diferencia_tipo_evento = (tipo_evento != caso.tipo_evento) * peso_tipo_evento
    diferencia_show_presentado = (show_presentado != caso.show_presentado) * peso_show_presentado
    diferencia_genero_musical = (genero_musical != caso.genero_musical) * peso_genero_musical
    diferencia_promociones = (promociones != caso.promociones) * peso_promociones
    
    # Similitud total como suma ponderada
    similitud = (
        diferencia_aforo + diferencia_ventas + diferencia_consumo +
        diferencia_tipo_evento + diferencia_show_presentado +
        diferencia_genero_musical + diferencia_promociones
    )
    return similitud







from .forms import ParametrosForm
from .models import CasoHistorico


from django.db.models import Q
from .models import CasoHistorico, Evento

from django.shortcuts import render
from .forms import BusquedaForm
from .models import CasoHistorico, Evento
from django.db.models import Q

def evaluar_casos_similares_view(request):
    form = BusquedaForm()  # Crea una instancia vacía del formulario

    if request.method == 'POST':
        # Obtener los datos del formulario
        tipo_evento = request.POST.get('tipo_evento')
        show_presentado = request.POST.get('show_presentado')
        genero_musical = request.POST.get('genero_musical')
        promociones = request.POST.get('promociones')

        # Filtrar los casos históricos basados en las coincidencias con al menos 2 de los parámetros
        filtros = Q()

        if tipo_evento:
            filtros &= Q(tipo_evento=tipo_evento)
        if show_presentado:
            filtros &= Q(show_presentado=show_presentado)
        if genero_musical:
            filtros &= Q(genero_musical=genero_musical)
        if promociones:
            filtros &= Q(promociones=promociones)

        # Obtener los casos históricos que coincidan con al menos dos de los filtros
        casos_similares = CasoHistorico.objects.filter(filtros)

        # Agregar la información del artista desde la tabla Evento
        casos_con_artista = []
        for caso in casos_similares:
            evento = Evento.objects.get(id=caso.evento_id)
            casos_con_artista.append({
                'caso': caso,
                'banda': evento.banda,
                'fecha': evento.fecha,
            })

        return render(request, 'analizador/casos_similares.html', {
            'form': form,  # Asegúrate de pasar el formulario al contexto
            'casos_con_artista': casos_con_artista
        })

    return render(request, 'analizador/casos_similares.html', {
        'form': form,  # Asegúrate de pasar el formulario al contexto cuando es un GET
    })


from django.db.models import Q
from django.shortcuts import render
from .models import CasoHistorico
from .forms import BusquedaForm

def buscar_casos_similares(request):
    if request.method == 'POST':
        form = BusquedaForm(request.POST)
        if form.is_valid():
            # Obtener los parámetros del formulario
            tipo_evento = form.cleaned_data.get('tipo_evento')
            show_presentado = form.cleaned_data.get('show_presentado')
            genero_musical = form.cleaned_data.get('genero_musical')
            promociones = form.cleaned_data.get('promociones')

            # Inicializamos una lista de condiciones
            condiciones = []

            if tipo_evento:
                condiciones.append(Q(tipo_evento=tipo_evento))
            if show_presentado:
                condiciones.append(Q(show_presentado=show_presentado))
            if genero_musical:
                condiciones.append(Q(genero_musical=genero_musical))
            if promociones:
                condiciones.append(Q(promociones=promociones))

            # Buscamos casos que cumplan al menos dos condiciones
            if len(condiciones) < 2:
                return render(request, 'analizador/error.html', {
                    'mensaje': 'Debes proporcionar al menos dos parámetros para la búsqueda.'
                })

            # Combinar condiciones con Q() y realizar búsqueda
            query = condiciones.pop()  # Inicia la query con la primera condición
            for condicion in condiciones:
                query |= condicion  # Combina las condiciones con OR

            casos_similares = CasoHistorico.objects.filter(query)

            # Filtrar solo aquellos con al menos 2 coincidencias
            resultados = []
            for caso in casos_similares:
                coincidencias = 0
                if tipo_evento and caso.tipo_evento == tipo_evento:
                    coincidencias += 1
                if show_presentado and caso.show_presentado == show_presentado:
                    coincidencias += 1
                if genero_musical and caso.genero_musical == genero_musical:
                    coincidencias += 1
                if promociones and caso.promociones == promociones:
                    coincidencias += 1

                if coincidencias >= 2:
                    resultados.append(caso)

            # Ordenar los resultados por 'performance' de mayor a menor
            resultados.sort(key=lambda caso: caso.performance, reverse=True)

            # Renderizamos los resultados en la plantilla
            return render(request, 'analizador/resultados_busqueda.html', {
                'casos_similares': resultados,  # Casos encontrados
                'form': form,  # Pasar el formulario
                'tipo_evento': tipo_evento,
                'show_presentado': show_presentado,
                'genero_musical': genero_musical,
                'promociones': promociones,
            })

    return render(request, 'analizador/error.html', {
        'mensaje': 'Método no permitido.',
    })



# simulacion de casos historicos (solo para pruebas)

from django.shortcuts import render
from analizador.models import CasoHistorico
from eventos.models import Evento
from .utils import simular_ventas, simular_compras, simular_inventario, calcular_coeficiente, calcular_performance

def generar_casos_historicos(request):
    eventos = Evento.objects.all()

    if not eventos.exists():
        return render(request, 'analizador/error.html', {"mensaje": "No hay eventos disponibles para generar casos históricos."})

    # Recorrer todos los eventos existentes
    for evento in eventos:
        # Simular ventas para el evento
        cuenta = simular_ventas(evento)  # Devuelve una instancia de Cuenta

        # Obtener el diccionario de ventas desde el campo 'cuenta'
        ventas = cuenta.cuenta  # Este es el diccionario con las ventas simuladas

        # Simular compras para el evento basado en las ventas
        compras = simular_compras(evento, ventas)  # Devuelve una instancia de Pedido

        # Simular inventario para el evento basado en las compras y ventas
        registro_stock = simular_inventario(evento, compras, ventas)  # Devuelve una instancia de RegistroStock

        # Calcular coeficiente y performance
        coeficiente = calcular_coeficiente(evento)
        performance = calcular_performance(evento)

        # Crear un caso histórico con la información simulada
        CasoHistorico.objects.create(
            evento=evento,
            tipo_evento="Concierto de Rock",  # Puedes personalizar esto según sea necesario
            show_presentado=evento.nombre,  # Nombre del evento
            genero_musical="Rock Clásico",  # Puedes ajustar este campo según los datos disponibles
            promociones="2x1 en cervezas",  # Ejemplo de promoción
            coeficiente=coeficiente,
            performance=performance,
            pedido=compras,  # Instancia de Pedido
            cuenta=cuenta,  # Instancia de Cuenta
            inventario=registro_stock  # Instancia de RegistroStock
        )

    return render(request, 'analizador/casos_historicos_generados.html', {'eventos': eventos})



from django.shortcuts import render
from analizador.models import CasoHistorico

def consultar_casos(request):
    # Obtener todos los casos históricos
    casos = CasoHistorico.objects.select_related('evento').all()

    # Filtrar por parámetros opcionales (si se implementa)
    tipo_evento = request.GET.get('tipo_evento')
    genero_musical = request.GET.get('genero_musical')

    if tipo_evento:
        casos = casos.filter(tipo_evento=tipo_evento)
    if genero_musical:
        casos = casos.filter(genero_musical=genero_musical)

    # Pasar los casos al template
    context = {'casos': casos}
    return render(request, 'analizador/consultar_casos.html', context)


# recomendaciones de compra
import random
from django.shortcuts import render

def generar_recomendacion(request):
    # Lista de productos ficticios para la recomendación
    productos = [
        'Chivas Regal', 'Jack Daniels', 'J. Walker', 'Jagermeister', 'Tequila Jarana',
        'Tequila Jose Cuervo', 'Fernet Branca', 'Singani Viuda Descalza', 'Singani Casa Real',
        'Ron Diplomatico', 'Ron Havana 7 años', 'Vodka Stolichnaya', 'Gin La Republica',
        'Vodka Karat', 'Ron Cap Cortez', 'Bendita Ipa', 'Bendita Hoppy', 'Huari', 'Heineken',
        'Cordillera', 'Equichela', 'Carabao', '500 coca', '500 sprite', 'h20 peq', 'coca cola', 'sprite', 'agua'
    ]

    # Generar valores aleatorios de compra (simulados) con un máximo de 15 unidades
    recomendacion = []
    for producto in productos:
        cantidad = random.randint(1, 15)  # Cantidades aleatorias entre 1 y 15
        costo_unitario = round(random.uniform(20, 500), 2)  # Costo entre 20 y 500
        recomendacion.append({
            'producto': producto,
            'cantidad': cantidad,
            'costo_unitario': costo_unitario,
            'costo_total': round(cantidad * costo_unitario, 2)
        })

    return render(request, 'analizador/recomendacion_compra.html', {'recomendacion': recomendacion})
