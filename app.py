from flask import Flask, render_template, jsonify
import paho.mqtt.client as mqtt
import json
from datetime import datetime

app = Flask(__name__)

# Global variables
latest_status = {
    "status": "Loading...",
    "fan_status": "Loading...",
    "lamp_status": "Loading...",
    "actions": []
}
history_data = []  # List to store history of actions

# MQTT Configuration
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_STATUS = "farm/monitoring/status"

# MQTT Callback functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(TOPIC_STATUS)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    global latest_status, history_data
    try:
        # Decode message
        status_data = json.loads(msg.payload.decode())
        latest_status = status_data

        # Add timestamp if not present
        timestamp = status_data.get("timestamp")
        if not timestamp:
            timestamp = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            status_data["timestamp"] = timestamp

        # Add to history (timestamped)
        if len(history_data) >= 10:  # Limit to the last 10 entries
            history_data.pop(0)
        history_data.append({
            "timestamp": timestamp,
            "status": status_data["status"],
            "fan_status": status_data["fan_status"],
            "lamp_status": status_data["lamp_status"],
            "actions": status_data["actions"]
        })
        print(f"Updated status and history: {status_data}")
    except Exception as e:
        print(f"Error processing message: {e}")

# MQTT Client Initialization
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER, PORT, 60)
mqtt_client.loop_start()

# Flask Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/status")
def status():
    return jsonify(latest_status)

@app.route("/history")
def history():
    return jsonify(history_data)

if __name__ == "__main__":
    app.run(debug=True)
