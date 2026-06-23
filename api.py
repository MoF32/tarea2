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

# 2. PROCESAMIENTO Y CÁLCULOS DICCIONARIOS (SIMPLIFICACIÓN)
limites_generacion = {
    'Wi-Fi 4': {'max_speed': 150, 'base_latency': 25}, 'Wi-Fi 5': {'max_speed': 866, 'base_latency': 12},
    'Wi-Fi 6': {'max_speed': 1201, 'base_latency': 6}, 'Wi-Fi 7': {'max_speed': 2402, 'base_latency': 2}
}
props_bandas = { # [Factor Distancia, Atenuación Fina, Atenuación Gruesa]
    '2.4 GHz': [20, 3, 8], '5 GHz': [23, 5, 15], '6 GHz': [25, 7, 20]
}
factores_congestion = {'Baja': [1.0, 0], 'Media': [0.65, 15], 'Alta': [0.30, 60]}

gen_props = limites_generacion[gen_sel]
f_dist, p_fina, p_gruesa = props_bandas[banda_sel]
f_cong, lat_cong = factores_congestion[congestion_red]

# Cálculo de RSSI
rssi = -30 - (f_dist * math.log10(distancia_m) if distancia_m > 1 else 0)
coef_pared = p_fina if tipo_pared_sel == 'Fina (Tabique/Madera)' else p_gruesa
rssi = max(-90, min(-30, rssi - (cantidad_paredes_sel * coef_pared)))

# Eficiencia y Penalizaciones
eficiencia_senal = max(0.0, (rssi - (-90)) / 40) if rssi < -50 else 1.0
velocidad_final = gen_props['max_speed'] * eficiencia_senal * f_cong
if rssi <= -85: velocidad_final *= 0.1 if rssi > -89 else 0.0

# Latencia y Estado
latencia_final = float('inf') if velocidad_final == 0 else max(0, gen_props['base_latency'] + (1.0 - eficiencia_senal) * 80 + lat_cong)
latencia_texto = '∞' if math.isinf(latencia_final) else round(latencia_final)

estados = [(-55, 'Excelente'), (-70, 'Buena'), (-82, 'Regular'), (-89, 'Mala')]
estado = next((est for lim, est in estados if rssi >= lim), 'Desconectado')
if velocidad_final == 0: estado = 'Desconectado'

# 3. INTERFAZ DE SALIDA (LOGICA VISUAL)
with st.expander("⚙️ ¿Qué significan los parámetros de simulación?"):
    st.markdown(" * **Generación:** Estándar de tecnología.\n * **Frecuencia:** 2.4 GHz penetra mejor; 5 y 6 GHz son veloces pero sensibles.\n * **Paredes:** Finas restan 3-7 dB; gruesas restan hasta 20 dB.")

st.markdown("---")
st.subheader("📊 Resultados del Diagnóstico")
col1, col2, col3 = st.columns(3)
col1.metric("Intensidad (RSSI)", f"{round(rssi)} dBm")
col2.metric("Velocidad Real", f"{round(velocidad_final)} Mbps")
col3.metric("Latencia (Ping)", f"{latencia_texto} ms")

with st.expander("🔍 ¿Qué significan estos resultados?"):
    st.markdown(" * **RSSI:** Ideal -30 a -50. Menos de -80 es inestable.\n * **Velocidad Real:** Navegación neta final.\n * **Latencia:** Retraso (ping).")

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
