"""
Flask Backend Server for Water Quality Monitoring System
Handles MQTT data from Wokwi, ML predictions, and email alerts
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import joblib
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import paho.mqtt.client as mqtt
import threading
from pymongo import MongoClient

# Import custom modules
from email_service import EmailAlertService
import config

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = 'water_quality_secret_key_2025'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", ping_interval=config.WEBSOCKET_PING_INTERVAL, async_mode='threading')

# MQTT Configuration
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 8080
MQTT_TOPIC = "water_quality/telemetry"

# Initialize MongoDB
try:
    mongo_client = MongoClient(config.MONGO_URI)
    db = mongo_client[config.MONGO_DB_NAME]
    readings_collection = db['readings']
    print(f"✅ MongoDB connected: {config.MONGO_DB_NAME}")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    readings_collection = None

# Load ML model
MODEL_PATH = Path(__file__).parent / config.MODEL_PATH
try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ ML Model loaded: {MODEL_PATH.name}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

# Initialize email service
email_service = None
if config.validate_config():
    try:
        email_service = EmailAlertService(
            smtp_server=config.SMTP_SERVER,
            smtp_port=config.SMTP_PORT,
            sender_email=config.SENDER_EMAIL,
            sender_password=config.SENDER_PASSWORD,
            recipient_email=config.RECIPIENT_EMAIL
        )
        print(f"✅ Email service initialized (recipient: {config.RECIPIENT_EMAIL})")
    except Exception as e:
        print(f"⚠️  Email service initialization failed: {e}")
else:
    print("⚠️  Email alerts disabled - configure config.py")

# Consecutive contamination tracking
consecutive_contamination_count = 0
last_prediction = None
email_alert_sent = False

def predict_water_quality(data):
    """
    Predict water quality using ML model
    Returns: prediction (0=Unsafe, 1=Safe), confidence
    """
    if model is None:
        return 0, 0.0
    
    try:
        features = np.array([[
            float(data.get('pH', 7.0)),
            float(data.get('Sulphate', 250)),
            float(data.get('Hardness', 165)),
            float(data.get('Conductivity', 500)),
            float(data.get('TDS', 600)),
            float(data.get('Turbidity', 3.0))
        ]])
        
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        confidence = float(max(probabilities) * 100)
        
        return int(prediction), confidence
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return 0, 0.0

def check_thresholds(data):
    """
    Check if parameters are within safe ranges
    """
    results = {}
    for param, value in data.items():
        if param in config.SAFE_RANGES and param != 'timestamp':
            safe_min = config.SAFE_RANGES[param]['min']
            safe_max = config.SAFE_RANGES[param]['max']
            try:
                val = float(value)
                is_safe = safe_min <= val <= safe_max
                results[param] = {
                    'value': val,
                    'safe_min': safe_min,
                    'safe_max': safe_max,
                    'is_safe': is_safe
                }
            except:
                pass
    return results

def handle_consecutive_contamination(sensor_data, prediction_value):
    """
    Track consecutive contamination and send email alert if threshold reached
    """
    global consecutive_contamination_count, last_prediction, email_alert_sent
    
    if prediction_value == 0:  # Unsafe/Contaminated
        consecutive_contamination_count += 1
        print(f"⚠️  Consecutive contamination count: {consecutive_contamination_count}")
        
        # Check if threshold reached and email not yet sent
        if (consecutive_contamination_count >= config.CONSECUTIVE_CONTAMINATION_THRESHOLD 
            and not email_alert_sent 
            and email_service is not None):
            
            print(f"🚨 ALERT: {config.CONSECUTIVE_CONTAMINATION_THRESHOLD} consecutive contaminations detected!")
            
            # Send email alert
            success = email_service.send_contamination_alert(
                sensor_data, 
                consecutive_contamination_count
            )
            
            if success:
                email_alert_sent = True
                # Broadcast alert to all clients
                socketio.emit('email_alert_sent', {
                    'consecutive_count': consecutive_contamination_count,
                    'timestamp': datetime.now().isoformat()
                })
    else:  # Safe
        # Reset counter when safe reading detected
        if consecutive_contamination_count > 0:
            print(f"✅ Safe reading detected. Resetting counter (was {consecutive_contamination_count})")
        consecutive_contamination_count = 0
        email_alert_sent = False
    
    last_prediction = prediction_value
    
    return consecutive_contamination_count

def process_sensor_data(sensor_data, source="MQTT"):
    """Common logic to process sensor data and broadcast updates"""
    try:
        # Add timestamp if not present
        if 'timestamp' not in sensor_data:
            sensor_data['timestamp'] = datetime.now().isoformat()
        
        # Make prediction
        prediction, confidence = predict_water_quality(sensor_data)
        threshold_results = check_thresholds(sensor_data)
        
        # Track consecutive contamination
        consecutive_count = handle_consecutive_contamination(sensor_data, prediction)
        
        # Save to MongoDB
        if readings_collection is not None:
            try:
                document = {
                    'timestamp': sensor_data['timestamp'],
                    'pH': float(sensor_data.get('pH', 0)),
                    'Sulphate': float(sensor_data.get('Sulphate', 0)),
                    'Hardness': float(sensor_data.get('Hardness', 0)),
                    'Conductivity': float(sensor_data.get('Conductivity', 0)),
                    'TDS': float(sensor_data.get('TDS', 0)),
                    'Turbidity': float(sensor_data.get('Turbidity', 0)),
                    'prediction': int(prediction),
                    'confidence': float(confidence),
                    'source': source
                }
                readings_collection.insert_one(document)
                # print("💾 Data saved to MongoDB")
            except Exception as e:
                print(f"❌ Failed to save to MongoDB: {e}")

        # Prepare response
        response = {
            'sensor_data': sensor_data,
            'prediction': 'Safe' if prediction == 1 else 'Unsafe',
            'prediction_value': int(prediction),
            'confidence': round(confidence, 2),
            'led_status': 'green' if prediction == 1 else 'red',
            'thresholds': threshold_results,
            'consecutive_count': consecutive_count,
            'email_alert_sent': email_alert_sent,
            'timestamp': sensor_data.get('timestamp', ''),
            'source': source
        }
        
        # Broadcast to all clients
        socketio.emit('prediction_update', response)
        
        status_icon = "✅" if prediction == 1 else "⚠️"
        print(f"{status_icon} [{source}] Prediction: {response['prediction']} ({confidence:.2f}% confidence)")
        
    except Exception as e:
        print(f"❌ Error processing data: {e}")

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"📡 MQTT Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC)
    print(f"👂 Subscribed to topic: {MQTT_TOPIC}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        print(f"📥 MQTT Data: {data}")
        process_sensor_data(data, source="MQTT")
    except json.JSONDecodeError:
        print(f"⚠️ Invalid JSON from MQTT: {msg.payload}")
    except Exception as e:
        print(f"❌ MQTT Error: {e}")

# Start MQTT Client
mqtt_client = mqtt.Client(transport="websockets")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def start_mqtt():
    try:
        print(f"🔌 Connecting to MQTT Broker: {MQTT_BROKER} (WebSockets)...")
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
    except Exception as e:
        print(f"❌ Failed to connect to MQTT broker: {e}")

# Routes
@app.route('/')
def index():
    """Main page with Wokwi simulator and prediction dashboard"""
    return render_template('index.html')

@app.route('/history')
def history():
    """History page with interactive charts"""
    return render_template('history.html')

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """REST API endpoint for water quality prediction"""
    try:
        data = request.json
        process_sensor_data(data, source="API")
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/status')
def api_status():
    """Get system status"""
    return jsonify({
        'model_loaded': model is not None,
        'email_configured': email_service is not None,
        'consecutive_count': consecutive_contamination_count,
        'email_alert_sent': email_alert_sent,
        'alert_threshold': config.CONSECUTIVE_CONTAMINATION_THRESHOLD,
        'mqtt_connected': mqtt_client.is_connected()
    })

@app.route('/api/history')
def api_history():
    """Get historical data for charts"""
    try:
        if readings_collection is None:
            return jsonify([])
        
        # Get last 100 readings, sorted by timestamp descending
        cursor = readings_collection.find({}, {'_id': 0}).sort('timestamp', -1).limit(100)
        data = list(cursor)
        # Return in ascending order for charts
        return jsonify(data[::-1])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('✅ Client connected - Emitting status...')
    emit('connection_status', {
        'status': 'connected',
        'consecutive_count': consecutive_contamination_count,
        'email_alert_sent': email_alert_sent
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('❌ Client disconnected')

if __name__ == '__main__':
    print("=" * 60)
    print("🌊 Water Quality Monitoring Server - MQTT Integration")
    print("=" * 60)
    print(f"✅ ML Model: {MODEL_PATH.name}")
    print(f"📡 MQTT Broker: {MQTT_BROKER}")
    print(f"👂 Topic: {MQTT_TOPIC}")
    print(f"🌐 Server: http://localhost:{config.FLASK_PORT}")
    print("=" * 60)
    
    # Start MQTT in background
    start_mqtt()
    
    socketio.run(
        app, 
        debug=config.DEBUG_MODE, 
        host=config.FLASK_HOST, 
        port=config.FLASK_PORT, 
        allow_unsafe_werkzeug=True
    )
