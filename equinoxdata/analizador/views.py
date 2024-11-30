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

            # Redirigir o mostrar la recomendación
            resumen=form.cleaned_data
             # Recupera el último registro de la tabla RegistroStock
            ultimo_registro = RegistroStock.objects.last()  # .last() devuelve el último registro insertado
            print(ultimo_registro)
    # Si no hay registros, podemos manejarlo aquí
            if not ultimo_registro:
                  ultimo_registro = "No hay registros en la tabla."
            return render(request, 'analizador/recomendacion.html', {'recomendacion': recomendacion, 'resumen': resumen, 'ultimo_registro': ultimo_registro})
    else:
        form = ParametrosForm()

    return render(request, 'analizador/entrada_parametros.html', {'form': form})


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

from django.shortcuts import render
from .models import CasoHistorico
from .evaluacion import evaluar_casos_similares, generar_recomendacion_compra
from .forms import ParametrosForm

def evaluar_casos_similares_view(request):
    if request.method == 'POST':
        form = ParametrosForm(request.POST)
        if form.is_valid():
            # Obtener los datos del formulario
            aforo = form.cleaned_data['aforo']
            ventas = form.cleaned_data['ventas']
            consumo = form.cleaned_data['consumo']
            
            # Obtener todos los casos históricos y evaluar la similitud
            casos_historicos = CasoHistorico.objects.all()
            casos_similares = evaluar_casos_similares(aforo, ventas, consumo, casos_historicos)
            
            # Generar recomendación de compra basada en los casos similares
            recomendacion_compra = generar_recomendacion_compra(casos_similares)
            
            return render(request, 'analizador/evaluar_casos_similares.html', {
                'form': form,
                'casos_similares': casos_similares,
                'recomendacion_compra': recomendacion_compra
            })
    else:
        form = ParametrosForm()

    return render(request, 'analizador/evaluar_casos_similares.html', {'form': form})


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


