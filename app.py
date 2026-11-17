import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import streamlit as st
import numpy as np
from PIL import Image, ImageOps
import tensorflow as tf
from mqtt_helper import init_mqtt, enviar_comando
from ui_arcade import aplicar_estilo_arcade, banner_arcade

st.set_page_config(page_title="Whack-a-LED Arcade IoT", page_icon="🕹️", layout="centered")
aplicar_estilo_arcade()
init_mqtt()

if "desbloqueado" not in st.session_state:
    st.session_state.desbloqueado = False

banner_arcade("PLAYER 1 READY • CONECTADO A ESP32 WOKWI")
st.title("WHACK-A-LED ARCADE")
st.markdown("<p style='text-align:center; color:#94a3b8;'>CONTROL MULTIMODAL EN TIEMPO REAL VÍA MQTT</p>", unsafe_allow_html=True)

@st.cache_resource
def cargar_modelo_tm():
    modelo = tf.keras.models.load_model("keras_model.h5", compile=False)
    with open("labels.txt", "r", encoding="utf-8") as f:
        etiquetas = [line.strip() for line in f.readlines()]
    return modelo, etiquetas

try:
    modelo, etiquetas = cargar_modelo_tm()
except Exception as e:
    st.error(f"Error cargando modelo: {e}")
    st.stop()

st.subheader("📷 Escáner Biométrico de Acceso")
st.markdown("Haz **👍 PULGAR ARRIBA** para encender la máquina o **👎 PULGAR ABAJO** para bloquearla.")

foto = st.camera_input("ESCÁNER DE GESTOS")

def predecir_gesto(imagen_pil):
    size = (224, 224)
    image = ImageOps.fit(imagen_pil.convert("RGB"), size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1.0

    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized_image_array

    prediccion = modelo.predict(data, verbose=0)
    indice = int(np.argmax(prediccion))
    clase_raw = etiquetas[indice]
    confianza = float(prediccion[0][indice])
    
    nombre_clase = clase_raw.split(" ", 1)[1] if " " in clase_raw else clase_raw
    return nombre_clase, confianza

if foto is not None:
    img = Image.open(foto)
    gesto_detectado, confianza = predecir_gesto(img)
    gesto_norm = gesto_detectado.lower().replace(" ", "_")

    if "pulgar_arriba" in gesto_norm and confianza >= 0.70:
        st.session_state.desbloqueado = True
        enviar_comando("UNLOCK")
        st.success(f"👍 GESTO VALIDADO: {gesto_detectado.upper()} ({confianza*100:.1f}%) — ¡SISTEMA ONLINE!")
    elif "pulgar_abajo" in gesto_norm and confianza >= 0.70:
        st.session_state.desbloqueado = False
        enviar_comando("LOCK")
        st.error(f"👎 GESTO VALIDADO: {gesto_detectado.upper()} ({confianza*100:.1f}%) — SISTEMA BLOQUEADO")
    else:
        st.warning(f"🖐️ LECTURA: {gesto_detectado.upper()} ({confianza*100:.1f}%) — HAZ PULGAR ARRIBA 👍")

st.divider()

if st.session_state.desbloqueado:
    st.markdown("""
    <div style="border: 2px solid #39ff14; background: rgba(57, 255, 20, 0.1); border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 0 20px rgba(57, 255, 20, 0.3);">
        <h3 style="color: #39ff14 !important; margin-top: 0;">🟢 TABLERO DESBLOQUEADO</h3>
        <p style="font-size: 0.95rem;">Abre el menú lateral izquierdo y selecciona tu nivel:</p>
        <p><b>🎙️ LEVEL 1: MODO VOZ</b> &nbsp;|&nbsp; <b>🖼️ LEVEL 2: MODO VISUAL</b></p>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    if st.button("🔒 BLOQUEAR GABINETE"):
        st.session_state.desbloqueado = False
        enviar_comando("LOCK")
        st.rerun()
else:
    st.markdown("""
    <div style="border: 2px solid #ff007f; background: rgba(255, 0, 127, 0.1); border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 0 20px rgba(255, 0, 127, 0.3);">
        <h3 style="color: #ff007f !important; margin-top: 0;">🔴 SYSTEM LOCKED</h3>
        <p style="margin-bottom: 0;">Muestra el <b>Pulgar Arriba 👍</b> en la cámara para iniciar partida</p>
    </div>
    """, unsafe_allow_html=True)
