import streamlit as st

def aplicar_estilo_arcade():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Press+Start+2P&display=swap');

    /* Fondo principal estilo gabinete oscuro con cuadrícula retro */
    .stApp {
        background-color: #090a16;
        background-image: 
            radial-gradient(circle at 50% 0%, #1c1245 0%, #090a16 70%),
            linear-gradient(rgba(0, 240, 255, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 240, 255, 0.04) 1px, transparent 1px);
        background-size: 100% 100%, 30px 30px, 30px 30px;
        color: #e2e8f0;
        font-family: 'Orbitron', sans-serif;
    }

    /* Barra lateral */
    [data-testid="stSidebar"] {
        background-color: #0d0f24;
        border-right: 2px solid #00f0ff;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.2);
    }

    /* Títulos estilo Arcade 8-bit */
    h1 {
        font-family: 'Press Start 2P', cursive !important;
        color: #00f0ff !important;
        text-shadow: 0 0 10px #00f0ff, 3px 3px 0px #ff007f;
        font-size: 1.65rem !important;
        line-height: 1.5 !important;
        text-align: center;
        padding-bottom: 10px;
    }

    h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #ff007f !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        text-shadow: 0 0 8px rgba(255, 0, 127, 0.6);
    }

    /* Métricas / Marcadores de puntaje */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #121530, #0a0c1c);
        border: 2px solid #7000ff;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 0 15px rgba(112, 0, 255, 0.35);
        text-align: center;
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Press Start 2P', cursive !important;
        color: #39ff14 !important;
        font-size: 1.3rem !important;
        text-shadow: 0 0 10px rgba(57, 255, 20, 0.6);
    }

    /* Botones estilo Arcade */
    .stButton > button {
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        background: linear-gradient(90deg, #ff007f, #7000ff) !important;
        color: #ffffff !important;
        border: 2px solid #00f0ff !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 0 12px rgba(255, 0, 127, 0.5);
        transition: all 0.2s ease-in-out;
        width: 100%;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px #00f0ff, 0 0 30px #ff007f;
        border-color: #ffffff !important;
    }

    /* Contenedor de cámara */
    [data-testid="stCameraInput"] {
        border: 2px dashed #00f0ff;
        border-radius: 15px;
        padding: 10px;
        background-color: rgba(13, 15, 36, 0.8);
    }

    /* Badge superior de Arcade */
    .arcade-banner {
        background: linear-gradient(90deg, rgba(0,240,255,0.15), rgba(255,0,127,0.15));
        border: 1px solid #00f0ff;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        font-family: 'Press Start 2P', cursive;
        font-size: 0.7rem;
        color: #facc15;
        margin-bottom: 20px;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

def banner_arcade(texto="INSERT COIN • IOT ARCADE SYSTEM v1.0"):
    st.markdown(f'<div class="arcade-banner">👾 {texto} 👾</div>', unsafe_allow_html=True)
