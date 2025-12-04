"""
DHT22 Temperature and Humidity Sensor Module
"""

import logging

logger = logging.getLogger(__name__)

class DHTSensor:
    """DHT22 temperature and humidity sensor interface"""
    
    def __init__(self, gpio_pin: int = 4):
        """Initialize DHT22 sensor"""
        self.gpio_pin = gpio_pin
        self.dht_available = False
        
        try:
            import adafruit_dht
            import board
            
            # Map GPIO pin number to board pin
            pin_map = {
                4: board.D4,
                17: board.D17,
                27: board.D27,
                22: board.D22,
            }
            
            board_pin = pin_map.get(gpio_pin, board.D4)
            self.dht = adafruit_dht.DHT22(board_pin)
            self.dht_available = True
            logger.info(f"✅ DHT22 sensor initialized on GPIO {self.gpio_pin}")
        except ImportError:
            logger.warning("⚠️ adafruit_dht not available - using mock mode")
        except Exception as e:
            logger.error(f"Failed to initialize DHT22 sensor: {e}")
    
    def read_temperature(self) -> float:
        """Read temperature in Celsius"""
        if self.dht_available:
            try:
                temp = self.dht.temperature
                if temp is not None:
                    return round(temp, 1)
                return 22.0  # Default
            except RuntimeError:
                # DHT sensors occasionally fail to read
                return 22.0
            except Exception as e:
                logger.error(f"Error reading temperature: {e}")
                return 22.0
        else:
            # Mock data
            import random
            return round(random.uniform(18.0, 28.0), 1)
    
    def read_humidity(self) -> float:
        """Read humidity percentage"""
        if self.dht_available:
            try:
                humidity = self.dht.humidity
                if humidity is not None:
                    return round(humidity, 1)
                return 45.0  # Default
            except RuntimeError:
                return 45.0
            except Exception as e:
                logger.error(f"Error reading humidity: {e}")
                return 45.0
        else:
            # Mock data
            import random
            return round(random.uniform(30.0, 70.0), 1)
    
    def cleanup(self):
        """Clean up sensor resources"""
        if self.dht_available:
            try:
                self.dht.exit()
                logger.info("🧹 DHT22 sensor cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up DHT sensor: {e}")
