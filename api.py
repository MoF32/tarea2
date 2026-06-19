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
    # Las paredes gruesas afectan mucho más a las frecuencias altas (5 y 6 GHz)
    if banda == '2.4 GHz':
        p_fina, p_gruesa = 3, 8
    elif banda == '5 GHz':
        p_fina, p_gruesa = 5, 15
    else: # 6 GHz
        p_fina, p_gruesa = 7, 20

    rssi -= (paredes_finas * p_fina) + (paredes_gruesas * p_gruesa)

    # Límites físicos del RSSI
    if rssi > -30: rssi = -30
    if rssi < -90: rssi = -90

    # EFICIENCIA DE LA SEÑAL
    eficiencia_senal = 0.0
    if rssi >= -50:
        eficiencia_senal = 1.0
    elif rssi > -90:
        eficiencia_senal = (rssi - (-90)) / (-50 - (-90))

    # VELOCIDAD REAL
    velocidad_base = gen_props['max_speed'] * eficiencia_senal
    factor_congestion = 1.0
    if congestion == 'Media': factor_congestion = 0.65
    elif congestion == 'Alta': factor_congestion = 0.30

    velocidad_final = velocidad_base * factor_congestion

    # Penalizaciones extremas por señal baja
    if rssi <= -85: velocidad_final *= 0.1
    if rssi <= -89: velocidad_final = 0.0

    # LATENCIA
    latencia_final = float(gen_props['base_latency'])
    if eficiencia_senal < 0.8:
        latencia_final += (1.0 - eficiencia_senal) * 80

    if congestion == 'Media': latencia_final += 15
    elif congestion == 'Alta': latencia_final += 60
    if velocidad_final == 0.0: latencia_final = float('inf')

    # ESTADO GENERAL
    estado = 'Excelente'
    if rssi < -55: estado = 'Buena'
    if rssi < -70: estado = 'Regular'
    if rssi < -82: estado = 'Mala'
    if velocidad_final == 0.0: estado = 'Desconectado'

    return {
        'rssi': round(rssi),
        'velocidad_mbps': round(velocidad_final),
        'latencia_ms': '∞' if math.isinf(latencia_final) else round(latencia_final),
        'estado': estado
    }

# ==========================================
# INTERFAZ DE USUARIO (STREAMLIT)
# ==========================================

st.set_page_config(page_title="Simulador de Rendimiento Wi-Fi", page_icon="📶", layout="centered")

st.title("📶 Simulador de Rendimiento Wi-Fi")
st.markdown("Ajusta los parámetros para observar cómo el entorno afecta tu conexión.")

# Controles en la barra lateral
st.sidebar.header("⚙️ Parámetros de Simulación")

gen_seleccionada = st.sidebar.selectbox("Generación Wi-Fi", ['Wi-Fi 4', 'Wi-Fi 5', 'Wi-Fi 6', 'Wi-Fi 7'], index=2)
banda_seleccionada = st.sidebar.radio("Banda de Frecuencia", ['2.4 GHz', '5 GHz', '6 GHz'], index=1)
distancia_m = st.sidebar.slider("Distancia al Router (metros)", 1, 50, 12)

st.sidebar.subheader("Obstáculos (Paredes)")
p_finas = st.sidebar.slider("Paredes Finas (Tabique/Madera)", 0, 5, 1)
p_gruesas = st.sidebar.slider("Paredes Gruesas (Concreto/Ladrillo)", 0, 5, 1)

congestion_red = st.sidebar.select_slider("Congestión de la Red", options=['Baja', 'Media', 'Alta'], value='Baja')

# Diccionario de entrada
datos_entrada = {
    'generacion': gen_seleccionada,
    'banda': banda_seleccionada,
    'distancia': distancia_m,
    'paredes_finas': p_finas,
    'paredes_gruesas': p_gruesas,
    'congestion': congestion_red
}

resultados = calcular_simulacion_wifi(datos_entrada)

# --- EXPLICACIÓN DE PARÁMETROS ---
with st.expander("⚙️ ¿Qué significan los parámetros de simulación?"):
    st.markdown(f"""
    * **Generación Wi-Fi:** Estándar tecnológico. Las versiones superiores (6 y 7) gestionan mejor la pérdida de datos.
    * **Banda de Frecuencia:** La frecuencia 2.4 GHz tieimport streamlit as st
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
    if rssi > -30: rssi = -30
    if rssi < -90: rssi = -90

    # EFICIENCIA DE LA SEÑAL
    eficiencia_senal = 0.0
    if rssi >= -50:
        eficiencia_senal = 1.0
    elif rssi > -90:
        eficiencia_senal = (rssi - (-90)) / (-50 - (-90))

    # VELOCIDAD REAL
    velocidad_base = gen_props['max_speed'] * eficiencia_senal
    factor_congestion = 1.0
    if congestion == 'Media': factor_congestion = 0.65
    elif congestion == 'Alta': factor_congestion = 0.30

    velocidad_final = velocidad_base * factor_congestion

    # Penalizaciones extremas por señal baja
    if rssi <= -85: velocidad_final *= 0.1
    if rssi <= -89: velocidad_final = 0.0

    # LATENCIA
    latencia_final = float(gen_props['base_latency'])
    if eficiencia_senal < 0.8:
        latencia_final += (1.0 - eficiencia_senal) * 80

    if congestion == 'Media': latencia_final += 15
    elif congestion == 'Alta': latencia_final += 60
    if velocidad_final == 0.0: latencia_final = float('inf')

    # ESTADO GENERAL
    estado = 'Excelente'
    if rssi < -55: estado = 'Buena'
    if rssi < -70: estado = 'Regular'
    if rssi < -82: estado = 'Mala'
    if velocidad_final == 0.0: estado = 'Desconectado'

    return {
        'rssi': round(rssi),
        'velocidad_mbps': round(velocidad_final),
        'latencia_ms': '∞' if math.isinf(latencia_final) else round(latencia_final),
        'estado': estado
    }

# ==========================================
# INTERFAZ DE USUARIO (STREAMLIT)
# ==========================================

st.set_page_config(page_title="Simulador de Rendimiento Wi-Fi", page_icon="📶", layout="centered")

st.title("📶 Simulador de Rendimiento Wi-Fi")
st.markdown("Ajusta los parámetros para observar cómo el entorno afecta tu conexión.")

# Controles en la barra lateral
st.sidebar.header("⚙️ Parámetros de Simulación")

gen_seleccionada = st.sidebar.selectbox("Generación Wi-Fi", ['Wi-Fi 4', 'Wi-Fi 5', 'Wi-Fi 6', 'Wi-Fi 7'], index=2)
banda_seleccionada = st.sidebar.radio("Banda de Frecuencia", ['2.4 GHz', '5 GHz', '6 GHz'], index=1)
distancia_m = st.sidebar.slider("Distancia al Router (metros)", 1, 50, 12)

st.sidebar.subheader("Obstáculos (Paredes)")
p_finas = st.sidebar.slider("Paredes Finas (Tabique/Madera)", 0, 5, 1)
p_gruesas = st.sidebar.slider("Paredes Gruesas (Concreto/Ladrillo)", 0, 5, 1)

congestion_red = st.sidebar.select_slider("Congestión de la Red", options=['Baja', 'Media', 'Alta'], value='Baja')

# Diccionario de entrada
datos_entrada = {
    'generacion': gen_seleccionada,
    'banda': banda_seleccionada,
    'distancia': distancia_m,
    'paredes_finas': p_finas,
    'paredes_gruesas': p_gruesas,
    'congestion': congestion_red
}

resultados = calcular_simulacion_wifi(datos_entrada)

# --- EX
