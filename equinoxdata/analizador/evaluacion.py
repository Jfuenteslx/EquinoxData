from .models import CasoHistorico


def umbral_similitud(evento, tipo_evento, show_presentado, genero_musical, caso_historico):
    """
    Calcula la similitud entre un caso actual y un caso histórico.
    """
    peso_evento = 0.3  # Ponderación para la variable 'evento'
    peso_tipo_evento = 0.3  # Ponderación para 'tipo_evento'
    peso_show = 0.2  # Ponderación para 'show_presentado'
    peso_genero = 0.2  # Ponderación para 'genero_musical'

    # Variables binarias: iguales o no
    similitud_evento = 1 if evento == caso_historico.evento else 0
    similitud_tipo_evento = 1 if tipo_evento == caso_historico.tipo_evento else 0
    similitud_show = 1 if show_presentado == caso_historico.show_presentado else 0
    similitud_genero = 1 if genero_musical == caso_historico.genero_musical else 0

    # Calcula el puntaje total de similitud
    puntaje_similitud = (
        (similitud_evento * peso_evento)
        + (similitud_tipo_evento * peso_tipo_evento)
        + (similitud_show * peso_show)
        + (similitud_genero * peso_genero)
    )

    return puntaje_similitud


# Evaluar la similitud entre un caso nuevo y casos históricos
def evaluar_casos_similares(evento, tipo_evento, show_presentado, genero_musical, casos_historicos):
    """
    Busca casos históricos similares al caso actual basado en variables no difusas.
    """
    umbral_minimo = 0.7  # Define un valor mínimo aceptable de similitud (escala de 0 a 1)
    casos_similares = []

    for caso in casos_historicos:
        # Calcula la similitud con el caso histórico
        puntaje_similitud = umbral_similitud(evento, tipo_evento, show_presentado, genero_musical, caso)
        
        if puntaje_similitud >= umbral_minimo:  # Si supera el umbral, es un caso similar
            casos_similares.append(caso)
    
    return casos_similares

# Función para calcular la similitud entre el caso actual y un caso histórico
def calcular_similitud(aforo, ventas, consumo, caso):
    # Aquí se implementa el cálculo de similitud
    similitud = 0
    # Ejemplo simple de similitud
    similitud += abs(aforo - caso.aforo)
    similitud += abs(ventas - caso.ventas)
    similitud += abs(consumo - caso.consumo)
    return similitud

# Generar recomendación de compra basada en los casos similares encontrados
def generar_recomendacion_compra(casos_similares):
    recomendacion = "Basado en los casos similares, recomendamos una compra de..."
    # Lógica para generar la recomendación a partir de los casos similares
    return recomendacion
