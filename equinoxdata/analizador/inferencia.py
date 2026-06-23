import numpy as np
import skfuzzy as fuzz


# ------------------------------------------------------------------
# Funciones de membresía para Aforo (0 - 300 personas)
# ------------------------------------------------------------------

def aforo_bajo(aforo):
    return fuzz.trapmf(np.array([aforo]), [0, 0, 50, 150])[0]

def aforo_medio(aforo):
    return fuzz.trimf(np.array([aforo]), [50, 150, 250])[0]

def aforo_alto(aforo):
    return fuzz.trapmf(np.array([aforo]), [150, 250, 300, 300])[0]


# ------------------------------------------------------------------
# Funciones de membresía para Ventas esperadas (2000 - 20000 Bs)
# ------------------------------------------------------------------

def ventas_bajo(ventas):
    return fuzz.trapmf(np.array([ventas]), [2000, 2000, 7000, 10000])[0]

def ventas_medio(ventas):
    return fuzz.trimf(np.array([ventas]), [7000, 12000, 15000])[0]

def ventas_alto(ventas):
    return fuzz.trapmf(np.array([ventas]), [12000, 15000, 20000, 20000])[0]


# ------------------------------------------------------------------
# Funciones de membresía para Consumo per cápita (30 - 200 Bs/persona)
# ------------------------------------------------------------------

def consumo_bajo(consumo):
    return fuzz.trapmf(np.array([consumo]), [30, 30, 70, 100])[0]

def consumo_medio(consumo):
    return fuzz.trimf(np.array([consumo]), [70, 100, 150])[0]

def consumo_alto(consumo):
    return fuzz.trapmf(np.array([consumo]), [100, 150, 200, 200])[0]


# ------------------------------------------------------------------
# Motor de inferencia Takagi-Sugeno
# Retorna el coeficiente de reabastecimiento (0-100%)
# ------------------------------------------------------------------

def reglas_inferencia(aforo, ventas, consumo):
    """
    Calcula el coeficiente de reabastecimiento usando lógica difusa.
    
    El coeficiente representa qué porcentaje del stock máximo estimado
    debe adquirirse para el evento. Ej: 80% = adquirir el 80% del stock
    proyectado según los parámetros del evento.
    
    Returns:
        float: Coeficiente entre 0 y 100
    """
    # Calcular grados de membresía
    ga_b = aforo_bajo(aforo)
    ga_m = aforo_medio(aforo)
    ga_a = aforo_alto(aforo)

    gv_b = ventas_bajo(ventas)
    gv_m = ventas_medio(ventas)
    gv_a = ventas_alto(ventas)

    gc_b = consumo_bajo(consumo)
    gc_m = consumo_medio(consumo)
    gc_a = consumo_alto(consumo)

    # 27 reglas: (peso, salida)
    # La salida es el coeficiente de reabastecimiento para esa combinación
    reglas = [
        # Aforo BAJO
        (min(ga_b, gv_b, gc_b), 10),
        (min(ga_b, gv_b, gc_m), 20),
        (min(ga_b, gv_b, gc_a), 30),
        (min(ga_b, gv_m, gc_b), 20),
        (min(ga_b, gv_m, gc_m), 40),
        (min(ga_b, gv_m, gc_a), 50),
        (min(ga_b, gv_a, gc_b), 30),
        (min(ga_b, gv_a, gc_m), 60),
        (min(ga_b, gv_a, gc_a), 70),
        # Aforo MEDIO
        (min(ga_m, gv_b, gc_b), 20),
        (min(ga_m, gv_b, gc_m), 40),
        (min(ga_m, gv_b, gc_a), 50),
        (min(ga_m, gv_m, gc_b), 30),
        (min(ga_m, gv_m, gc_m), 60),
        (min(ga_m, gv_m, gc_a), 80),
        (min(ga_m, gv_a, gc_b), 50),
        (min(ga_m, gv_a, gc_m), 90),
        (min(ga_m, gv_a, gc_a), 100),
        # Aforo ALTO
        (min(ga_a, gv_b, gc_b), 30),
        (min(ga_a, gv_b, gc_m), 50),
        (min(ga_a, gv_b, gc_a), 60),
        (min(ga_a, gv_m, gc_b), 40),
        (min(ga_a, gv_m, gc_m), 70),
        (min(ga_a, gv_m, gc_a), 90),
        (min(ga_a, gv_a, gc_b), 50),
        (min(ga_a, gv_a, gc_m), 80),
        (min(ga_a, gv_a, gc_a), 100),
    ]

    peso_total = sum(w for w, s in reglas)
    if peso_total == 0:
        return 0.0

    salida = sum(w * s for w, s in reglas) / peso_total
    return round(float(salida), 2)