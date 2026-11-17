import streamlit as st
import random
import io
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
from mqtt_helper import enviar_comando, leer_boton
from ui_arcade import aplicar_estilo_arcade, banner_arcade

st.set_page_config(page_title="Level 1: Modo Voz", page_icon="🎙️", layout="centered")
aplicar_estilo_arcade()

if not st.session_state.get("desbloqueado", False):
    st.warning("⚠️ SYSTEM LOCKED: Ve a la pantalla principal y haz Pulgar Arriba 👍.")
    st.stop()

banner_arcade("LEVEL 1 • VOICE COMMAND ARENA")
st.title("MODO VOZ")

COLORES = {"rojo": 0, "verde": 1, "azul": 2, "amarillo": 3}
INFO_LEDS = [
    {"nombre": "ROJO", "hex": "#ff2a5f", "icono": "🔴"},
    {"nombre": "VERDE", "hex": "#39ff14", "icono": "🟢"},
    {"nombre": "AZUL", "hex": "#00f0ff", "icono": "🔵"},
    {"nombre": "AMARILLO", "hex": "#facc15", "icono": "🟡"},
]

if "objetivo_voz" not in st.session_state:
    st.session_state.objetivo_voz = None
if "puntos_voz" not in st.session_state:
    st.session_state.puntos_voz = 0

col1, col2 = st.columns(2)
col1.metric("SCORE", f"{st.session_state.puntos_voz:04d}")
activo_txt = INFO_LEDS[st.session_state.objetivo_voz]["nombre"] if st.session_state.objetivo_voz is not None else "ESPERANDO"
col2.metric("TOPO ACTIVO", activo_txt)

# Radar visual del estado del LED en Wokwi
if st.session_state.objetivo_voz is not None:
    led = INFO_LEDS[st.session_state.objetivo_voz]
    st.markdown(f"""
    <div style="border: 3px solid {led['hex']}; background: {led['hex']}22; border-radius: 15px; padding: 20px; text-align: center; box-shadow: 0 0 25px {led['hex']}; margin: 15px 0;">
        <h2 style="color: {led['hex']} !important; margin: 0;">{led['icono']} LED {led['nombre']} ENCENDIDO</h2>
        <p style="margin: 5px 0 0 0;">¡Presiona rápido el botón <b>{led['nombre']}</b> en Wokwi!</p>
    </div>
    """, unsafe_allow_html=True)

st.subheader("1. Invoca un Topo por Voz")
st.caption("Di: **'Rojo'**, **'Verde'**, **'Azul'**, **'Amarillo'** o **'Aleatorio'**")
audio = mic_recorder(start_prompt="🎤 MANTENER / GRABAR VOZ", stop_prompt="⏹️ ENVIAR COMANDO", format="wav", key="mic_voz")

if audio is not None:
    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(audio["bytes"])) as source:
        audio_data = recognizer.record(source)
        try:
            texto = recognizer.recognize_google(audio_data, language="es-ES").lower()
            st.info(f"🗣️ COMANDO RECIBIDO: **'{texto.upper()}'**")
            
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
                st.warning("Comando no reconocido. Di Rojo, Verde, Azul, Amarillo o Aleatorio.")
        except Exception:
            st.error("No se captó audio claro. Intenta de nuevo.")

st.divider()
st.subheader("2. Confirmar Golpe en Wokwi")

if st.button("⚡ VALIDAR IMPACTO EN WOKWI"):
    btn = leer_boton()
    if btn is not None and st.session_state.objetivo_voz is not None:
        if int(btn) == st.session_state.objetivo_voz:
            st.session_state.puntos_voz += 10
            st.session_state.objetivo_voz = None
            enviar_comando("HIT")
            st.balloons()
            st.success("💥 ¡CRITICAL HIT! +10 PUNTOS")
        else:
            enviar_comando("MISS")
            st.error(f"❌ FALLASTE: Presionaste {INFO_LEDS[int(btn)]['nombre']} y el activo era {INFO_LEDS[st.session_state.objetivo_voz]['nombre']}.")
    elif btn is None:
        st.info("Presiona primero el botón físico en Wokwi.")
