import urllib.request
import json
import streamlit as st

URL_CMD = "https://ntfy.sh/miguel_whackaled_cmd_2026"
URL_RES = "https://ntfy.sh/miguel_whackaled_res_2026/json?poll=1&since=30s"

def init_mqtt():
    if "ultimo_res_id" not in st.session_state:
        st.session_state.ultimo_res_id = ""

def enviar_comando(comando: str):
    init_mqtt()
    try:
        req = urllib.request.Request(
            URL_CMD,
            data=comando.encode("utf-8"),
            method="POST"
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception as e:
        st.error(f"Error enviando orden a Wokwi: {e}")

def leer_resultado():
    init_mqtt()
    try:
        req = urllib.request.urlopen(URL_RES, timeout=3)
        lineas = req.read().decode("utf-8").strip().split("\n")
        for linea in reversed(lineas):
            if not linea.strip():
                continue
            data = json.loads(linea)
            msg_id = data.get("id", "")
            mensaje = data.get("message", "").strip()
            if ":" in mensaje and msg_id != st.session_state.ultimo_res_id:
                st.session_state.ultimo_res_id = msg_id
                return mensaje
    except Exception:
        pass
    return None
