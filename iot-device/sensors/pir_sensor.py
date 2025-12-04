"""
PIR Motion Sensor Module
Detects motion using HC-SR501 PIR sensor
"""

import logging

logger = logging.getLogger(__name__)

class PIRSensor:
    """PIR motion sensor interface"""
    
    def __init__(self, gpio_pin: int = 17):
        """Initialize PIR sensor"""
        self.gpio_pin = gpio_pin
        self.gpio_available = False
        
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.GPIO.setmode(GPIO.BCM)
            self.GPIO.setup(self.gpio_pin, GPIO.IN)
            self.gpio_available = True
            logger.info(f"✅ PIR sensor initialized on GPIO {self.gpio_pin}")
        except ImportError:
            logger.warning("⚠️ RPi.GPIO not available - using mock mode")
        except Exception as e:
            logger.error(f"Failed to initialize PIR sensor: {e}")
    
    def read(self) -> bool:
        """Read motion detection state"""
        if self.gpio_available:
            try:
                return bool(self.GPIO.input(self.gpio_pin))
            except Exception as e:
                logger.error(f"Error reading PIR sensor: {e}")
                return False
        else:
            # Mock data for testing without hardware
            import random
            return random.choice([True, False])
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if self.gpio_available:
            try:
                self.GPIO.cleanup(self.gpio_pin)
                logger.info("🧹 PIR sensor GPIO cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up PIR sensor: {e}")
