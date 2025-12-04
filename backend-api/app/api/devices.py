"""
Devices API endpoints
Handles IoT device registration and management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter()

# Request/Response models
class DeviceRegister(BaseModel):
    device_name: str
    device_type: str
    mac_address: str

class DeviceResponse(BaseModel):
    device_id: str
    device_name: str
    status: str
    mqtt_topic: str

class DeviceCommand(BaseModel):
    command: str
    parameters: Optional[Dict[str, Any]] = None

class DeviceInfo(BaseModel):
    device_id: str
    device_name: str
    device_type: str
    status: str
    last_seen: Optional[datetime] = None
    mqtt_topic: str

# Mock devices database
devices_db = {}

@router.post("/register", response_model=DeviceResponse, status_code=201)
async def register_device(device_data: DeviceRegister):
    """Register a new IoT device"""
    
    # Check if device already exists
    for device_id, device in devices_db.items():
        if device["mac_address"] == device_data.mac_address:
            raise HTTPException(
                status_code=400,
                detail="Device with this MAC address already registered"
            )
    
    # Create device
    device_id = f"device-{len(devices_db) + 1:03d}"
    mqtt_topic = f"wellbeing/sensors/{device_id}"
    
    devices_db[device_id] = {
        "device_id": device_id,
        "device_name": device_data.device_name,
        "device_type": device_data.device_type,
        "mac_address": device_data.mac_address,
        "status": "registered",
        "mqtt_topic": mqtt_topic,
        "created_at": datetime.utcnow(),
        "last_seen": None
    }
    
    return DeviceResponse(
        device_id=device_id,
        device_name=device_data.device_name,
        status="registered",
        mqtt_topic=mqtt_topic
    )

@router.get("", response_model=List[DeviceInfo])
async def list_devices():
    """List all registered IoT devices"""
    
    return [
        DeviceInfo(
            device_id=device["device_id"],
            device_name=device["device_name"],
            device_type=device["device_type"],
            status=device["status"],
            last_seen=device.get("last_seen"),
            mqtt_topic=device["mqtt_topic"]
        )
        for device in devices_db.values()
    ]

@router.get("/{device_id}")
async def get_device(device_id: str):
    """Get specific device information"""
    
    device = devices_db.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return device

@router.post("/{device_id}/command")
async def send_device_command(device_id: str, command: DeviceCommand):
    """Send command to IoT device"""
    
    device = devices_db.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # TODO: Publish command to MQTT
    # mqtt_service.publish(f"wellbeing/commands/{device_id}", command.dict())
    
    command_id = f"cmd-{len(devices_db) * 100 + 1}"
    
    return {
        "status": "command_sent",
        "device_id": device_id,
        "command_id": command_id,
        "command": command.command,
        "timestamp": datetime.utcnow()
    }

@router.delete("/{device_id}")
async def unregister_device(device_id: str):
    """Unregister a device"""
    
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    
    del devices_db[device_id]
    
    return {
        "status": "unregistered",
        "device_id": device_id
    }

@router.post("/{device_id}/heartbeat")
async def device_heartbeat(device_id: str):
    """Update device last seen timestamp"""
    
    device = devices_db.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device["last_seen"] = datetime.utcnow()
    device["status"] = "online"
    
    return {
        "status": "acknowledged",
        "device_id": device_id,
        "timestamp": device["last_seen"]
    }
