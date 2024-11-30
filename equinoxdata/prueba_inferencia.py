import numpy as np
import skfuzzy as fuzz

# Funciones de membresía para Aforo
def aforo_bajo(aforo):
    aforo = np.array([aforo])  # Convertir a arreglo
    return fuzz.trapmf(aforo, [0, 0, 50, 150])[0]

def aforo_medio(aforo):
    aforo = np.array([aforo])  # Convertir a arreglo
    return fuzz.trimf(aforo, [50, 150, 250])[0]

def aforo_alto(aforo):
    aforo = np.array([aforo])  # Convertir a arreglo
    return fuzz.trapmf(aforo, [150, 250, 300, 300])[0]

# Funciones de membresía para Ventas
def ventas_bajo(ventas):
    ventas = np.array([ventas])  # Convertir a arreglo
    return fuzz.trapmf(ventas, [2000, 2000, 7000, 10000])[0]

def ventas_medio(ventas):
    ventas = np.array([ventas])  # Convertir a arreglo
    return fuzz.trimf(ventas, [7000, 12000, 15000])[0]

def ventas_alto(ventas):
    ventas = np.array([ventas])  # Convertir a arreglo
    return fuzz.trapmf(ventas, [12000, 15000, 20000, 20000])[0]

# Funciones de membresía para Consumo
def consumo_bajo(consumo):
    consumo = np.array([consumo])  # Convertir a arreglo
    return fuzz.trapmf(consumo, [30, 30, 70, 100])[0]

def consumo_medio(consumo):
    consumo = np.array([consumo])  # Convertir a arreglo
    return fuzz.trimf(consumo, [70, 100, 150])[0]

def consumo_alto(consumo):
    consumo = np.array([consumo])  # Convertir a arreglo
    return fuzz.trapmf(consumo, [100, 150, 200, 200])[0]

# Función para inferir las reglas
def reglas_inferencia(aforo, ventas, consumo):
    # Aplicar las funciones de membresía
    grado_aforo_bajo = aforo_bajo(aforo)
    grado_aforo_medio = aforo_medio(aforo)
    grado_aforo_alto = aforo_alto(aforo)

    grado_ventas_bajo = ventas_bajo(ventas)
    grado_ventas_medio = ventas_medio(ventas)
    grado_ventas_alto = ventas_alto(ventas)

    grado_consumo_bajo = consumo_bajo(consumo)
    grado_consumo_medio = consumo_medio(consumo)
    grado_consumo_alto = consumo_alto(consumo)

    # Definir las reglas (todas las combinaciones posibles)
    reglas = [
        (min(grado_aforo_bajo, grado_ventas_bajo, grado_consumo_bajo), 10),   # Baja Baja Baja
        (min(grado_aforo_bajo, grado_ventas_bajo, grado_consumo_medio), 20),   # Baja Baja Media
        (min(grado_aforo_bajo, grado_ventas_bajo, grado_consumo_alto), 30),    # Baja Baja Alta
        (min(grado_aforo_bajo, grado_ventas_medio, grado_consumo_bajo), 20),   # Baja Media Baja
        (min(grado_aforo_bajo, grado_ventas_medio, grado_consumo_medio), 40),  # Baja Media Media
        (min(grado_aforo_bajo, grado_ventas_medio, grado_consumo_alto), 50),   # Baja Media Alta
        (min(grado_aforo_bajo, grado_ventas_alto, grado_consumo_bajo), 30),    # Baja Alta Baja
        (min(grado_aforo_bajo, grado_ventas_alto, grado_consumo_medio), 60),   # Baja Alta Media
        (min(grado_aforo_bajo, grado_ventas_alto, grado_consumo_alto), 70),    # Baja Alta Alta

        (min(grado_aforo_medio, grado_ventas_bajo, grado_consumo_bajo), 20),   # Media Baja Baja
        (min(grado_aforo_medio, grado_ventas_bajo, grado_consumo_medio), 40),  # Media Baja Media
        (min(grado_aforo_medio, grado_ventas_bajo, grado_consumo_alto), 50),   # Media Baja Alta
        (min(grado_aforo_medio, grado_ventas_medio, grado_consumo_bajo), 30),  # Media Media Baja
        (min(grado_aforo_medio, grado_ventas_medio, grado_consumo_medio), 60), # Media Media Media
        (min(grado_aforo_medio, grado_ventas_medio, grado_consumo_alto), 80),  # Media Media Alta
        (min(grado_aforo_medio, grado_ventas_alto, grado_consumo_bajo), 50),   # Media Alta Baja
        (min(grado_aforo_medio, grado_ventas_alto, grado_consumo_medio), 90),  # Media Alta Media
        (min(grado_aforo_medio, grado_ventas_alto, grado_consumo_alto), 100),  # Media Alta Alta

        (min(grado_aforo_alto, grado_ventas_bajo, grado_consumo_bajo), 30),    # Alta Baja Baja
        (min(grado_aforo_alto, grado_ventas_bajo, grado_consumo_medio), 50),   # Alta Baja Media
        (min(grado_aforo_alto, grado_ventas_bajo, grado_consumo_alto), 60),    # Alta Baja Alta
        (min(grado_aforo_alto, grado_ventas_medio, grado_consumo_bajo), 40),   # Alta Media Baja
        (min(grado_aforo_alto, grado_ventas_medio, grado_consumo_medio), 70),  # Alta Media Media
        (min(grado_aforo_alto, grado_ventas_medio, grado_consumo_alto), 90),   # Alta Media Alta
        (min(grado_aforo_alto, grado_ventas_alto, grado_consumo_bajo), 50),    # Alta Alta Baja
        (min(grado_aforo_alto, grado_ventas_alto, grado_consumo_medio), 80),   # Alta Alta Media
        (min(grado_aforo_alto, grado_ventas_alto, grado_consumo_alto), 100),   # Alta Alta Alta
    ]

    # Inferencia: Promedio ponderado de todas las reglas
    salida_total = sum([w * s for w, s in reglas]) / sum([w for w, s in reglas])

    return salida_total

# Probar con un ejemplo
aforo_test = 250
ventas_test = 15000
consumo_test = 120

recomendacion = reglas_inferencia(aforo_test, ventas_test, consumo_test)
print(f'Recomendación de cantidad de productos: {recomendacion}')
