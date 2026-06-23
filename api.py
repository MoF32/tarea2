import streamlit as st
import math

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Simulador de Rendimiento Wi-Fi", page_icon="📶", layout="centered")
st.title("📶 Simulador de Rendimiento Wi-Fi")
st.markdown("Ajusta los parámetros para observar cómo el entorno afecta tu conexión.")

# 1. ENTRADAS DE USUARIO
st.sidebar.header("⚙️ Parámetros de Simulación")
gen_sel = st.sidebar.selectbox("Generación Wi-Fi", ['Wi-Fi 4', 'Wi-Fi 5', 'Wi-Fi 6', 'Wi-Fi 7'], index=2)
banda_sel = st.sidebar.radio("Banda de Frecuencia", ['2.4 GHz', '5 GHz', '6 GHz'], index=1)
distancia_m = st.sidebar.slider("Distancia al Router (metros)", 1, 50, 12)

st.sidebar.subheader("Obstáculos (Paredes)")
tipo_pared_sel = st.sidebar.selectbox("Tipo de Pared", ['Fina (Tabique/Madera)', 'Gruesa (Concreto/Ladrillo)'])
cantidad_paredes_sel = st.sidebar.slider("Cantidad de Paredes", 0, 5, 1)
congestion_red = st.sidebar.select_slider("Congestión de la Red", options=['Baja', 'Media', 'Alta'], value='Baja')

# 2. PROCESAMIENTO Y CÁLCULOS (ESTRICTAMENTE LINEALES)
limites_generacion = {
    'Wi-Fi 4': {'max_speed': 150, 'base_latency': 25}, 'Wi-Fi 5': {'max_speed': 866, 'base_latency': 12},
    'Wi-Fi 6': {'max_speed': 1201, 'base_latency': 6}, 'Wi-Fi 7': {'max_speed': 2402, 'base_latency': 2}
}
# props_bandas: [Pérdida lineal en dB por metro, Atenuación Fina, Atenuación Gruesa]
props_bandas = { 
    '2.4 GHz': [0.8, 3, 8], 
    '5 GHz':   [1.1, 5, 15], 
    '6 GHz':   [1.3, 7, 20]
}
factores_congestion = {'Baja': [1.0, 0], 'Media': [0.65, 15], 'Alta': [0.30, 60]}

gen_props = limites_generacion[gen_sel]
f_dist_lineal, p_fina, p_gruesa = props_bandas[banda_sel]
f_cong, lat_cong = factores_congestion[congestion_red]

# Cálculo de RSSI usando una Función Lineal: RSSI = -30 - (Pérdida_Metro * Metros) - Obstáculos
coef_pared = p_fina if tipo_pared_sel == 'Fina (Tabique/Madera)' else p_gruesa
pérdida_total_obstaculos = cantidad_paredes_sel * coef_pared
pérdida_total_distancia = (distancia_m - 1) * f_dist_lineal

rssi = -30 - pérdida_total_distancia - pérdida_total_obstaculos
rssi = max(-90, min(-30, rssi))  # Acotación por límites físicos transmisor/receptor

# Eficiencia de señal (Mapeo de función lineal continua entre -90 y -50 dBm)
eficiencia_senal = max(0.0, (rssi - (-90)) / 40) if rssi < -50 else 1.0

# Velocidad Final (Función lineal aditiva y multiplicativa directa)
velocidad_final = gen_props['max_speed'] * eficiencia_senal * f_cong

# Latencia Final (Función lineal inversa respecto a la eficiencia de señal)
if velocidad_final == 0:
    latencia_final = float('inf')
else:
    latencia_final = max(0, gen_props['base_latency'] + (1.0 - eficiencia_senal) * 80 + lat_cong)
latencia_texto = '∞' if math.isinf(latencia_final) else round(latencia_final)

