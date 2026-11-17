import streamlit as st
import random
import io
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
from mqtt_helper import enviar_comando, leer_resultado
from ui_arcade import aplicar_estilo_arcade, banner_arcade

st.set_page_config(page_title="Level 1: Modo Voz", page_icon="🎙️", layout="centered")
aplicar_estilo_arcade()

if not st.session_state.get("desbloqueado", False):
    st.warning("⚠️ SYSTEM LOCKED: Ve a la pantalla principal y haz Pulgar Arriba 👍.")
    st.stop()

banner_arcade("LEVEL 1 • RÁFAGA ACUMULATIVA POR VOZ")
st.title("MODO VOZ")

COLORES = {"rojo": 0, "verde": 1, "azul": 2, "amarillo": 3}
INFO_LEDS = [
    {"nombre": "ROJO", "hex": "#ff2a5f", "icono": "🔴"},
    {"nombre": "VERDE", "hex": "#39ff14", "icono": "🟢"},
    {"nombre": "AZUL", "hex": "#00f0ff", "icono": "🔵"},
    {"nombre": "AMARILLO", "hex": "#facc15", "icono": "🟡"},
]

# Inicializar variables acumulativas
if "objetivo_voz" not in st.session_state:
    st.session_state.objetivo_voz = None
if "puntos_voz" not in st.session_state:
    st.session_state.puntos_voz = 0
if "puntaje_total" not in st.session_state:
    st.session_state.puntaje_total = 0
if "historial_voz" not in st.session_state:
    st.session_state.historial_voz = []

# Marcadores superiores
col1, col2, col3 = st.columns(3)
col1.metric("SCORE MODO VOZ", f"{st.session_state.puntos_voz:04d}")
col2.metric("SCORE GLOBAL", f"{st.session_state.puntaje_total:04d}")
activo_txt = INFO_LEDS[st.session_state.objetivo_voz]["nombre"] if st.session_state.objetivo_voz is not None else "LISTO"
col3.metric("COLOR ACTIVO", activo_txt)

if st.session_state.objetivo_voz is not None:
    led = INFO_LEDS[st.session_state.objetivo_voz]
    st.markdown(f"""
    <div style="border: 3px solid {led['hex']}; background: {led['hex']}22; border-radius: 15px; padding: 20px; text-align: center; box-shadow: 0 0 25px {led['hex']}; margin: 15px 0;">
        <h2 style="color: {led['hex']} !important; margin: 0;">{led['icono']} ¡3 SEGUNDOS EN {led['nombre']}!</h2>
        <p style="margin: 5px 0 0 0;">Haz todos los clics posibles en el botón <b>{led['nombre']}</b> de Wokwi.</p>
    </div>
    """, unsafe_allow_html=True)

st.subheader("1. Di el siguiente color (Rojo, Verde, Azul, Amarillo)")
audio = mic_recorder(start_prompt="🎤 GRABAR COLOR", stop_prompt="⏹️ ENVIAR A WOKWI (3s)", format="wav", key="mic_voz")

if audio is not None:
    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(audio["bytes"])) as source:
        audio_data = recognizer.record(source)
        try:
            texto = recognizer.recognize_google(audio_data, language="es-ES").lower()
            idx_elegido = None
            for nombre, idx in COLORES.items():
                if nombre in texto:
                    idx_elegido = idx
                    break
            
            if idx_elegido is None and ("aleatorio" in texto or "topo" in texto or "iniciar" in texto):
                idx_elegido = random.randint(0, 3)

            if idx_elegido is not None:
                st.session_state.objetivo_voz = idx_elegido
                enviar_comando(f"LED:{idx_elegido}")
                st.rerun()
            else:
                st.warning(f"Escuché '{texto}'. Di Rojo, Verde, Azul, Amarillo o Aleatorio.")
        except Exception:
            st.error("No se captó audio claro. Intenta de nuevo.")

st.divider()
st.subheader("2. Sumar puntos de la ronda")

if st.button("⚡ SUMAR CLICS AL MARCADOR"):
    res = leer_resultado()
    if res is not None and ":" in res:
        color_idx, clicks = map(int, res.split(":"))
        ganados = clicks * 10
        
        # Suma acumulativa al modo y al puntaje global
        st.session_state.puntos_voz += ganados
        st.session_state.puntaje_total += ganados
        st.session_state.objetivo_voz = None
        
        color_info = INFO_LEDS[color_idx]
        st.session_state.historial_voz.append(f"{color_info['icono']} {color_info['nombre']}: {clicks} clics (+{ganados} pts)")
        
        if clicks > 0:
            st.balloons()
            st.success(f"💥 +{ganados} PTS sumados ({clicks} clics en {color_info['nombre']}). ¡Total acumulado: {st.session_state.puntos_voz} PTS!")
        else:
            st.warning("⏱️ 0 clics en esta ronda. ¡Di otro color para seguir sumando!")
        st.rerun()
    else:
        st.info("Espera a que terminen los 3 segundos en Wokwi (el LED se apaga) y presiona este botón para sumar tus puntos.")

# Mostrar historial de rondas acumuladas
if st.session_state.historial_voz:
    with st.expander("📜 Historial de rondas acumuladas", expanded=True):
        for item in reversed(st.session_state.historial_voz):
            st.write(item)
        if st.button("🔄 Reiniciar marcador de Modo Voz"):
            st.session_state.puntos_voz = 0
            st.session_state.historial_voz = []
            st.rerun()
