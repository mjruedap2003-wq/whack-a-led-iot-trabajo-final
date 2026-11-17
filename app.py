import streamlit as st
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
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

# Descargar y cargar el modelo oficial FaceLandmarker de MediaPipe
@st.cache_resource
def cargar_detector():
    modelo = "face_landmarker.task"
    if not os.path.exists(modelo):
        url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
        urllib.request.urlretrieve(url, modelo)
    
    base_options = python.BaseOptions(model_asset_path=modelo)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=True,
        num_faces=1
    )
    return vision.FaceLandmarker.create_from_options(options)

detector = cargar_detector()

st.subheader("Paso 1: Desbloqueo Biométrico 😊")
st.info("Tómate una foto sonriendo para desbloquear el tablero en Wokwi y habilitar los modos de juego.")

foto = st.camera_input("Activa tu cámara y sonríe")

def detectar_sonrisa(imagen_pil):
    img_np = np.array(imagen_pil.convert("RGB"))
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_np)
    resultado = detector.detect(mp_image)
    
    if not resultado.face_blendshapes:
        return False, "No se detectó ningún rostro en la foto. Acércate un poco más a la cámara."
    
    # MediaPipe calcula directamente el nivel de sonrisa (mouthSmileLeft y mouthSmileRight) de 0.0 a 1.0
    blendshapes = {b.category_name: b.score for b in resultado.face_blendshapes[0]}
    nivel_sonrisa = (blendshapes.get("mouthSmileLeft", 0) + blendshapes.get("mouthSmileRight", 0)) / 2
    
    if nivel_sonrisa > 0.35:
        return True, f"¡Sonrisa detectada! (Nivel de felicidad: {nivel_sonrisa*100:.0f}%)"
    else:
        return False, f"Rostro detectado, pero parece serio ({nivel_sonrisa*100:.0f}%). ¡Sonríe más!"

if foto is not None:
    img = Image.open(foto)
    sonrisa_ok, mensaje = detectar_sonrisa(img)

    if sonrisa_ok:
        st.session_state.desbloqueado = True
        enviar_comando("UNLOCK")
        st.success(f"{mensaje} Tablero Wokwi desbloqueado.")
    else:
        st.session_state.desbloqueado = False
        enviar_comando("LOCK")
        st.warning(mensaje)

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
