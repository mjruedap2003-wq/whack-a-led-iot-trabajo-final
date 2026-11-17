import paho.mqtt.client as mqtt
import streamlit as st
import queue
import uuid

BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC_CMD = "miguel_whackaled_2026/comando"
TOPIC_RES = "miguel_whackaled_2026/resultado"

def init_mqtt():
    if "mqtt_client" not in st.session_state:
        msg_queue = queue.Queue(maxsize=10)
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                client.subscribe(TOPIC_RES)

        def on_message(client, userdata, msg):
            payload = msg.payload.decode("utf-8").strip()
            if msg_queue.full():
                try:
                    msg_queue.get_nowait()
                except queue.Empty:
                    pass
            msg_queue.put(payload)

        # Client ID único para Streamlit Cloud
        client = mqtt.Client(client_id=f"Streamlit-Miguel-{uuid.uuid4().hex[:8]}")
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(BROKER, PORT, 60)
        client.loop_start()

        st.session_state.mqtt_client = client
        st.session_state.mqtt_queue = msg_queue

def limpiar_cola():
    init_mqtt()
    while not st.session_state.mqtt_queue.empty():
        try:
            st.session_state.mqtt_queue.get_nowait()
        except queue.Empty:
            break

def enviar_comando(comando: str):
    init_mqtt()
    if comando.startswith("LED:"):
        limpiar_cola()
    st.session_state.mqtt_client.publish(TOPIC_CMD, comando)

def leer_resultado():
    init_mqtt()
    if not st.session_state.mqtt_queue.empty():
        return st.session_state.mqtt_queue.get()
    return None