# Determinación de Estados por umbrales lineales
estados = [(-55, 'Excelente'), (-70, 'Buena'), (-82, 'Regular'), (-89, 'Mala')]
estado = next((est for lim, est in estados if rssi >= lim), 'Desconectado')
if velocidad_final == 0: estado = 'Desconectado'

# 3. INTERFAZ DE SALIDA (LOGICA VISUAL)
with st.expander("⚙️ ¿Qué significan los parámetros de simulación?"):
    st.markdown(" * **Generación:** Estándar de tecnología.\n * **Frecuencia:** Coeficiente de atenuación lineal variable.\n * **Paredes:** Modificadores lineales directos.")

st.markdown("---")
st.subheader("📊 Resultados del Diagnóstico")
col1, col2, col3 = st.columns(3)
col1.metric("Intensidad (RSSI)", f"{round(rssi)} dBm")
col2.metric("Velocidad Real", f"{round(velocidad_final)} Mbps")
col3.metric("Latencia (Ping)", f"{latencia_texto} ms")

with st.expander("🔍 ¿Qué significan estos resultados?"):
    st.markdown("""
    * **Intensidad (RSSI):** Indica qué tan "fuerte" llega la señal. De -30 a -50 es ideal. Por debajo de -80 la conexión es inestable.
    * **Velocidad Real:** Lo que realmente puedes navegar después de restar pérdidas físicas e interferencias.
    * **Latencia (Ping):** El retraso en milisegundos. Un ping alto hace que la navegación se sienta "pesada" o con lag.
    """)
st.markdown("---")
st.subheader("📢 Estado de la Conexión")
alertas = {
    'Excelente': (st.success, "🟢 **Conexión Excelente**: Máximo rendimiento disponible."),
    'Buena': (st.info, "🔵 **Conexión Buena**: Funcionamiento óptimo para casi todo."),
    'Regular': (st.warning, "🟡 **Conexión Regular**: Posibles micro-cortes o lentitud."),
    'Mala': (st.error, "🟠 **Conexión Mala**: Señal crítica. Se recomienda repetidor."),
    'Desconectado': (st.error, "🔴 **Desconectado**: Sin comunicación con el router.")
}
mostrar_alerta, texto_alerta = alertas[estado]
mostrar_alerta(texto_alerta)

# RECOMENDACIONES DINÁMICAS
st.markdown("---")
st.subheader("🛠️ Recomendaciones de Optimización")

if estado in ['Excelente', 'Buena']:
    st.balloons()
    st.success("✨ **¡Tu configuración actual es ideal!** No requieres cambios físicos.")
else:
    st.markdown("Basado en tu diagnóstico:")
    if distancia_m > 20 or cantidad_paredes_sel >= 2:
        st.markdown("* **📍 Ubicación:** Aleja obstáculos o evalúa instalar un sistema **Wi-Fi Mesh**.")
    if banda_sel in ['5 GHz', '6 GHz'] and estado in ['Mala', 'Desconectado']:
        st.markdown("* **🔄 Cobertura:** Forzar conexión a banda **2.4 GHz** para atravesar muros.")
    elif banda_sel == '2.4 GHz' and congestion_red in ['Media', 'Alta']:
        st.markdown("* **🚀 Saturación:** Cambia a la banda de **5 GHz/6 GHz** para evitar congestión.")
    if gen_sel in ['Wi-Fi 4', 'Wi-Fi 5']:
        st.markdown("* **🏷️ Tecnología:** Un salto a **Wi-Fi 6 / 7** gestionará mejor la pérdida de paquetes.")
    if congestion_red == 'Alta' and estado == 'Regular':
        st.markdown("* **🌐 Canales:** Cambia el canal de transmisión desde el router por uno libre.")
    if estado == 'Desconectado':
        st.markdown("* **🔌 Bloqueo:** Usa cable **Ethernet** o adaptadores **PLC (Powerline)**.")

st.markdown("---")
st.info("💡 **Nota sobre el Internet:** Mide el rendimiento de transmisión local inalámbrica. La velocidad real externa estará topada por el plan que pagues a tu proveedor.")
