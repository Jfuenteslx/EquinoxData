# inferencia.py

from django.shortcuts import render
from .forms import ParametrosForm  # Formulario que crearemos para recibir los datos
from .models import Parametro
import numpy as np
import skfuzzy as fuzz

def aforo_bajo(aforo):
    aforo = np.array([aforo])
    resultado = fuzz.trapmf(aforo, [0, 0, 50, 150])[0]
    print(f"aforo_bajo({aforo}): {resultado}")
    return resultado

def aforo_medio(aforo):
    aforo = np.array([aforo])
    resultado = fuzz.trimf(aforo, [50, 150, 250])[0]
    print(f"aforo_medio({aforo}): {resultado}")
    return resultado

def aforo_alto(aforo):
    aforo = np.array([aforo])
    resultado = fuzz.trapmf(aforo, [150, 250, 300, 300])[0]
    print(f"aforo_alto({aforo}): {resultado}")
    return resultado

# Funciones de membresía para Ventas
def ventas_bajo(ventas):
    ventas = np.array([ventas])
    resultado = fuzz.trapmf(ventas, [2000, 2000, 7000, 10000])[0]
    print(f"ventas_bajo({ventas}): {resultado}")
    return resultado

def ventas_medio(ventas):
    ventas = np.array([ventas])
    resultado = fuzz.trimf(ventas, [7000, 12000, 15000])[0]
    print(f"ventas_medio({ventas}): {resultado}")
    return resultado

def ventas_alto(ventas):
    ventas = np.array([ventas])
    resultado = fuzz.trapmf(ventas, [12000, 15000, 20000, 20000])[0]
    print(f"ventas_alto({ventas}): {resultado}")
    return resultado

# Funciones de membresía para Consumo
def consumo_bajo(consumo):
    consumo = np.array([consumo])
    resultado = fuzz.trapmf(consumo, [30, 30, 70, 100])[0]
    print(f"consumo_bajo({consumo}): {resultado}")
    return resultado

def consumo_medio(consumo):
    consumo = np.array([consumo])
    resultado = fuzz.trimf(consumo, [70, 100, 150])[0]
    print(f"consumo_medio({consumo}): {resultado}")
    return resultado

def consumo_alto(consumo):
    consumo = np.array([consumo])
    resultado = fuzz.trapmf(consumo, [100, 150, 200, 200])[0]
    print(f"consumo_alto({consumo}): {resultado}")
    return resultado

# Función de inferencia
def reglas_inferencia(aforo, ventas, consumo):
    print(f"Calculando con aforo={aforo}, ventas={ventas}, consumo={consumo}")
    
    grado_aforo_bajo = aforo_bajo(aforo)
    grado_aforo_medio = aforo_medio(aforo)
    grado_aforo_alto = aforo_alto(aforo)

    grado_ventas_bajo = ventas_bajo(ventas)
    grado_ventas_medio = ventas_medio(ventas)
    grado_ventas_alto = ventas_alto(ventas)

    grado_consumo_bajo = consumo_bajo(consumo)
    grado_consumo_medio = consumo_medio(consumo)
    grado_consumo_alto = consumo_alto(consumo)

    # Comprobamos los valores de los grados de membresía
    print(f"Grados de membresía:")
    print(f"  Aforo: bajo={grado_aforo_bajo}, medio={grado_aforo_medio}, alto={grado_aforo_alto}")
    print(f"  Ventas: bajo={grado_ventas_bajo}, medio={grado_ventas_medio}, alto={grado_ventas_alto}")
    print(f"  Consumo: bajo={grado_consumo_bajo}, medio={grado_consumo_medio}, alto={grado_consumo_alto}")

    # Regla de inferencia (ejemplo, ajustar según necesidades)
    reglas = [
        (min(grado_aforo_bajo, grado_ventas_bajo, grado_consumo_bajo), 10),
        (min(grado_aforo_bajo, grado_ventas_bajo, grado_consumo_medio), 20),
        (min(grado_aforo_bajo, grado_ventas_bajo, grado_consumo_alto), 30),
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
    

    # Comprobamos los valores de las reglas
    print(f"Reglas aplicadas:")
    for i, (w, s) in enumerate(reglas):
        print(f"  Regla {i+1}: peso={w}, salida={s}")

    # Cálculo del valor ponderado
    if sum([w for w, s in reglas]) != 0:
        salida_total = sum([w * s for w, s in reglas]) / sum([w for w, s in reglas])
    else:
        salida_total = 0
    
    print(f"Salida total (valor recomendado): {salida_total}")
    
    # Asegurarse de que la salida sea un número y no un array
    return float(salida_total)  # Convertir a número flotante
