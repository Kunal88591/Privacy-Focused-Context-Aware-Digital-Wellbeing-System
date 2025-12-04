"""
Noise Sensor Module
Measures ambient sound level using USB microphone
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)

class NoiseSensor:
    """USB microphone noise level sensor"""
    
    def __init__(self, device_index: int = None):
        """Initialize noise sensor"""
        self.device_index = device_index
        self.audio_available = False
        
        try:
            import pyaudio
            self.pyaudio = pyaudio
            self.audio = pyaudio.PyAudio()
            self.audio_available = True
            logger.info("✅ Noise sensor initialized")
        except ImportError:
            logger.warning("⚠️ PyAudio not available - using mock mode")
        except Exception as e:
            logger.error(f"Failed to initialize noise sensor: {e}")
    
    def read_db(self) -> float:
        """Read ambient noise level in decibels"""
        if self.audio_available:
            try:
                # Record a short audio sample
                CHUNK = 1024
                FORMAT = self.pyaudio.paInt16
                CHANNELS = 1
                RATE = 44100
                RECORD_SECONDS = 0.1
                
                stream = self.audio.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=self.device_index
                )
                
                frames = []
                for _ in range(int(RATE / CHUNK * RECORD_SECONDS)):
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    frames.append(data)
                
                stream.stop_stream()
                stream.close()
                
                # Convert to numpy array
                audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
                
                # Calculate RMS (Root Mean Square)
                rms = np.sqrt(np.mean(audio_data**2))
                
                # Convert to decibels (approximate)
                if rms > 0:
                    db = 20 * np.log10(rms) - 90  # Calibration offset
                    return round(max(0, min(120, db)), 2)  # Clamp between 0-120 dB
                return 30.0  # Silent
                
            except Exception as e:
                logger.error(f"Error reading noise sensor: {e}")
                return 40.0  # Default
        else:
            # Mock data
            import random
            return round(random.uniform(30.0, 80.0), 2)
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.audio_available:
            try:
                self.audio.terminate()
                logger.info("🧹 Noise sensor cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up noise sensor: {e}")
