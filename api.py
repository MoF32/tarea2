import streamlit as st
import math

# 1. Función de simulación con lógica de paredes adaptada
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
    cantidad_paredes = input_data.get('cantidad_paredes', 0)
    tipo_pared = input_data.get('tipo_pared', 'Fina (Tabique/Madera)')
    congestion = input_data.get('congestion', 'Baja')

    gen_props = limites_generacion.get(generacion, limites_generacion['Wi-Fi 6'])

    # CÁLCULO DE RSSI (Potencia de señal)
    rssi = -30
    factor_distancia = 20 if banda == '2.4 GHz' else (23 if banda == '5 GHz' else 25)

    if distancia > 1:
        rssi -= factor_distancia * math.log10(distancia)

    # Coeficientes de pérdida según banda y tipo de pared seleccionado
    if banda == '2.4 GHz':
        p_fina, p_gruesa = 3, 8
    elif banda == '5 GHz':
        p_fina, p_gruesa = 5, 15
    else:  # 6 GHz
        p_fina, p_gruesa = 7, 20

    # Determinar qué coeficiente usar
    coeficiente_pared = p_fina if tipo_pared == 'Fina (Tabique/Madera)' else p_gruesa

    # Aplicar la atenuación total de las paredes
    rssi -= (cantidad_paredes * coeficiente_pared)

    # Límites físicos del RSSI
    if rssi > -30: 
        rssi = -30
    if rssi < -90: 
        rssi = -90

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

    # Penalizaciones extremas por señal baja
    if rssi <= -85: 
        velocidad_final *= 0.1
    if rssi <= -89: 
        velocidad_final = 0.0

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
st.markdown("Ajusta los parámetros para observar cómo el entorno afecta tu conexión.")

# Controles en la barra lateral
st.sidebar.header("⚙️ Parámetros de Simulación")

gen_seleccionada = st.sidebar.selectbox("Generación Wi-Fi", ['Wi-Fi 4', 'Wi-Fi 5', 'Wi-Fi 6', 'Wi-Fi 7'], index=2)
banda_seleccionada = st.sidebar.radio("Banda de Frecuencia", ['2.4 GHz', '5 GHz', '6 GHz'], index=1)
distancia_m = st.sidebar.slider("Distancia al Router (metros)", 1, 50, 12)

st.sidebar.subheader("Obstáculos (Paredes)")
tipo_pared_sel = st.sidebar.selectbox("Tipo de Pared", ['Fina (Tabique/Madera)', 'Gruesa (Concreto/Ladrillo)'])
cantidad_paredes_sel = st.sidebar.slider("Cantidad de Paredes", 0, 5, 1)

congestion_red = st.sidebar.select_slider("Congestión de la Red", options=['Baja', 'Media', 'Alta'], value='Baja')

# Diccionario de entrada adaptado
datos_entrada = {
    'generacion': gen_seleccionada,
    'banda': banda_seleccionada,
    'distancia': distancia_m,
    'cantidad_paredes': cantidad_paredes_sel,
    'tipo_pared': tipo_pared_sel,
    'congestion': congestion_red
}

resultados = calcular_simulacion_wifi(datos_entrada)

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

# Resultados
st.subheader("📊 Resultados del Diagnóstico")
col1, col2, col3 = st.columns(3)
col1.metric("Intensidad (RSSI)", f"{resultados['rssi']} dBm")
col2.metric("Velocidad Real", f"{resultados['velocidad_mbps']} Mbps")
col3.metric("Latencia (Ping)", f"{resultados['latencia_ms']} ms")

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
estado = resultados['estado']
if estado == 'Excelente': st.success(f"🟢 **Conexión {estado}**: Máximo rendimiento disponible.")
elif estado == 'Buena': st.info(f"🔵 **Conexión {estado}**: Funcionamiento óptimo para casi todo.")
elif estado == 'Regular': st.warning(f"🟡 **Conexión {estado}**: Posibles micro-cortes o lentitud en video.")
elif estado == 'Mala': st.error(f"🟠 **Conexión {estado}**: Señal crítica. Se recomienda usar un repetidor.")
else: st.error(f"🔴 **{estado}**: Sin comunicación con el router.")

