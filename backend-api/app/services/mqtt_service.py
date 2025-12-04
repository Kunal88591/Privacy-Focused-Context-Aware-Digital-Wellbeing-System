"""
MQTT Service
Handles pub/sub messaging for real-time communication
"""

import paho.mqtt.client as mqtt
import json
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class MQTTService:
    """MQTT client for real-time messaging"""
    
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        """Initialize MQTT service"""
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = None
        self.connected = False
        self.subscriptions = {}
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            logger.info(f"✅ Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.connected = True
            
            # Resubscribe to all topics
            for topic in self.subscriptions.keys():
                client.subscribe(topic)
                logger.info(f"📡 Resubscribed to {topic}")
        else:
            logger.error(f"❌ Connection failed with code {rc}")
            self.connected = False
    
    def on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        logger.warning(f"⚠️ Disconnected from MQTT broker (code: {rc})")
        self.connected = False
    
    def on_message(self, client, userdata, msg):
        """Callback when message is received"""
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"📨 Received message on {msg.topic}: {payload}")
            
            # Call registered callback if exists
            callback = self.subscriptions.get(msg.topic)
            if callback:
                callback(msg.topic, payload)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode message: {msg.payload}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def connect(self, username: Optional[str] = None, password: Optional[str] = None):
        """Connect to MQTT broker"""
        try:
            self.client = mqtt.Client(client_id="backend-api-server")
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message
            
            # Set authentication if provided
            if username and password:
                self.client.username_pw_set(username, password)
            
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            logger.info("🔄 MQTT connection initiated...")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("🛑 Disconnected from MQTT broker")
    
    def publish(self, topic: str, payload: dict, qos: int = 1):
        """Publish message to topic"""
        if not self.connected:
            logger.warning("⚠️ Not connected to MQTT broker")
            return False
        
        try:
            message = json.dumps(payload)
            result = self.client.publish(topic, message, qos=qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"📤 Published to {topic}: {payload}")
                return True
            else:
                logger.error(f"Failed to publish message (code: {result.rc})")
                return False
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            return False
    
    def subscribe(self, topic: str, callback: Optional[Callable] = None):
        """Subscribe to topic with optional callback"""
        if not self.client:
            logger.error("❌ MQTT client not initialized")
            return False
        
        try:
            self.client.subscribe(topic)
            self.subscriptions[topic] = callback
            logger.info(f"📡 Subscribed to {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to {topic}: {e}")
            return False
    
    def unsubscribe(self, topic: str):
        """Unsubscribe from topic"""
        if self.client:
            self.client.unsubscribe(topic)
            if topic in self.subscriptions:
                del self.subscriptions[topic]
            logger.info(f"📡 Unsubscribed from {topic}")
    
    # Convenience methods for common topics
    
    def publish_sensor_alert(self, device_id: str, alert_type: str, message: str, data: dict = None):
        """Publish sensor alert to mobile app"""
        topic = f"wellbeing/alerts/{device_id}"
        payload = {
            "type": alert_type,
            "message": message,
            "data": data or {},
            "timestamp": None  # Will be set by serializer
        }
        return self.publish(topic, payload)
    
    def publish_command(self, device_id: str, command: str, parameters: dict = None):
        """Send command to IoT device"""
        topic = f"wellbeing/commands/{device_id}"
        payload = {
            "command": command,
            "parameters": parameters or {},
            "timestamp": None
        }
        return self.publish(topic, payload)
    
    def subscribe_to_sensors(self, device_id: str, callback: Callable):
        """Subscribe to sensor data from device"""
        topic = f"wellbeing/sensors/{device_id}"
        return self.subscribe(topic, callback)
    
    def publish_notification(self, user_id: str, notification_type: str, message: str):
        """Send notification to mobile app"""
        topic = f"wellbeing/notifications/{user_id}"
        payload = {
            "type": notification_type,
            "message": message,
            "timestamp": None
        }
        return self.publish(topic, payload)

# Global MQTT service instance
mqtt_service = MQTTService()

def get_mqtt_service() -> MQTTService:
    """Get global MQTT service instance"""
    return mqtt_service
