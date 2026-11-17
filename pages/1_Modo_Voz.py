import streamlit as st
import random
import io
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
from mqtt_helper import enviar_comando, leer_boton

st.set_page_config(page_title="Modo Voz - Whack-a-LED", page_icon="🎙️")

if not st.session_state.get("desbloqueado", False):
    st.warning("⚠️ Primero debes desbloquear el juego sonriendo en la página principal (`app`).")
    st.stop()

st.title("🎙️ Ambiente 1: Topo por Comandos de Voz")
st.markdown("Di un color (**Rojo, Verde, Azul, Amarillo**) o di **'Aleatorio'** para encender un LED en Wokwi, luego presiona el botón físico.")

COLORES = {"rojo": 0, "verde": 1, "azul": 2, "amarillo": 3}
NOMBRES = ["ROJO 🔴", "VERDE 🟢", "AZUL 🔵", "AMARILLO 🟡"]

if "objetivo_voz" not in st.session_state:
    st.session_state.objetivo_voz = None
if "puntos_voz" not in st.session_state:
    st.session_state.puntos_voz = 0

col1, col2 = st.columns(2)
col1.metric("Puntaje Modo Voz", st.session_state.puntos_voz)
col2.metric("Topo Activo", NOMBRES[st.session_state.objetivo_voz] if st.session_state.objetivo_voz is not None else "Ninguno")

st.subheader("1. Habla al micrófono")
audio = mic_recorder(start_prompt="🎤 Grabar comando de voz", stop_prompt="⏹️ Detener", format="wav", key="mic_voz")

if audio is not None:
    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(audio["bytes"])) as source:
        audio_data = recognizer.record(source)
        try:
            texto = recognizer.recognize_google(audio_data, language="es-ES").lower()
            st.info(f"🗣️ Escuché: **'{texto}'**")
            
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
                st.success(f"¡LED {NOMBRES[idx_elegido]} encendido en Wokwi! Ve a presionarlo.")
            else:
                st.warning("No reconocí un color válido. Di: Rojo, Verde, Azul, Amarillo o Aleatorio.")
        except Exception:
            st.error("No se pudo entender el audio. Intenta hablar más claro.")

st.divider()
st.subheader("2. Verifica tu golpe en Wokwi")
st.caption("Presiona el botón físico en Wokwi y luego haz clic abajo para validar la lectura MQTT (o activa la escucha).")

if st.button("🔄 Verificar botón presionado en Wokwi", type="primary"):
    btn = leer_boton()
    if btn is not None and st.session_state.objetivo_voz is not None:
        if int(btn) == st.session_state.objetivo_voz:
            st.session_state.puntos_voz += 10
            st.session_state.objetivo_voz = None
            enviar_comando("HIT")
            st.balloons()
            st.success("¡ACIERTO! +10 puntos.")
        else:
            enviar_comando("MISS")
            st.error(f"Presionaste el botón {NOMBRES[int(btn)]}, pero el activo era {NOMBRES[st.session_state.objetivo_voz]}.")
    elif btn is None:
        st.info("Aún no se ha recibido ninguna pulsación nueva desde Wokwi.")
