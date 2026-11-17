import streamlit as st
import cv2
import numpy as np
import urllib.request
import os
from PIL import Image
from mqtt_helper import init_mqtt, enviar_comando

st.set_page_config(page_title="Whack-a-LED IoT", page_icon="🕹️", layout="centered")
init_mqtt()

if "desbloqueado" not in st.session_state:
    st.session_state.desbloqueado = False
if "puntaje_total" not in st.session_state:
    st.session_state.puntaje_total = 0

st.title("🕹️ Whack-a-LED / Topo IoT")
st.markdown("Sistema multimodal conectado en tiempo real con **Wokwi (ESP32)** vía MQTT.")

# Descargar clasificadores Haar si no existen localmente (evita el error de cv2.data)
@st.cache_resource
def cargar_clasificadores():
    base_url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/"
    archivos = {
        "face": "haarcascade_frontalface_default.xml",
        "smile": "haarcascade_smile.xml"
    }
    for clave, nombre in archivos.items():
        if not os.path.exists(nombre):
            urllib.request.urlretrieve(base_url + nombre, nombre)
    return cv2.CascadeClassifier(archivos["face"]), cv2.CascadeClassifier(archivos["smile"])

face_cascade, smile_cascade = cargar_clasificadores()

st.subheader("Paso 1: Desbloqueo Biométrico 😊")
st.info("Tómate una foto sonriendo para desbloquear el tablero en Wokwi y habilitar los modos de juego.")

foto = st.camera_input("Activa tu cámara y sonríe")

if foto is not None:
    img = Image.open(foto)
    img_np = np.array(img)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

    rostros = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    sonrisa_detectada = False

    for (x, y, w, h) in rostros:
        roi_gray = gray[y:y+h, x:x+w]
        sonrisas = smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.7, minNeighbors=20)
        if len(sonrisas) > 0:
            sonrisa_detectada = True
            break

    if sonrisa_detectada:
        st.session_state.desbloqueado = True
        enviar_comando("UNLOCK")
        st.success("¡Sonrisa detectada! Tablero Wokwi desbloqueado. Selecciona un ambiente en el menú lateral izquierdo.")
    else:
        st.session_state.desbloqueado = False
        enviar_comando("LOCK")
        st.warning("No detectamos una sonrisa clara. ¡Inténtalo de nuevo sonriendo ampliamente!")

st.divider()

if st.session_state.desbloqueado:
    st.success("🔓 **Estado del sistema: DESBLOQUEADO**")
    st.markdown("""
    👈 **Abre el menú lateral izquierdo y elige tu ambiente de juego:**
    1. **1 Modo Voz:** Controla qué topo aparece mediante comandos de voz y golpéalo en Wokwi.
    2. **2 Modo Visual:** Asocia imágenes en pantalla con los botones físicos de colores en Wokwi.
    """)
    if st.button("🔒 Bloquear juego nuevamente"):
        st.session_state.desbloqueado = False
        enviar_comando("LOCK")
        st.rerun()
else:
    st.error("🔒 **Estado del sistema: BLOQUEADO** (Sonríe arriba para jugar)")
