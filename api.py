import streamlit as st
import math

# 1. Definición de la función de simulación (lógica original)
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
    paredes = input_data.get('paredes', 0)
    congestion = input_data.get('congestion', 'Baja')

    gen_props = limites_generacion.get(generacion, limites_generacion['Wi-Fi 6'])

    # CÁLCULO DE RSSI
    rssi = -30
    factor_distancia = 20 if banda == '2.4 GHz' else (23 if banda == '5 GHz' else 25)

    if distancia > 1:
        rssi -= factor_distancia * math.log10(distancia)

    perdida_por_pared = 6 if banda == '2.4 GHz' else (12 if banda == '5 GHz' else 15)
    rssi -= (paredes * perdida_por_pared)

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
    if congestion == 'Media':
        factor_congestion = 0.65
    elif congestion == 'Alta':
        factor_congestion = 0.30

    velocidad_final = velocidad_base * factor_congestion

    if rssi <= -85: velocidad_final *= 0.1
    if rssi <= -89: velocidad_final = 0.0

    # LATENCIA
    latencia_final = float(gen_props['base_latency'])
    if eficiencia_senal < 0.8:
        latencia_final += (1.0 - eficiencia_senal) * 80

    if congestion == 'Media':
        latencia_final += 15
    elif congestion == 'Alta':
        latencia_final += 60

    if velocidad_final == 0.0:
        latencia_final = float('inf')

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
st.markdown("Ajusta los parámetros en la barra lateral para ver cómo afectan la calidad de tu conexión en tiempo real.")

# Controles en la barra lateral
st.sidebar.header("⚙️ Parámetros de Simulación")

gen_seleccionada = st.sidebar.selectbox("Generación Wi-Fi", ['Wi-Fi 4', 'Wi-Fi 5', 'Wi-Fi 6', 'Wi-Fi 7'], index=2)
banda_seleccionada = st.sidebar.radio("Banda de Frecuencia", ['2.4 GHz', '5 GHz', '6 GHz'], index=1)
distancia_m = st.sidebar.slider("Distancia al Router (metros)", min_value=1, max_value=50, value=12)
num_paredes = st.sidebar.slider("Paredes de concreto intermedias", min_value=0, max_value=5, value=2)
congestion_red = st.sidebar.select_slider("Congestión de la Red", options=['Baja', 'Media', 'Alta'], value='Alta')

# Crear el diccionario de entrada para la función
datos_entrada = {
    'generacion': gen_seleccionada,
    'banda': banda_seleccionada,
    'distancia': distancia_m,
    'paredes': num_paredes,
    'congestion': congestion_red
}

# Ejecutar la simulación automáticamente al mover los controles
resultados = calcular_simulacion_wifi(datos_entrada)

# Mostrar resultados principales en métricas atractivas
st.subheader("📊 Resultados del Diagnóstico")

col1, col2, col3 = st.columns(3)
col1.metric(label="Intensidad (RSSI)", value=f"{resultados['rssi']} dBm")
col2.metric(label="Velocidad Real", value=f"{resultados['velocidad_mbps']} Mbps")
col3.metric(label="Latencia (Ping)", value=f"{resultados['latencia_ms']} ms")

# --- EXPLICACIÓN VISIBLE DIRECTAMENTE EN LA APP ---
st.markdown("#### 🔍 Entendiendo las métricas:")

exp_col1, exp_col2, exp_col3 = st.columns(3)

with exp_col1:
    st.caption("**Intensidad (RSSI):**")
    st.markdown("<small>Potencia de la señal. Al ser valores negativos, <b>más cerca de 0 es mejor</b> (-30 dBm es ideal, -90 dBm es desconexión).</small>", unsafe_allow_html=True)

with exp_col2:
    st.caption("**Velocidad Real:**")
    st.markdown("<small>Ancho de banda efectivo (Mbps) para transferir datos. Disminuye por la distancia, muros y congestión de la red.</small>", unsafe_allow_html=True)

with exp_col3:
    st.caption("**Latencia (Ping):**")
    st.markdown("<small>Tiempo de respuesta (ms) del router. <b>Menor es mejor</b>. Si la señal es baja, aumenta por retransmisión de paquetes.</small>", unsafe_allow_html=True)

st.markdown("---")

# Alertas visuales según el estado de la conexión
st.subheader("📢 Estado de la Conexión")
estado = resultados['estado']

if estado == 'Excelente':
    st.success(f"🟢 **Conexión {estado}**: Ideal para streaming 4K/8K, gaming competitivo y descargas masivas sin interrupciones.")
elif estado == 'Buena':
    st.info(f"🔵 **Conexión {estado}**: Rendimiento fluido para la mayoría de tareas diarias y vide
