"""
IoT Automation Service
Handles automated responses to sensor data and environmental conditions
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class AutomationType(str, Enum):
    NOISE_DETECTION = "noise_detection"
    LIGHTING_ADJUSTMENT = "lighting_adjustment"
    BREAK_REMINDER = "break_reminder"
    FOCUS_MODE = "focus_mode"
    TEMPERATURE_ALERT = "temperature_alert"


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IoTAutomationService:
    """Manages automated responses to IoT sensor data"""
    
    def __init__(self):
        self.automation_rules = []
        self.automation_history = []
        self.last_motion_time = None
        self.sitting_duration_threshold = 3600  # 1 hour in seconds
        self.noise_threshold = 70  # dB
        self.low_light_threshold = 200  # lux
        self.high_light_threshold = 1000  # lux
        self.temp_low_threshold = 18  # °C
        self.temp_high_threshold = 28  # °C
        
    async def process_sensor_data(self, sensor_data: Dict) -> Dict:
        """
        Process incoming sensor data and trigger automations
        
        Args:
            sensor_data: Dictionary containing sensor readings
            
        Returns:
            Dictionary with triggered automations and recommendations
        """
        triggered_automations = []
        
        # Check noise level
        noise_automation = await self._check_noise_level(sensor_data.get('noise_level', 0))
        if noise_automation:
            triggered_automations.append(noise_automation)
        
        # Check lighting
        lighting_automation = await self._check_lighting(sensor_data.get('light_level', 0))
        if lighting_automation:
            triggered_automations.append(lighting_automation)
        
        # Check for prolonged sitting
        motion_automation = await self._check_motion(
            sensor_data.get('motion_detected', False),
            sensor_data.get('timestamp')
        )
        if motion_automation:
            triggered_automations.append(motion_automation)
        
        # Check temperature
        temp_automation = await self._check_temperature(sensor_data.get('temperature', 22))
        if temp_automation:
            triggered_automations.append(temp_automation)
        
        # Log automations
        for automation in triggered_automations:
            self._log_automation(automation)
        
        return {
            'sensor_data': sensor_data,
            'automations_triggered': triggered_automations,
            'total_automations': len(triggered_automations),
            'processed_at': datetime.utcnow().isoformat()
        }
    
    async def _check_noise_level(self, noise_level: float) -> Optional[Dict]:
        """Check noise level and trigger noise cancellation suggestion"""
        if noise_level > self.noise_threshold:
            severity = AlertSeverity.HIGH if noise_level > 80 else AlertSeverity.MEDIUM
            
            return {
                'type': AutomationType.NOISE_DETECTION,
                'severity': severity,
                'trigger_value': noise_level,
                'threshold': self.noise_threshold,
                'message': f'High noise detected ({noise_level:.1f} dB)',
                'action': 'suggest_noise_cancellation',
                'recommendations': [
                    'Enable noise-canceling headphones',
                    'Move to a quieter location',
                    'Activate Do Not Disturb mode',
                    'Use white noise or ambient sounds'
                ],
                'timestamp': datetime.utcnow().isoformat()
            }
        return None
    
    async def _check_lighting(self, light_level: float) -> Optional[Dict]:
        """Check lighting and suggest adjustments"""
        if light_level < self.low_light_threshold:
            return {
                'type': AutomationType.LIGHTING_ADJUSTMENT,
                'severity': AlertSeverity.MEDIUM,
                'trigger_value': light_level,
                'threshold': self.low_light_threshold,
                'message': f'Low light detected ({light_level:.0f} lux)',
                'action': 'increase_lighting',
                'recommendations': [
                    'Turn on desk lamp',
                    'Increase ambient lighting',
                    'Move closer to natural light source',
                    'Adjust screen brightness'
                ],
                'timestamp': datetime.utcnow().isoformat()
            }
        elif light_level > self.high_light_threshold:
            return {
                'type': AutomationType.LIGHTING_ADJUSTMENT,
                'severity': AlertSeverity.LOW,
                'trigger_value': light_level,
                'threshold': self.high_light_threshold,
                'message': f'Excessive light detected ({light_level:.0f} lux)',
                'action': 'reduce_lighting',
                'recommendations': [
                    'Close blinds or curtains',
                    'Reduce screen brightness',
                    'Use blue light filter',
                    'Reposition workspace'
                ],
                'timestamp': datetime.utcnow().isoformat()
            }
        return None
    
    async def _check_motion(self, motion_detected: bool, timestamp: str = None) -> Optional[Dict]:
        """Check for prolonged sitting and trigger break reminder"""
        current_time = datetime.utcnow()
        
        if motion_detected:
            self.last_motion_time = current_time
            return None
        
        # If no motion and we have a last motion time
        if self.last_motion_time:
            sitting_duration = (current_time - self.last_motion_time).total_seconds()
            
            if sitting_duration > self.sitting_duration_threshold:
                return {
                    'type': AutomationType.BREAK_REMINDER,
                    'severity': AlertSeverity.MEDIUM,
                    'trigger_value': sitting_duration,
                    'threshold': self.sitting_duration_threshold,
                    'message': f'You\'ve been sitting for {sitting_duration/60:.0f} minutes',
                    'action': 'suggest_break',
                    'recommendations': [
                        'Stand up and stretch',
                        'Take a 5-minute walk',
                        'Do some light exercises',
                        'Get a drink of water',
                        'Look away from screen (20-20-20 rule)'
                    ],
                    'sitting_duration_minutes': sitting_duration / 60,
                    'timestamp': datetime.utcnow().isoformat()
                }
        else:
            # Initialize last motion time
            self.last_motion_time = current_time
        
        return None
    
    async def _check_temperature(self, temperature: float) -> Optional[Dict]:
        """Check temperature and suggest adjustments"""
        if temperature < self.temp_low_threshold:
            return {
                'type': AutomationType.TEMPERATURE_ALERT,
                'severity': AlertSeverity.MEDIUM,
                'trigger_value': temperature,
                'threshold': self.temp_low_threshold,
                'message': f'Temperature is too low ({temperature:.1f}°C)',
                'action': 'increase_temperature',
                'recommendations': [
                    'Adjust thermostat to 20-26°C',
                    'Dress warmer',
                    'Close windows',
                    'Use space heater if available'
                ],
                'timestamp': datetime.utcnow().isoformat()
            }
        elif temperature > self.temp_high_threshold:
            return {
                'type': AutomationType.TEMPERATURE_ALERT,
                'severity': AlertSeverity.MEDIUM,
                'trigger_value': temperature,
                'threshold': self.temp_high_threshold,
                'message': f'Temperature is too high ({temperature:.1f}°C)',
                'action': 'decrease_temperature',
                'recommendations': [
                    'Adjust thermostat to 20-26°C',
                    'Open windows for ventilation',
                    'Use fan or air conditioning',
                    'Reduce direct sunlight'
                ],
                'timestamp': datetime.utcnow().isoformat()
            }
        return None
    
    async def schedule_focus_mode(self, start_time: str, duration_minutes: int, 
                                 auto_adjustments: Dict = None) -> Dict:
        """
        Schedule automated focus mode activation with environment adjustments
        
        Args:
            start_time: ISO format datetime string
            duration_minutes: Duration of focus session
            auto_adjustments: Optional dict with lighting, noise preferences
            
        Returns:
            Scheduled automation details
        """
        automation = {
            'type': AutomationType.FOCUS_MODE,
            'scheduled_for': start_time,
            'duration_minutes': duration_minutes,
            'auto_adjustments': auto_adjustments or {
                'enable_dnd': True,
                'optimal_lighting': 400,  # lux
                'max_noise_level': 50,  # dB
                'block_notifications': True
            },
            'actions': [
                'Enable Do Not Disturb mode',
                'Suggest optimal lighting',
                'Monitor noise levels',
                'Block distracting apps'
            ],
            'created_at': datetime.utcnow().isoformat(),
            'status': 'scheduled'
        }
        
        self.automation_rules.append(automation)
        logger.info(f"Scheduled focus mode for {start_time}, duration: {duration_minutes} min")
        
        return automation
    
    async def activate_focus_mode(self, session_id: str = None) -> Dict:
        """Immediately activate focus mode with environmental optimizations"""
        activation = {
            'type': AutomationType.FOCUS_MODE,
            'session_id': session_id or f"focus_{int(datetime.utcnow().timestamp())}",
            'activated_at': datetime.utcnow().isoformat(),
            'status': 'active',
            'adjustments_applied': [
                'DND mode enabled',
                'Notifications blocked',
                'Optimal lighting suggested',
                'Noise monitoring active'
            ],
            'recommendations': [
                'Close unnecessary browser tabs',
                'Silence phone',
                'Use noise-canceling headphones',
                'Set timer for focused work session'
            ]
        }
        
        self._log_automation(activation)
        logger.info(f"Focus mode activated: {activation['session_id']}")
        
        return activation
    
    async def get_automation_stats(self) -> Dict:
        """Get automation statistics and insights"""
        if not self.automation_history:
            return {
                'total_automations': 0,
                'by_type': {},
                'by_severity': {},
                'most_common': None
            }
        
        by_type = {}
        by_severity = {}
        
        for automation in self.automation_history:
            # Count by type
            auto_type = automation.get('type')
            by_type[auto_type] = by_type.get(auto_type, 0) + 1
            
            # Count by severity
            severity = automation.get('severity')
            if severity:
                by_severity[severity] = by_severity.get(severity, 0) + 1
        
        most_common = max(by_type, key=by_type.get) if by_type else None
        
        return {
            'total_automations': len(self.automation_history),
            'by_type': by_type,
            'by_severity': by_severity,
            'most_common_automation': most_common,
            'last_automation': self.automation_history[-1] if self.automation_history else None
        }
    
    async def get_automation_history(self, limit: int = 50) -> List[Dict]:
        """Get recent automation history"""
        return self.automation_history[-limit:]
    
    async def configure_thresholds(self, thresholds: Dict) -> Dict:
        """Update automation thresholds"""
        if 'noise_threshold' in thresholds:
            self.noise_threshold = thresholds['noise_threshold']
        if 'low_light_threshold' in thresholds:
            self.low_light_threshold = thresholds['low_light_threshold']
        if 'high_light_threshold' in thresholds:
            self.high_light_threshold = thresholds['high_light_threshold']
        if 'sitting_duration_threshold' in thresholds:
            self.sitting_duration_threshold = thresholds['sitting_duration_threshold']
        if 'temp_low_threshold' in thresholds:
            self.temp_low_threshold = thresholds['temp_low_threshold']
        if 'temp_high_threshold' in thresholds:
            self.temp_high_threshold = thresholds['temp_high_threshold']
        
        logger.info(f"Thresholds updated: {thresholds}")
        
        return {
            'noise_threshold': self.noise_threshold,
            'low_light_threshold': self.low_light_threshold,
            'high_light_threshold': self.high_light_threshold,
            'sitting_duration_threshold': self.sitting_duration_threshold,
            'temp_low_threshold': self.temp_low_threshold,
            'temp_high_threshold': self.temp_high_threshold,
            'updated_at': datetime.utcnow().isoformat()
        }
    
    async def get_current_thresholds(self) -> Dict:
        """Get current automation thresholds"""
        return {
            'noise_threshold': self.noise_threshold,
            'low_light_threshold': self.low_light_threshold,
            'high_light_threshold': self.high_light_threshold,
            'sitting_duration_threshold': self.sitting_duration_threshold,
            'temp_low_threshold': self.temp_low_threshold,
            'temp_high_threshold': self.temp_high_threshold
        }
    
    def _log_automation(self, automation: Dict):
        """Log automation to history"""
        self.automation_history.append({
            **automation,
            'logged_at': datetime.utcnow().isoformat()
        })
        
        # Keep history limited to last 1000 entries
        if len(self.automation_history) > 1000:
            self.automation_history = self.automation_history[-1000:]


# Global singleton instance
iot_automation = IoTAutomationService()