# ==========================================
# NUEVO: RECOMENDACIONES DINÁMICAS
# ==========================================
st.markdown("---")
st.subheader("🛠️ Recomendaciones de Optimización")

if estado in ['Excelente', 'Buena']:
    st.balloons()
    st.success("✨ **¡Tu configuración actual es ideal!** No requieres cambios de hardware ni de ubicación. La señal física y el entorno permiten un rendimiento óptimo.")
else:
    st.markdown("Basado en el diagnóstico actual, te sugerimos aplicar las siguientes soluciones:")
    
    # 1. Recomendaciones por distancia u obstáculos
    if distancia_m > 20 or cantidad_paredes_sel >= 2:
        st.markdown("""
        * **📍 Reubicación o Repetidores:** La señal se degrada fuertemente por la distancia o materiales densos. 
          * Intenta mover el router a una posición más central y elevada.
          * Si no puedes moverlo, considera instalar un **sistema Wi-Fi Mesh (en malla)** en lugar de un repetidor tradicional para mantener la velocidad sin crear microcortes.
        """)
        
    # 2. Recomendaciones por la banda elegida
    if banda_seleccionada in ['5 GHz', '6 GHz'] and estado in ['Mala', 'Desconectado']:
        st.markdown("""
        * **🔄 Cambia a la banda de 2.4 GHz:** Estás usando una frecuencia alta (5/6 GHz) que ofrece mucha velocidad pero sufre mucho con los obstáculos. Si necesitas cobertura a través de varias paredes, prioriza la banda de 2.4 GHz en tu dispositivo, ya que atraviesa mejor las estructuras sólidas.
        """)
    elif banda_seleccionada == '2.4 GHz' and congestion_red in ['Media', 'Alta']:
        st.markdown("""
        * **🚀 Migra a 5 GHz o 6 GHz:** La banda de 2.4 GHz está severamente saturada. Si tu router y dispositivo lo permiten, conéctate a la banda de 5 GHz. Aunque tiene menos alcance, cuenta con muchos más canales libres y evitarás la ralentización por congestión vecinal.
        """)

    # 3. Recomendaciones por tecnología obsoleta
    if gen_seleccionada in ['Wi-Fi 4', 'Wi-Fi 5']:
        st.markdown("""
        * **🏷️ Actualización de Hardware:** Estás simulando con un estándar antiguo (`Wi-Fi 4` o `Wi-Fi 5`). Los routers y dispositivos modernos con **Wi-Fi 6 o Wi-Fi 7** gestionan de forma mucho más eficiente las interferencias y la pérdida de paquetes en entornos complejos.
        """)

    # 4. Recomendaciones por congestión pura
    if congestion_red == 'Alta' and estado == 'Regular':
        st.markdown("""
        * **🌐 Gestión de Canales:** Tu señal física llega bien, pero la red está saturada. Entra a la configuración de tu router y cambia el canal de transmisión a uno menos congestionado (puedes usar apps móviles como *Wi-Fi Analyzer* para ver cuáles están libres en tu zona).
        """)

    # 5. Caso extremo: Desconectado
    if estado == 'Desconectado':
        st.markdown("""
        * **🔌 Solución Cableada:** El entorno físico bloquea por completo la señal inalámbrica. Para este escenario, la única alternativa real es tirar un cable Ethernet directo o utilizar adaptadores **PLC (Powerline)**, que transmiten la señal de internet a través de los cables eléctricos de la casa.
        """)

# --- ACLARACIÓN FINAL (PLAN DE INTERNET) ---
st.markdown("---")
st.info("""
💡 **Nota importante sobre tu velocidad de Internet:** Este simulador calcula la **capacidad máxima de transmisión inalámbrica (el "tubo" de tu Wi-Fi)** entre el router y tu dispositivo bajo estas condiciones. 

Si la *Velocidad Real* calculada aquí es mayor que el plan de internet que tienes contratado con tu proveedor, **no significa que el simulador funcione mal**. En la práctica, tu velocidad de navegación real estará limitada por el tope de tu plan contratado.
""")
