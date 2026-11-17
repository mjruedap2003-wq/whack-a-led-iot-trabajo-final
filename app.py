import streamlit as st
import mediapipe as mp
import numpy as np
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

st.subheader("Paso 1: Desbloqueo Biométrico 😊")
st.info("Tómate una foto sonriendo para desbloquear el tablero en Wokwi y habilitar los modos de juego.")

foto = st.camera_input("Activa tu cámara y sonríe")

def detectar_sonrisa(imagen_pil):
    mp_face_mesh = mp.solutions.face_mesh
    img_np = np.array(imagen_pil.convert("RGB"))
    
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True) as face_mesh:
        resultados = face_mesh.process(img_np)
        if not resultados.multi_face_landmarks:
            return False, "No se detectó ningún rostro en la foto."
        
        puntos = resultados.multi_face_landmarks[0].landmark
        # Puntos clave del rostro: comisuras de labios (61 y 291) y ancho de mejillas (234 y 454)
        izq_boca = puntos[61]
        der_boca = puntos[291]
        izq_cara = puntos[234]
        der_cara = puntos[454]
        
        ancho_boca = abs(der_boca.x - izq_boca.x)
        ancho_cara = abs(der_cara.x - izq_cara.x)
        proporcion = ancho_boca / ancho_cara
        
        # Cuando una persona sonríe, el ancho de la boca supera el 42% del ancho del rostro
        if proporcion > 0.42:
            return True, f"¡Sonrisa detectada! (Índice de expresión: {proporcion:.2f})"
        else:
            return False, f"Rostro detectado, pero parece serio (Índice: {proporcion:.2f}). ¡Sonríe más!"

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
