import os
# Forzar compatibilidad de Keras para modelos exportados desde Teachable Machine
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import streamlit as st
import numpy as np
from PIL import Image, ImageOps
import tf_keras as keras
from mqtt_helper import init_mqtt, enviar_comando

st.set_page_config(page_title="Whack-a-LED IoT", page_icon="🕹️", layout="centered")
init_mqtt()

if "desbloqueado" not in st.session_state:
    st.session_state.desbloqueado = False

st.title("🕹️ Whack-a-LED / Topo IoT")
st.markdown("Sistema multimodal conectado en tiempo real con **Wokwi (ESP32)** vía MQTT.")

# Cargar modelo y etiquetas de Teachable Machine una sola vez
@st.cache_resource
def cargar_modelo_tm():
    modelo = keras.models.load_model("keras_model.h5", compile=False)
    with open("labels.txt", "r", encoding="utf-8") as f:
        etiquetas = [line.strip() for line in f.readlines()]
    return modelo, etiquetas

try:
    modelo, etiquetas = cargar_modelo_tm()
except Exception as e:
    st.error(f"Error cargando keras_model.h5 o labels.txt. Verifica que estén en la raíz de GitHub. Detalle: {e}")
    st.stop()

st.subheader("Paso 1: Desbloqueo Biométrico 😊")
st.info("Tómate una foto sonriendo (modelo entrenado en Teachable Machine) para desbloquear el tablero en Wokwi.")

foto = st.camera_input("Activa tu cámara y sonríe")

def predecir_expresion(imagen_pil):
    # Teachable Machine requiere imágenes RGB de 224x224 normalizadas entre -1 y 1
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
    
    # Limpiar el número inicial de labels.txt (ej. "0 Feliz" -> "Feliz")
    nombre_clase = clase_raw.split(" ", 1)[1] if " " in clase_raw else clase_raw
    return nombre_clase, confianza

if foto is not None:
    img = Image.open(foto)
    clase_detectada, confianza = predecir_expresion(img)

    # Verifica si la clase ganadora es "Feliz" (sin importar mayúsculas/minúsculas) con al menos 70% de confianza
    if "feliz" in clase_detectada.lower() and confianza >= 0.70:
        st.session_state.desbloqueado = True
        enviar_comando("UNLOCK")
        st.success(f"¡Expresión detectada: **{clase_detectada}** ({confianza*100:.1f}%)! Tablero Wokwi desbloqueado.")
    else:
        st.session_state.desbloqueado = False
        enviar_comando("LOCK")
        st.warning(f"Detectado: **{clase_detectada}** ({confianza*100:.1f}%). Necesitas sonreír para desbloquear.")

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
