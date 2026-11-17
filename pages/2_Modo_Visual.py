import streamlit as st
import random
from mqtt_helper import enviar_comando, leer_resultado
from ui_arcade import aplicar_estilo_arcade, banner_arcade

st.set_page_config(page_title="Level 2: Modo Visual", page_icon="🖼️", layout="centered")
aplicar_estilo_arcade()

if not st.session_state.get("desbloqueado", False):
    st.warning("⚠️ SYSTEM LOCKED: Ve a la pantalla principal y haz Pulgar Arriba 👍.")
    st.stop()

banner_arcade("LEVEL 2 • RÁFAGA VISUAL ACUMULATIVA")
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
if "puntaje_total" not in st.session_state:
    st.session_state.puntaje_total = 0
if "historial_visual" not in st.session_state:
    st.session_state.historial_visual = []

col1, col2, col3 = st.columns(3)
col1.metric("SCORE VISUAL", f"{st.session_state.puntos_visual:04d}")
col2.metric("SCORE GLOBAL", f"{st.session_state.puntaje_total:04d}")
col3.metric("VALOR CLIC", "15 PTS")

if st.button("🎲 LANZAR RETO DE 3 SEGUNDOS A WOKWI"):
    st.session_state.objetivo_visual = random.choice(ELEMENTOS)
    enviar_comando(f"LED:{st.session_state.objetivo_visual['idx']}")
    st.rerun()

obj = st.session_state.objetivo_visual
st.markdown(f"""
<div style="background: linear-gradient(145deg, {obj['color']}25, #0d0f24); border: 3px solid {obj['color']}; border-radius: 18px; padding: 30px; text-align: center; box-shadow: 0 0 30px {obj['color']}66; margin: 15px 0;">
    <div style="font-size: 85px; line-height: 1.1; filter: drop-shadow(0 0 15px {obj['color']});">{obj['icono']}</div>
    <h2 style="color: {obj['color']} !important; margin: 15px 0 5px 0;">{obj['nombre']}</h2>
    <p style="color: #cbd5e1; margin: 0;">¡Tienes <b>3 segundos</b> en Wokwi para darle todos los clics posibles!</p>
</div>
""", unsafe_allow_html=True)

with st.expander("👾 Personalizar Skin del Topo (Subir Imagen)"):
    avatar = st.file_uploader("Sube una imagen PNG/JPG para tu personaje", type=["png", "jpg", "jpeg"])
    if avatar is not None:
        st.image(avatar, caption="SKIN EQUIPADA", width=140)

st.divider()
if st.button("✅ SUMAR PUNTAJE DE LA RONDA"):
    res = leer_resultado()
    if res is not None and ":" in res:
        color_idx, clicks = map(int, res.split(":"))
        ganados = clicks * 15
        
        st.session_state.puntos_visual += ganados
        st.session_state.puntaje_total += ganados
        
        el_info = ELEMENTOS[color_idx]
        st.session_state.historial_visual.append(f"{el_info['icono']} {el_info['nombre']}: {clicks} clics (+{ganados} pts)")
        
        if clicks > 0:
            st.balloons()
            st.success(f"💥 +{ganados} PTS sumados ({clicks} clics). ¡Total acumulado: {st.session_state.puntos_visual} PTS!")
        else:
            st.warning("⏱️ 0 clics registrados en los 3 segundos. ¡Lanza otro reto!")
        st.rerun()
    else:
        st.info("Lanza un reto, haz todos los clics que puedas en Wokwi durante 3 segundos y luego suma tu puntaje.")

if st.session_state.historial_visual:
    with st.expander("📜 Historial de rondas acumuladas", expanded=True):
        for item in reversed(st.session_state.historial_visual):
            st.write(item)
        if st.button("🔄 Reiniciar marcador de Modo Visual"):
            st.session_state.puntos_visual = 0
            st.session_state.historial_visual = []
            st.rerun()
