import streamlit as st
import math

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Simulador de Rendimiento Wi-Fi", page_icon="📶", layout="centered")

st.title("📶 Simulador de Rendimiento Wi-Fi")
st.markdown("Ajusta los parámetros para observar cómo el entorno afecta tu conexión.")

# ==========================================
# 1. ENTRADAS DE USUARIO (CONTROLES EN LA BARRA LATERAL)
# ==========================================
st.sidebar.header("⚙️ Parámetros de Simulación")

gen_seleccionada = st.sidebar.selectbox("Generación Wi-Fi", ['Wi-Fi 4', 'Wi-Fi 5', 'Wi-Fi 6', 'Wi-Fi 7'], index=2)
banda_seleccionada = st.sidebar.radio("Banda de Frecuencia", ['2.4 GHz', '5 GHz', '6 GHz'], index=1)
distancia_m = st.sidebar.slider("Distancia al Router (metros)", 1, 50, 12)

st.sidebar.subheader("Obstáculos (Paredes)")
tipo_pared_sel = st.sidebar.selectbox("Tipo de Pared", ['Fina (Tabique/Madera)', 'Gruesa (Concreto/Ladrillo)'])
cantidad_paredes_sel = st.sidebar.slider("Cantidad de Paredes", 0, 5, 1)

congestion_red = st.sidebar.select_slider("Congestión de la Red", options=['Baja', 'Media', 'Alta'], value='Baja')

# ==========================================
# 2. PROCESAMIENTO Y CÁLCULOS (LÓGICA LINEAL)
# ==========================================

# Diccionario de propiedades tecnológicas
limites_generacion = {
    'Wi-Fi 4': {'max_speed': 150, 'base_latency': 25},
    'Wi-Fi 5': {'max_speed': 866, 'base_latency': 12},
    'Wi-Fi 6': {'max_speed': 1201, 'base_latency': 6},
    'Wi-Fi 7': {'max_speed': 2402, 'base_latency': 2}
}
gen_props = limites_generacion[gen_seleccionada]

# Cálculo inicial de RSSI (Potencia de señal base)
rssi = -30
factor_distancia = 20 if banda_seleccionada == '2.4 GHz' else (23 if banda_seleccionada == '5 GHz' else 25)

if distancia_m > 1:
    rssi -= factor_distancia * math.log10(distancia_m)

# Asignación de coeficientes de pérdida por tipo de pared y banda
if banda_seleccionada == '2.4 GHz':
    p_fina, p_gruesa = 3, 8
elif banda_seleccionada == '5 GHz':
    p_fina, p_gruesa = 5, 15
else:  # 6 GHz
    p_fina, p_gruesa = 7, 20

# Determinar coeficiente según la selección de la interfaz
coeficiente_pared = p_fina if tipo_pared_sel == 'Fina (Tabique/Madera)' else p_gruesa

# Aplicar la atenuación de los obstáculos al RSSI
rssi -= (cantidad_paredes_sel * coeficiente_pared)

# Acotar límites físicos del RSSI
if rssi > -30: 
    rssi = -30
if rssi < -90: 
    rssi = -90

# Cálculo de la Eficiencia de la Señal
eficiencia_senal = 0.0
if rssi >= -50:
    eficiencia_senal = 1.0
elif rssi > -90:
    eficiencia_senal = (rssi - (-90)) / (-50 - (-90))

# Cálculo de la Velocidad Real
velocidad_base = gen_props['max_speed'] * eficiencia_senal
factor_congestion = 1.0

if congestion_red == 'Media': 
    factor_congestion = 0.65
elif congestion_red == 'Alta': 
    factor_congestion = 0.30

velocidad_final = velocidad_base * factor_congestion

# Penalizaciones extremas por señal crítica
if rssi <= -85: 
    velocidad_final *= 0.1
if rssi <= -89: 
    velocidad_final = 0.0

# Cálculo de la Latencia
latencia_final = float(gen_props['base_latency'])
if eficiencia_senal < 0.8:
    latencia_final += (1.0 - eficiencia_senal) * 80

if congestion_red == 'Media': 
    latencia_final += 15
elif congestion_red == 'Alta': 
    latencia_final += 60
    
if velocidad_final == 0.0: 
    latencia_final = float('inf')

# Determinación del Estado General de la conexión
estado = 'Excelente'
if rssi < -55: estado = 'Buena'
if rssi < -70: estado = 'Regular'
if rssi < -82: estado = 'Mala'
if velocidad_final == 0.0: estado = 'Desconectado'

# Formatear el texto de la latencia para la interfaz gráfica
latencia_texto = '∞' if math.isinf(latencia_final) else round(latencia_final)

# ==========================================
# 3. INTERFAZ DE SALIDA (LOGICA VISUAL)
# ==========================================

# --- EXPLICACIÓN DE PARÁMETROS ---
with st.expander("⚙️ ¿Qué significan los parámetros de simulación?"):
    st.markdown("""
    * **Generación Wi-Fi:** Estándar tecnológico. Las versiones superiores (6 y 7) gestionan mejor la pérdida de datos.
    * **Banda de Frecuencia:** La frecuencia 2.4 GHz tiene mayor penetración en paredes pero menos velocidad. Las de 5 y 6 GHz son muy sensibles a obstáculos.
    * **Distancia:** A mayor distancia, la onda pierde energía naturalmente.
    * **Tipos de Pared:**
        * **Finas (Atenuación leve):** Materiales como drywall, madera o vidrio. Restan entre **3 y 7 dB**.
        * **Gruesas (Atenuación severa):** Concreto armado, ladrillo macizo o piedra. Pueden restar hasta **20 dB**, bloqueando casi por completo las bandas de 5/6 GHz.
    * **Congestión:** Saturación por otros dispositivos. Afecta el tráfico, no la potencia de la señal.
    """)

