"""
IoT Device - MQTT Client
Raspberry Pi sensor monitoring and automation
"""

import paho.mqtt.client as mqtt
import json
import time
import logging
from datetime import datetime
import os
from dotenv import load_dotenv
from sensors.sensor_manager import SensorManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WellbeingIoTDevice:
    """Main IoT device class for environmental monitoring"""
    
    def __init__(self):
        """Initialize the IoT device"""
        self.mqtt_client = None
        self.broker_host = os.getenv('MQTT_BROKER_HOST', 'localhost')
        self.broker_port = int(os.getenv('MQTT_BROKER_PORT', 1883))
        self.topic_prefix = os.getenv('MQTT_TOPIC_PREFIX', 'wellbeing')
        self.device_id = os.getenv('DEVICE_ID', 'iot-device-001')
        
        # Initialize sensor manager
        self.sensors = SensorManager()
        
        # Sensor readings
        self.current_state = {
            'noise_level': 0.0,
            'light_level': 0.0,
            'motion_detected': False,
            'temperature': 0.0,
            'humidity': 0.0,
            'timestamp': None
        }
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            logger.info(f"✅ Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            # Subscribe to command topics
            client.subscribe(f"{self.topic_prefix}/commands/{self.device_id}/#")
            logger.info(f"📡 Subscribed to {self.topic_prefix}/commands/{self.device_id}/#")
        else:
            logger.error(f"❌ Connection failed with code {rc}")
    
    def on_message(self, client, userdata, msg):
        """Callback when message is received"""
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"📨 Received message on {msg.topic}: {payload}")
            self.handle_command(payload)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode message: {msg.payload}")
    
    def handle_command(self, command):
        """Handle commands from backend"""
        cmd_type = command.get('type')
        
        if cmd_type == 'activate_focus_mode':
            logger.info("🎯 Activating focus mode...")
            # TODO: Trigger noise cancellation, adjust lighting
        elif cmd_type == 'suggest_break':
            logger.info("☕ Suggesting break to user...")
            # TODO: Send break reminder via connected devices
        elif cmd_type == 'adjust_environment':
            logger.info("🌡️ Adjusting environment...")
            # TODO: Adjust smart devices (lights, fans, etc.)
        else:
            logger.warning(f"Unknown command type: {cmd_type}")
    
    def read_sensors(self):
        """Read all sensor values"""
        self.current_state = self.sensors.read_all()
        return self.current_state
    
    def analyze_environment(self):
        """Analyze environment and get recommendations"""
        analysis = self.sensors.analyze_environment()
        
        # Send recommendations if any issues detected
        if analysis['recommendations']:
            for rec in analysis['recommendations']:
                self.publish_alert(rec)
        
        return analysis
    
    def publish_sensor_data(self):
        """Publish sensor readings to MQTT broker"""
        sensor_data = self.read_sensors()
        topic = f"{self.topic_prefix}/sensors/{self.device_id}"
        
        try:
            self.mqtt_client.publish(
                topic,
                json.dumps(sensor_data),
                qos=1
            )
            logger.info(f"📤 Published sensor data: {sensor_data}")
        except Exception as e:
            logger.error(f"Failed to publish sensor data: {e}")
    
    def publish_alert(self, alert: dict):
        """Publish environmental alert"""
        topic = f"{self.topic_prefix}/alerts/{self.device_id}"
        
        try:
            self.mqtt_client.publish(
                topic,
                json.dumps(alert),
                qos=1
            )
            logger.info(f"🚨 Published alert: {alert['message']}")
        except Exception as e:
            logger.error(f"Failed to publish alert: {e}")
    
    def connect(self):
        """Connect to MQTT broker"""
        self.mqtt_client = mqtt.Client(client_id=self.device_id)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        
        # Set username/password if provided
        username = os.getenv('MQTT_USERNAME')
        password = os.getenv('MQTT_PASSWORD')
        if username and password:
            self.mqtt_client.username_pw_set(username, password)
        
        try:
            self.mqtt_client.connect(self.broker_host, self.broker_port, 60)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def run(self):
        """Main run loop"""
        if not self.connect():
            logger.error("Failed to connect. Exiting...")
            return
        
        logger.info("🚀 IoT Device started successfully")
        logger.info("📊 Starting sensor monitoring...")
        
        # Start MQTT loop in background
        self.mqtt_client.loop_start()
        
        try:
            # Main sensor reading loop
            while True:
                self.publish_sensor_data()
                time.sleep(5)  # Publish every 5 seconds
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutting down IoT device...")
            self.sensors.cleanup()
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

if __name__ == "__main__":
    device = WellbeingIoTDevice()
    device.run()
