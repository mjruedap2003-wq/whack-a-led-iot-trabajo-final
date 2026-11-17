import paho.mqtt.client as mqtt
import streamlit as st
import queue

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_CMD = "eafit/whackaled/comando"
TOPIC_BTN = "eafit/whackaled/boton"

def init_mqtt():
    if "mqtt_client" not in st.session_state:
        msg_queue = queue.Queue()
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                client.subscribe(TOPIC_BTN)

        def on_message(client, userdata, msg):
            payload = msg.payload.decode("utf-8").strip()
            msg_queue.put(payload)

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(BROKER, PORT, 60)
        client.loop_start()

        st.session_state.mqtt_client = client
        st.session_state.mqtt_queue = msg_queue

def enviar_comando(comando: str):
    init_mqtt()
    st.session_state.mqtt_client.publish(TOPIC_CMD, comando)

def leer_boton():
    init_mqtt()
    if not st.session_state.mqtt_queue.empty():
        return st.session_state.mqtt_queue.get()
    return None