st.markdown("---")

# Métricas de Resultados
st.subheader("📊 Resultados del Diagnóstico")
col1, col2, col3 = st.columns(3)
col1.metric("Intensidad (RSSI)", f"{round(rssi)} dBm")
col2.metric("Velocidad Real", f"{round(velocidad_final)} Mbps")
col3.metric("Latencia (Ping)", f"{latencia_texto} ms")

# --- EXPLICACIÓN DE RESULTADOS ---
with st.expander("🔍 ¿Qué significan estos resultados?"):
    st.markdown("""
    * **Intensidad (RSSI):** Indica qué tan "fuerte" llega la señal. De -30 a -50 es ideal. Por debajo de -80 la conexión es inestable.
    * **Velocidad Real:** Lo que realmente puedes navegar después de restar pérdidas físicas e interferencias.
    * **Latencia (Ping):** El retraso en milisegundos. Un ping alto hace que la navegación se sienta "pesada" o con lag.
    """)

st.markdown("---")

# Alertas de estado
st.subheader("📢 Estado de la Conexión")
if estado == 'Excelente': st.success(f"🟢 **Conexión {estado}**: Máximo rendimiento disponible.")
elif estado == 'Buena': st.info(f"🔵 **Conexión {estado}**: Funcionamiento óptimo para casi todo.")
elif estado == 'Regular': st.warning(f"🟡 **Conexión {estado}**: Posibles micro-cortes o lentitud en video.")
elif estado == 'Mala': st.error(f"🟠 **Conexión {estado}**: Señal crítica. Se recomienda usar un repetidor.")
else: st.error(f"🔴 **{estado}**: Sin comunicación con el router.")

# --- RECOMENDACIONES DINÁMICAS ---
st.markdown("---")
st.subheader("🛠️ Recomendaciones de Optimización")

if estado in ['Excelente', 'Buena']:
    st.balloons()
    st.success("✨ **¡Tu configuración actual es ideal!** No requieres cambios de hardware ni de ubicación. La señal física y el entorno permiten un rendimiento óptimo.")
else:
    st.markdown("Basado en el diagnóstico actual, te sugerimos aplicar las siguientes soluciones:")
    
    # Recomendaciones por distancia u obstáculos
    if distancia_m > 20 or cantidad_paredes_sel >= 2:
        st.markdown("""
        * **📍 Reubicación o Repetidores:** La señal se degrada fuertemente por la distancia o materiales densos. 
          * Intenta mover el router a una posición más central y elevada.
          * Si no puedes moverlo, considera instalar un **sistema Wi-Fi Mesh (en malla)** en lugar de un repetidor tradicional.
        """)
        
    # Recomendaciones por la banda elegida
    if banda_seleccionada in ['5 GHz', '6 GHz'] and estado in ['Mala', 'Desconectado']:
        st.markdown("""
        * **🔄 Cambia a la banda de 2.4 GHz:** Estás usando una frecuencia alta (5/6 GHz) que ofrece mucha velocidad pero sufre mucho con los obstáculos. Si necesitas cobertura a través de varias paredes, prioriza la banda de 2.4 GHz en tu dispositivo.
        """)
    elif banda_seleccionada == '2.4 GHz' and congestion_red in ['Media', 'Alta']:
        st.markdown("""
        * **🚀 Migra a 5 GHz o 6 GHz:** La banda de 2.4 GHz está severamente saturada. Si tu router lo permite, conéctate a la banda de 5 GHz para usar canales más libres.
        """)

    # Recomendaciones por tecnología obsoleta
    if gen_seleccionada in ['Wi-Fi 4', 'Wi-Fi 5']:
        st.markdown("""
        * **🏷️ Actualización de Hardware:** Estás simulando con un estándar antiguo. Los routers y dispositivos modernos con **Wi-Fi 6 o Wi-Fi 7** gestionan de forma mucho más eficiente las interferencias.
        """)

    # Recomendaciones por congestión pura
    if congestion_red == 'Alta' and estado == 'Regular':
        st.markdown("""
        * **🌐 Gestión de Canales:** Tu señal física llega bien, pero la red está saturada. Entra a la configuración de tu router y cambia el canal de transmisión a uno menos congestionado.
        """)

    # Caso extremo: Desconectado
    if estado == 'Desconectado':
        st.markdown("""
        * **🔌 Solución Cableada:** El entorno físico bloquea por completo la señal inalámbrica. Para este escenario, la alternativa real es usar un cable Ethernet directo o adaptadores **PLC (Powerline)**.
        """)

# --- ACLARACIÓN FINAL ---
st.markdown("---")
st.info("""
💡 **Nota importante sobre tu velocidad de Internet:** Este simulador calcula la **capacidad máxima de transmisión inalámbrica (el "tubo" de tu Wi-Fi)** entre el router y tu dispositivo bajo estas condiciones. 

Si la *Velocidad Real* calculada aquí es mayor que el plan de internet que tienes contratado con tu proveedor, **no significa que el simulador funcione mal**. En la práctica, tu velocidad de navegación real estará limitada por el tope de tu plan contratado.
""")
