"""
Sensor Manager
Aggregates all sensor readings into a single interface
"""

import logging
from .pir_sensor import PIRSensor
from .dht_sensor import DHTSensor
from .light_sensor import LightSensor
from .noise_sensor import NoiseSensor
from datetime import datetime

logger = logging.getLogger(__name__)

class SensorManager:
    """Manages all sensors and aggregates readings"""
    
    def __init__(self):
        """Initialize all sensors"""
        logger.info("🔧 Initializing sensor manager...")
        
        self.pir = PIRSensor(gpio_pin=17)
        self.dht = DHTSensor(gpio_pin=4)
        self.light = LightSensor(i2c_address=0x39)
        self.noise = NoiseSensor()
        
        logger.info("✅ Sensor manager initialized")
    
    def read_all(self) -> dict:
        """Read all sensors and return aggregated data"""
        try:
            data = {
                'motion_detected': self.pir.read(),
                'temperature': self.dht.read_temperature(),
                'humidity': self.dht.read_humidity(),
                'light_level': self.light.read_lux(),
                'noise_level': self.noise.read_db(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.debug(f"📊 Sensor readings: {data}")
            return data
        except Exception as e:
            logger.error(f"Error reading sensors: {e}")
            return self._get_default_readings()
    
    def _get_default_readings(self) -> dict:
        """Return default readings in case of error"""
        return {
            'motion_detected': False,
            'temperature': 22.0,
            'humidity': 45.0,
            'light_level': 250.0,
            'noise_level': 40.0,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def analyze_environment(self) -> dict:
        """Analyze environment and provide recommendations"""
        data = self.read_all()
        
        recommendations = []
        issues = []
        
        # Check noise level
        if data['noise_level'] > 70:
            issues.append("high_noise")
            recommendations.append({
                'type': 'noise',
                'severity': 'high',
                'message': 'Environment is too noisy for focus work',
                'suggestion': 'Enable noise cancellation or move to quieter space'
            })
        
        # Check lighting
        if data['light_level'] < 200:
            issues.append("low_light")
            recommendations.append({
                'type': 'lighting',
                'severity': 'medium',
                'message': 'Lighting is insufficient',
                'suggestion': 'Increase ambient lighting or desk lamp'
            })
        elif data['light_level'] > 1000:
            issues.append("excessive_light")
            recommendations.append({
                'type': 'lighting',
                'severity': 'low',
                'message': 'Lighting is too bright',
                'suggestion': 'Reduce screen brightness or close blinds'
            })
        
        # Check temperature
        if data['temperature'] < 18 or data['temperature'] > 28:
            issues.append("uncomfortable_temperature")
            recommendations.append({
                'type': 'temperature',
                'severity': 'medium',
                'message': f"Temperature is {data['temperature']}°C (uncomfortable)",
                'suggestion': 'Adjust room temperature to 20-26°C range'
            })
        
        # Check motion (for break reminders)
        if not data['motion_detected']:
            recommendations.append({
                'type': 'activity',
                'severity': 'low',
                'message': 'No movement detected recently',
                'suggestion': 'Consider taking a short break'
            })
        
        return {
            'sensor_data': data,
            'issues': issues,
            'recommendations': recommendations,
            'environment_score': self._calculate_environment_score(data)
        }
    
    def _calculate_environment_score(self, data: dict) -> int:
        """Calculate environment quality score (0-100)"""
        score = 100
        
        # Penalize for noise
        if data['noise_level'] > 70:
            score -= 30
        elif data['noise_level'] > 60:
            score -= 15
        
        # Penalize for poor lighting
        if data['light_level'] < 200:
            score -= 20
        elif data['light_level'] > 1000:
            score -= 10
        
        # Penalize for uncomfortable temperature
        if data['temperature'] < 18 or data['temperature'] > 28:
            score -= 25
        elif data['temperature'] < 20 or data['temperature'] > 26:
            score -= 10
        
        return max(0, min(100, score))
    
    def cleanup(self):
        """Clean up all sensor resources"""
        logger.info("🧹 Cleaning up sensors...")
        self.pir.cleanup()
        self.dht.cleanup()
        self.light.cleanup()
        self.noise.cleanup()
        logger.info("✅ Sensors cleaned up")
