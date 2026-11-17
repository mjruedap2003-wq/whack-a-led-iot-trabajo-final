import streamlit as st
import random
from mqtt_helper import enviar_comando, leer_boton
from ui_arcade import aplicar_estilo_arcade, banner_arcade

st.set_page_config(page_title="Level 2: Modo Visual", page_icon="🖼️", layout="centered")
aplicar_estilo_arcade()

if not st.session_state.get("desbloqueado", False):
    st.warning("⚠️ SYSTEM LOCKED: Ve a la pantalla principal y haz Pulgar Arriba 👍.")
    st.stop()

banner_arcade("LEVEL 2 • VISUAL MATCH ARENA")
st.title("MODO VISUAL")

ELEMENTOS = [
    {"idx": 0, "nombre": "FUEGO (BOTÓN ROJO)", "icono": "🔥", "color": "#ff2a5f"},
    {"idx": 1, "nombre": "BOSQUE (BOTÓN VERDE)", "icono": "🌿", "color": "#39ff14"},
    {"idx": 2, "nombre": "OCÉANO (BOTÓN AZUL)", "icono": "🌊", "color": "#00f0ff"},
    {"idx": 3, "nombre": "RAYO (BOTÓN AMARILLO)", "icono": "⚡", "color": "#facc15"},
]

if "objetivo_visual" not in st.session_state:
    st.session_state.objetivo_visual = random.choice(ELEMENTOS)
if "puntos_visual" not in st.session_state:
    st.session_state.puntos_visual = 0

col1, col2 = st.columns(2)
col1.metric("SCORE", f"{st.session_state.puntos_visual:04d}")
col2.metric("MULTIPLICADOR", "x1.5 PTS")

if st.button("🎲 LANZAR NUEVO RETO A WOKWI"):
    st.session_state.objetivo_visual = random.choice(ELEMENTOS)
    enviar_comando("ALL_ON")
    st.rerun()

obj = st.session_state.objetivo_visual
st.markdown(f"""
<div style="background: linear-gradient(145deg, {obj['color']}25, #0d0f24); border: 3px solid {obj['color']}; border-radius: 18px; padding: 30px; text-align: center; box-shadow: 0 0 30px {obj['color']}66; margin: 15px 0;">
    <div style="font-size: 85px; line-height: 1.1; filter: drop-shadow(0 0 15px {obj['color']});">{obj['icono']}</div>
    <h2 style="color: {obj['color']} !important; margin: 15px 0 5px 0;">{obj['nombre']}</h2>
    <p style="color: #cbd5e1; margin: 0;">Golpea el botón correspondiente en el tablero Wokwi</p>
</div>
""", unsafe_allow_html=True)

with st.expander("👾 Personalizar Skin del Topo (Subir Imagen)"):
    avatar = st.file_uploader("Sube una imagen PNG/JPG para tu personaje", type=["png", "jpg", "jpeg"])
    if avatar is not None:
        st.image(avatar, caption="SKIN EQUIPADA", width=140)

st.divider()
if st.button("✅ VALIDAR BOTÓN PRESIONADO"):
    btn = leer_boton()
    if btn is not None:
        if int(btn) == obj["idx"]:
            st.session_state.puntos_visual += 15
            enviar_comando("HIT")
            st.balloons()
            st.success(f"💥 ¡COMBO PERFECTO! {obj['icono']} asociado correctamente (+15 PTS)")
            st.session_state.objetivo_visual = random.choice(ELEMENTOS)
        else:
            enviar_comando("MISS")
            st.error(f"❌ ERROR DE ASOCIACIÓN: Pulsaste el botón #{int(btn)+1}, pero tocaba {obj['nombre']}.")
    else:
        st.info("Presiona primero el botón físico en Wokwi y luego valida aquí.")
