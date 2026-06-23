from datetime import date
from .models import CasoHistorico
from inventarios.models import Inventario


# ------------------------------------------------------------------
# Pesos para el cálculo de similitud entre casos (CBR)
# ------------------------------------------------------------------
PESOS_SIMILITUD = {
    'banda':          0.30,
    'tipo_evento':    0.20,
    'genero_musical': 0.20,
    'promociones':    0.15,
    'aforo':          0.10,
    'proximidad':     0.05,
}

UMBRAL_MINIMO = 0.40   # Similitud mínima para considerar un caso
MAX_CASOS = 10          # Máximo de casos similares a recuperar


def similitud_texto(a, b):
    """Similitud binaria entre dos strings."""
    if not a or not b:
        return 0
    return 1 if str(a).strip().lower() == str(b).strip().lower() else 0


def similitud_numerica(val_nuevo, val_historico, rango_max):
    """Similitud numérica normalizada. Más cercanos = más similares."""
    if rango_max == 0:
        return 1
    diff = abs(val_nuevo - val_historico)
    return max(0, 1 - diff / rango_max)


def similitud_temporal(fecha_evento_historico):
    """
    Penaliza casos más antiguos.
    - Último año: 1.0
    - Cada año adicional: -0.15
    - Mínimo: 0.40 (eventos de más de 4 años)
    """
    if not fecha_evento_historico:
        return 0.40
    hoy = date.today()
    anos_diferencia = (hoy - fecha_evento_historico).days / 365.0
    factor = max(0.40, 1.0 - (anos_diferencia * 0.15))
    return round(factor, 4)


def calcular_similitud(parametros_nuevo, caso_historico):
    """
    Calcula la similitud ponderada entre un caso nuevo y un caso histórico.

    Args:
        parametros_nuevo: dict con banda, tipo_evento, genero_musical,
                          promociones, aforo_esperado
        caso_historico: instancia de CasoHistorico

    Returns:
        float: puntaje de similitud entre 0 y 1
    """
    # Banda/grupo — mayor predictor
    banda_nuevo = parametros_nuevo.get('banda', '')
    banda_historico = ''
    if caso_historico.evento and hasattr(caso_historico.evento, 'banda'):
        banda_historico = caso_historico.evento.banda or ''
    sim_banda = similitud_texto(banda_nuevo, banda_historico)

    # Tipo de evento
    sim_tipo = similitud_texto(
        parametros_nuevo.get('tipo_evento'),
        caso_historico.tipo_evento
    )

    # Género musical
    sim_genero = similitud_texto(
        parametros_nuevo.get('genero_musical'),
        caso_historico.genero_musical
    )

    # Promociones
    sim_promo = similitud_texto(
        parametros_nuevo.get('promociones'),
        caso_historico.promociones
    )

    # Aforo
    sim_aforo = similitud_numerica(
        parametros_nuevo.get('aforo_esperado', 0),
        caso_historico.aforo_esperado,
        rango_max=300
    )

    # Proximidad temporal
    fecha_hist = None
    if caso_historico.evento:
        fecha_hist = caso_historico.evento.fecha
    sim_temporal = similitud_temporal(fecha_hist)

    puntaje = (
        sim_banda   * PESOS_SIMILITUD['banda'] +
        sim_tipo    * PESOS_SIMILITUD['tipo_evento'] +
        sim_genero  * PESOS_SIMILITUD['genero_musical'] +
        sim_promo   * PESOS_SIMILITUD['promociones'] +
        sim_aforo   * PESOS_SIMILITUD['aforo'] +
        sim_temporal * PESOS_SIMILITUD['proximidad']
    )
    return round(puntaje, 4)


def buscar_casos_similares(parametros_nuevo):
    """
    Recupera los casos históricos más similares al caso nuevo.

    Returns:
        list: lista de tuplas (caso_historico, puntaje_similitud)
              ordenada por similitud descendente
    """
    todos_los_casos = CasoHistorico.objects.select_related('evento').all()
    casos_con_puntaje = []

    for caso in todos_los_casos:
        puntaje = calcular_similitud(parametros_nuevo, caso)
        if puntaje >= UMBRAL_MINIMO:
            casos_con_puntaje.append((caso, puntaje))

    casos_con_puntaje.sort(key=lambda x: x[1], reverse=True)
    return casos_con_puntaje[:MAX_CASOS]


def calcular_performance_promedio(casos_similares):
    """
    Calcula el performance promedio ponderado de los casos similares.
    El performance es ventas_reales / ventas_esperadas * 100.

    Returns:
        float o None
    """
    if not casos_similares:
        return None

    suma_ponderada = 0
    suma_pesos = 0

    for caso, puntaje in casos_similares:
        if caso.performance > 0:
            suma_ponderada += caso.performance * puntaje
            suma_pesos += puntaje

    if suma_pesos == 0:
        return None

    return round(suma_ponderada / suma_pesos, 2)


def generar_recomendacion_compra(coeficiente, casos_similares):
    """
    Genera la recomendación de compra basada en el coeficiente difuso
    y el inventario actual.

    Args:
        coeficiente: float entre 0 y 100
        casos_similares: lista de tuplas (caso_historico, puntaje)

    Returns:
        list: lista de dicts con recomendación por producto
    """
    factor = coeficiente / 100.0
    inventarios = Inventario.objects.select_related('producto').all()
    recomendaciones = []

    # Consumo histórico promedio por producto
    consumo_por_producto = {}
    if casos_similares:
        for caso, puntaje in casos_similares:
            resumen = caso.resumen_ventas or {}
            for nombre_prod, datos in resumen.items():
                if nombre_prod not in consumo_por_producto:
                    consumo_por_producto[nombre_prod] = []
                consumo_por_producto[nombre_prod].append(
                    datos.get('cantidad_total', 0)
                )

    consumo_promedio = {
        nombre: sum(vals) / len(vals)
        for nombre, vals in consumo_por_producto.items()
        if vals
    }

    for inv in inventarios:
        producto = inv.producto
        stock_actual_botellas = inv.botellas
        stock_actual_medidas = float(inv.medidas_sueltas)

        consumo_hist = consumo_promedio.get(producto.nombre, 0)

        if producto.medidas_por_unidad > 0 and consumo_hist > 0:
            medidas_necesarias = consumo_hist * factor
            botellas_necesarias = medidas_necesarias / producto.medidas_por_unidad
        else:
            botellas_necesarias = max(2, round(stock_actual_botellas * factor))

        botellas_a_comprar = max(0, round(botellas_necesarias - stock_actual_botellas))

        recomendaciones.append({
            'producto': producto.nombre,
            'unidad': producto.get_unidad_medida_display(),
            'stock_actual_botellas': stock_actual_botellas,
            'stock_actual_medidas': stock_actual_medidas,
            'consumo_historico_promedio': round(consumo_hist, 1),
            'proyeccion_necesaria': round(botellas_necesarias, 1),
            'botellas_a_comprar': botellas_a_comprar,
            'costo_estimado': round(
                botellas_a_comprar * float(producto.precio_costo), 2
            ),
        })

    recomendaciones.sort(key=lambda x: x['botellas_a_comprar'], reverse=True)
    return recomendaciones