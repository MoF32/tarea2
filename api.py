import streamlit as st
import math

# 1. Función de simulación con lógica de paredes diferenciada
def calcular_simulacion_wifi(input_data):
    limites_generacion = {
        'Wi-Fi 4': {'max_speed': 150, 'base_latency': 25},
        'Wi-Fi 5': {'max_speed': 866, 'base_latency': 12},
        'Wi-Fi 6': {'max_speed': 1201, 'base_latency': 6},
        'Wi-Fi 7': {'max_speed': 2402, 'base_latency': 2}
    }

    generacion = input_data.get('generacion', 'Wi-Fi 6')
    banda = input_data.get('banda', '5 GHz')
    distancia = input_data.get('distancia', 1)
    paredes_finas = input_data.get('paredes_finas', 0)
    paredes_gruesas = input_data.get('paredes_gruesas', 0)
    congestion = input_data.get('congestion', 'Baja')

    gen_props = limites_generacion.get(generacion, limites_generacion['Wi-Fi 6'])

    # CÁLCULO DE RSSI (Potencia de señal)
    rssi = -30
    factor_distancia = 20 if banda == '2.4 GHz' else (23 if banda == '5 GHz' else 25)

    if distancia > 1:
        rssi -= factor_distancia * math.log10(distancia)

    # Coeficientes de pérdida por tipo de pared y banda
    if banda == '2.4 GHz':
        p_fina, p_gruesa = 3, 8
    elif banda == '5 GHz':
        p_fina, p_gruesa = 5, 15
    else: # 6 GHz
        p_fina, p_gruesa = 7, 20

    rssi -= (paredes_finas * p_fina) + (paredes_gruesas * p_gruesa)

    # Límites físicos del RSSI
    if rssi
