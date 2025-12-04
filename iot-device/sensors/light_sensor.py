"""
TSL2561 Light Sensor Module
Measures ambient light level in lux
"""

import logging

logger = logging.getLogger(__name__)

class LightSensor:
    """TSL2561 light sensor interface"""
    
    def __init__(self, i2c_address: int = 0x39):
        """Initialize TSL2561 light sensor"""
        self.i2c_address = i2c_address
        self.sensor_available = False
        
        try:
            import board
            import adafruit_tsl2561
            
            i2c = board.I2C()
            self.sensor = adafruit_tsl2561.TSL2561(i2c, address=i2c_address)
            self.sensor_available = True
            logger.info(f"✅ TSL2561 light sensor initialized at 0x{i2c_address:02X}")
        except ImportError:
            logger.warning("⚠️ adafruit_tsl2561 not available - using mock mode")
        except Exception as e:
            logger.error(f"Failed to initialize TSL2561 sensor: {e}")
    
    def read_lux(self) -> float:
        """Read ambient light level in lux"""
        if self.sensor_available:
            try:
                lux = self.sensor.lux
                if lux is not None:
                    return round(lux, 2)
                return 250.0  # Default
            except Exception as e:
                logger.error(f"Error reading light sensor: {e}")
                return 250.0
        else:
            # Mock data
            import random
            return round(random.uniform(50.0, 500.0), 2)
    
    def cleanup(self):
        """Clean up sensor resources"""
        if self.sensor_available:
            logger.info("🧹 Light sensor cleaned up")
