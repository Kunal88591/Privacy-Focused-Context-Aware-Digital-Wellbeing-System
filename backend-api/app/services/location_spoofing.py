"""
Location Spoofing Service
Provides location privacy by spoofing GPS coordinates
"""

import random
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import math

logger = logging.getLogger(__name__)


class LocationMode(str, Enum):
    REAL = "real"
    SPOOFED = "spoofed"
    APPROXIMATE = "approximate"  # Fuzzy location (e.g., city-level)
    RANDOM = "random"


class LocationSpoofing:
    """Manage location spoofing and privacy"""
    
    def __init__(self):
        self.mode = LocationMode.REAL
        self.spoofed_location = None
        self.real_location = None
        self.approximation_radius_km = 5.0  # For approximate mode
        self.location_history = []
        
    async def set_mode(self, mode: LocationMode) -> Dict:
        """Set location privacy mode"""
        self.mode = mode
        logger.info(f"Location mode set to: {mode}")
        
        return {
            "mode": mode,
            "description": self._get_mode_description(mode),
            "changed_at": datetime.now().isoformat()
        }
    
    def _get_mode_description(self, mode: LocationMode) -> str:
        """Get description for location mode"""
        descriptions = {
            LocationMode.REAL: "Your real GPS location is shared",
            LocationMode.SPOOFED: "A fake location is shared instead of your real location",
            LocationMode.APPROXIMATE: f"Your location is approximated to ~{self.approximation_radius_km}km radius",
            LocationMode.RANDOM: "A random location is generated each time"
        }
        return descriptions.get(mode, "Unknown mode")
    
    async def set_real_location(self, latitude: float, longitude: float) -> Dict:
        """Set the user's real location (for tracking)"""
        self.real_location = {
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Real location updated: {latitude}, {longitude}")
        
        return {
            "status": "updated",
            "real_location_set": True
        }
    
    async def set_spoofed_location(self, latitude: float, longitude: float) -> Dict:
        """Set a specific spoofed location"""
        self.spoofed_location = {
            "latitude": latitude,
            "longitude": longitude,
            "set_at": datetime.now().isoformat()
        }
        
        self.mode = LocationMode.SPOOFED
        
        logger.info(f"Spoofed location set to: {latitude}, {longitude}")
        
        return {
            "mode": self.mode,
            "spoofed_location": self.spoofed_location,
            "message": "Location spoofing enabled"
        }
    
    async def get_location(self) -> Dict:
        """Get location based on current mode"""
        
        if self.mode == LocationMode.REAL:
            return await self._get_real_location()
        
        elif self.mode == LocationMode.SPOOFED:
            return await self._get_spoofed_location()
        
        elif self.mode == LocationMode.APPROXIMATE:
            return await self._get_approximate_location()
        
        elif self.mode == LocationMode.RANDOM:
            return await self._get_random_location()
        
        # Default to real
        return await self._get_real_location()
    
    async def _get_real_location(self) -> Dict:
        """Get real GPS location"""
        if not self.real_location:
            # Simulate getting device location
            self.real_location = {
                "latitude": 37.7749,  # San Francisco
                "longitude": -122.4194,
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "mode": LocationMode.REAL,
            "latitude": self.real_location["latitude"],
            "longitude": self.real_location["longitude"],
            "accuracy": "precise",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_spoofed_location(self) -> Dict:
        """Get spoofed location"""
        if not self.spoofed_location:
            # Default spoofed location
            self.spoofed_location = {
                "latitude": 40.7128,  # New York
                "longitude": -74.0060,
                "set_at": datetime.now().isoformat()
            }
        
        return {
            "mode": LocationMode.SPOOFED,
            "latitude": self.spoofed_location["latitude"],
            "longitude": self.spoofed_location["longitude"],
            "accuracy": "spoofed",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_approximate_location(self) -> Dict:
        """Get approximated location (fuzzy)"""
        if not self.real_location:
            await self._get_real_location()
        
        # Add random offset within radius
        lat_offset = random.uniform(-self.approximation_radius_km, self.approximation_radius_km) / 111  # ~111km per degree
        lon_offset = random.uniform(-self.approximation_radius_km, self.approximation_radius_km) / (111 * math.cos(math.radians(self.real_location["latitude"])))
        
        approx_lat = self.real_location["latitude"] + lat_offset
        approx_lon = self.real_location["longitude"] + lon_offset
        
        return {
            "mode": LocationMode.APPROXIMATE,
            "latitude": round(approx_lat, 4),
            "longitude": round(approx_lon, 4),
            "accuracy": f"~{self.approximation_radius_km}km radius",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_random_location(self) -> Dict:
        """Get completely random location"""
        # Random coordinates within reasonable bounds
        random_lat = random.uniform(-85, 85)  # Avoid poles
        random_lon = random.uniform(-180, 180)
        
        return {
            "mode": LocationMode.RANDOM,
            "latitude": round(random_lat, 6),
            "longitude": round(random_lon, 6),
            "accuracy": "random",
            "timestamp": datetime.now().isoformat()
        }
    
    async def select_city_location(self, city: str) -> Dict:
        """Set spoofed location to a specific city"""
        # Predefined city coordinates
        cities = {
            "new_york": (40.7128, -74.0060),
            "london": (51.5074, -0.1278),
            "tokyo": (35.6762, 139.6503),
            "paris": (48.8566, 2.3522),
            "sydney": (-33.8688, 151.2093),
            "dubai": (25.2048, 55.2708),
            "singapore": (1.3521, 103.8198),
            "toronto": (43.6532, -79.3832),
            "berlin": (52.5200, 13.4050),
            "mumbai": (19.0760, 72.8777)
        }
        
        city_lower = city.lower().replace(" ", "_")
        
        if city_lower in cities:
            lat, lon = cities[city_lower]
            
            # Add small random offset to avoid exact coordinates
            lat += random.uniform(-0.01, 0.01)
            lon += random.uniform(-0.01, 0.01)
            
            await self.set_spoofed_location(lat, lon)
            
            return {
                "city": city,
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "mode": LocationMode.SPOOFED,
                "message": f"Location spoofed to {city}"
            }
        else:
            available_cities = ", ".join([c.replace("_", " ").title() for c in cities.keys()])
            return {
                "error": f"City not found. Available cities: {available_cities}"
            }
    
    async def get_available_cities(self) -> List[Dict]:
        """Get list of available city locations for spoofing"""
        cities = [
            {"id": "new_york", "name": "New York", "country": "USA"},
            {"id": "london", "name": "London", "country": "UK"},
            {"id": "tokyo", "name": "Tokyo", "country": "Japan"},
            {"id": "paris", "name": "Paris", "country": "France"},
            {"id": "sydney", "name": "Sydney", "country": "Australia"},
            {"id": "dubai", "name": "Dubai", "country": "UAE"},
            {"id": "singapore", "name": "Singapore", "country": "Singapore"},
            {"id": "toronto", "name": "Toronto", "country": "Canada"},
            {"id": "berlin", "name": "Berlin", "country": "Germany"},
            {"id": "mumbai", "name": "Mumbai", "country": "India"}
        ]
        return cities
    
    async def get_status(self) -> Dict:
        """Get current location spoofing status"""
        return {
            "mode": self.mode,
            "mode_description": self._get_mode_description(self.mode),
            "approximation_radius_km": self.approximation_radius_km if self.mode == LocationMode.APPROXIMATE else None,
            "spoofed_location_set": self.spoofed_location is not None,
            "timestamp": datetime.now().isoformat()
        }
    
    async def calculate_distance(self, lat1: float, lon1: float, 
                                lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates (Haversine formula)"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distance_km = R * c
        return round(distance_km, 2)
    
    async def verify_location_privacy(self) -> Dict:
        """Verify that location is properly spoofed"""
        current_location = await self.get_location()
        
        is_private = current_location["mode"] != LocationMode.REAL
        
        privacy_level = "high" if current_location["mode"] in [LocationMode.SPOOFED, LocationMode.RANDOM] else \
                       "medium" if current_location["mode"] == LocationMode.APPROXIMATE else "low"
        
        return {
            "is_location_private": is_private,
            "privacy_level": privacy_level,
            "current_mode": current_location["mode"],
            "timestamp": datetime.now().isoformat()
        }


# Global location spoofing instance
location_spoofing = LocationSpoofing()
