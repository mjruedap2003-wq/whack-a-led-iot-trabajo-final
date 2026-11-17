import streamlit as st
import random
from mqtt_helper import enviar_comando, leer_boton

st.set_page_config(page_title="Modo Visual - Whack-a-LED", page_icon="🖼️")

if not st.session_state.get("desbloqueado", False):
    st.warning("⚠️ Primero debes desbloquear el juego sonriendo en la página principal (`app`).")
    st.stop()

st.title("🖼️ Ambiente 2: Caza Visual por Imágenes")
st.markdown("Asocia la imagen que aparece en pantalla con su botón correspondiente en **Wokwi**.")

# Mapeo visual: Emoji/Imagen -> Índice de botón en Wokwi
ELEMENTOS = [
    {"idx": 0, "nombre": "Fuego (Botón Rojo)", "icono": "🔥", "color": "#FF4B4B"},
    {"idx": 1, "nombre": "Naturaleza (Botón Verde)", "icono": "🌿", "color": "#21C354"},
    {"idx": 2, "nombre": "Océano (Botón Azul)", "icono": "🌊", "color": "#1C83E1"},
    {"idx": 3, "nombre": "Energía (Botón Amarillo)", "icono": "⚡", "color": "#FACA2B"},
]

if "objetivo_visual" not in st.session_state:
    st.session_state.objetivo_visual = random.choice(ELEMENTOS)
if "puntos_visual" not in st.session_state:
    st.session_state.puntos_visual = 0

# Personalización multimodal con carga de imagen
avatar = st.file_uploader("Opcional: Sube una imagen personalizada para tu Topo", type=["png", "jpg", "jpeg"])

col1, col2 = st.columns(2)
col1.metric("Puntaje Modo Visual", st.session_state.puntos_visual)
col2.metric("Objetivo Actual", st.session_state.objetivo_visual["nombre"])

if st.button("🎲 Lanzar nuevo objetivo visual a Wokwi"):
    st.session_state.objetivo_visual = random.choice(ELEMENTOS)
    enviar_comando("ALL_ON")  # Enciende los 4 LEDs como señal de reto visual
    st.rerun()

# Tarjeta visual grande del objetivo
obj = st.session_state.objetivo_visual
st.markdown(f"""
<div style="background-color:{obj['color']}22; border: 3px solid {obj['color']}; border-radius: 15px; padding: 30px; text-align: center;">
    <h1 style="font-size: 80px; margin: 0;">{obj['icono']}</h1>
    <h3>¡Golpea el botón de: {obj['nombre']}!</h3>
</div>
""", unsafe_allow_html=True)

if avatar is not None:
    st.image(avatar, caption="Tu Topo personalizado apareció aquí", width=150)

st.divider()
if st.button("✅ Validar botón presionado en Wokwi", type="primary"):
    btn = leer_boton()
    if btn is not None:
        if int(btn) == obj["idx"]:
            st.session_state.puntos_visual += 15
            enviar_comando("HIT")
            st.success(f"¡Correcto! Asociaste {obj['icono']} con su botón físico (+15 pts).")
            st.session_state.objetivo_visual = random.choice(ELEMENTOS)
        else:
            enviar_comando("MISS")
            st.error(f"Incorrecto. Presionaste el botón {int(btn)+1}, pero {obj['icono']} corresponde a {obj['nombre']}.")
    else:
        st.info("Presiona primero el botón físico en Wokwi y luego haz clic aquí para verificar.")
