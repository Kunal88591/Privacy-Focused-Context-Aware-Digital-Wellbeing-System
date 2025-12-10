"""
Location Service - Location Privacy and Spoofing
Provides location privacy, spoofing, and tracking management
"""

import random
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum


class LocationAccuracy(str, Enum):
    """Location accuracy levels"""
    EXACT = "exact"          # Real coordinates
    STREET = "street"        # Approximate to street
    CITY = "city"            # Approximate to city
    REGION = "region"        # Approximate to region
    COUNTRY = "country"      # Approximate to country
    DISABLED = "disabled"    # Location completely hidden


class LocationService:
    """Location privacy and spoofing service"""
    
    def __init__(self):
        # Current real location (would be from device GPS)
        self.real_location = None
        
        # Spoofing settings
        self.spoofing_enabled = False
        self.spoofed_location = None
        self.accuracy_level = LocationAccuracy.EXACT
        
        # Location history
        self.location_history = []
        
        # Apps with location access
        self.apps_with_access = {}
        
        # Major cities for spoofing (lat, lon)
        self.major_cities = {
            "New York, US": (40.7128, -74.0060),
            "Los Angeles, US": (34.0522, -118.2437),
            "London, UK": (51.5074, -0.1278),
            "Paris, France": (48.8566, 2.3522),
            "Tokyo, Japan": (35.6762, 139.6503),
            "Sydney, Australia": (-33.8688, 151.2093),
            "Berlin, Germany": (52.5200, 13.4050),
            "Toronto, Canada": (43.6532, -79.3832),
            "Dubai, UAE": (25.2048, 55.2708),
            "Singapore": (1.3521, 103.8198)
        }
    
    def set_real_location(self, latitude: float, longitude: float, accuracy: Optional[float] = None) -> Dict:
        """
        Set/update real device location
        
        Args:
            latitude: GPS latitude
            longitude: GPS longitude  
            accuracy: Accuracy in meters
            
        Returns:
            Location update result
        """
        self.real_location = {
            "latitude": latitude,
            "longitude": longitude,
            "accuracy_meters": accuracy or 10,
            "timestamp": datetime.now().isoformat(),
            "source": "gps"
        }
        
        # Add to history
        self.location_history.append({
            **self.real_location,
            "type": "real"
        })
        
        return {
            "success": True,
            "location": self.real_location
        }
    
    def get_current_location(self) -> Dict:
        """
        Get current location (spoofed if enabled, real otherwise)
        
        Returns:
            Current location coordinates
        """
        if self.spoofing_enabled and self.spoofed_location:
            location = self.spoofed_location
        elif self.real_location:
            location = self._apply_accuracy_filter(self.real_location)
        else:
            # No location available
            return {
                "available": False,
                "message": "Location not available"
            }
        
        return {
            "available": True,
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "accuracy_meters": location.get("accuracy_meters", 0),
            "is_spoofed": self.spoofing_enabled,
            "accuracy_level": self.accuracy_level,
            "timestamp": location.get("timestamp", datetime.now().isoformat())
        }
    
    def _apply_accuracy_filter(self, location: Dict) -> Dict:
        """Apply accuracy filter to reduce precision"""
        lat = location["latitude"]
        lon = location["longitude"]
        
        if self.accuracy_level == LocationAccuracy.EXACT:
            return location
        elif self.accuracy_level == LocationAccuracy.STREET:
            # Round to ~100m precision (3 decimal places)
            return {
                **location,
                "latitude": round(lat, 3),
                "longitude": round(lon, 3),
                "accuracy_meters": 100
            }
        elif self.accuracy_level == LocationAccuracy.CITY:
            # Round to ~10km precision (1 decimal place)
            return {
                **location,
                "latitude": round(lat, 1),
                "longitude": round(lon, 1),
                "accuracy_meters": 10000
            }
        elif self.accuracy_level == LocationAccuracy.REGION:
            # Round to ~100km precision (0 decimal places)
            return {
                **location,
                "latitude": round(lat, 0),
                "longitude": round(lon, 0),
                "accuracy_meters": 100000
            }
        elif self.accuracy_level == LocationAccuracy.COUNTRY:
            # Very rough approximation
            return {
                **location,
                "latitude": round(lat / 5) * 5,
                "longitude": round(lon / 5) * 5,
                "accuracy_meters": 500000
            }
        else:  # DISABLED
            return {
                "latitude": 0,
                "longitude": 0,
                "accuracy_meters": 0
            }
    
    def enable_spoofing(self, city: Optional[str] = None, latitude: Optional[float] = None, 
                       longitude: Optional[float] = None) -> Dict:
        """
        Enable location spoofing
        
        Args:
            city: Name of city to spoof (from major_cities)
            latitude: Custom latitude (if not using city)
            longitude: Custom longitude (if not using city)
            
        Returns:
            Spoofing configuration result
        """
        if city and city in self.major_cities:
            lat, lon = self.major_cities[city]
            location_name = city
        elif latitude is not None and longitude is not None:
            lat, lon = latitude, longitude
            location_name = f"{lat:.4f}, {lon:.4f}"
        else:
            # Random location
            city_name, (lat, lon) = random.choice(list(self.major_cities.items()))
            location_name = city_name
        
        # Add small random offset for realism
        lat += random.uniform(-0.01, 0.01)
        lon += random.uniform(-0.01, 0.01)
        
        self.spoofing_enabled = True
        self.spoofed_location = {
            "latitude": lat,
            "longitude": lon,
            "accuracy_meters": 10,
            "timestamp": datetime.now().isoformat(),
            "source": "spoofed",
            "location_name": location_name
        }
        
        return {
            "success": True,
            "spoofing_enabled": True,
            "spoofed_location": self.spoofed_location,
            "message": f"Location spoofed to {location_name}"
        }
    
    def disable_spoofing(self) -> Dict:
        """Disable location spoofing"""
        self.spoofing_enabled = False
        
        return {
            "success": True,
            "spoofing_enabled": False,
            "message": "Location spoofing disabled - using real location"
        }
    
    def set_accuracy_level(self, level: LocationAccuracy) -> Dict:
        """
        Set location accuracy level for privacy
        
        Args:
            level: Accuracy level to use
            
        Returns:
            Configuration result
        """
        self.accuracy_level = level
        
        privacy_descriptions = {
            LocationAccuracy.EXACT: "Full precision - apps see exact location",
            LocationAccuracy.STREET: "Street level - apps see approximate street (~100m)",
            LocationAccuracy.CITY: "City level - apps see general area (~10km)",
            LocationAccuracy.REGION: "Region level - apps see region only (~100km)",
            LocationAccuracy.COUNTRY: "Country level - apps see country only",
            LocationAccuracy.DISABLED: "Disabled - apps cannot access location"
        }
        
        return {
            "success": True,
            "accuracy_level": level,
            "description": privacy_descriptions[level],
            "privacy_score": self._get_privacy_score_for_accuracy(level)
        }
    
    def _get_privacy_score_for_accuracy(self, level: LocationAccuracy) -> int:
        """Calculate privacy score based on accuracy level"""
        scores = {
            LocationAccuracy.EXACT: 0,
            LocationAccuracy.STREET: 20,
            LocationAccuracy.CITY: 50,
            LocationAccuracy.REGION: 70,
            LocationAccuracy.COUNTRY: 90,
            LocationAccuracy.DISABLED: 100
        }
        return scores.get(level, 0)
    
    def manage_app_access(self, app_name: str, permission: str) -> Dict:
        """
        Manage location access for specific apps
        
        Args:
            app_name: Name of the application
            permission: 'always', 'while_using', 'never', 'ask_each_time'
            
        Returns:
            Permission update result
        """
        self.apps_with_access[app_name] = {
            "permission": permission,
            "updated_at": datetime.now().isoformat(),
            "access_count": self.apps_with_access.get(app_name, {}).get("access_count", 0)
        }
        
        return {
            "success": True,
            "app_name": app_name,
            "permission": permission,
            "message": f"Location permission for {app_name} set to '{permission}'"
        }
    
    def get_app_permissions(self) -> List[Dict]:
        """Get list of apps with location permissions"""
        return [
            {
                "app_name": app,
                **details
            }
            for app, details in self.apps_with_access.items()
        ]
    
    def track_app_location_access(self, app_name: str) -> Dict:
        """
        Track when an app accesses location
        
        Args:
            app_name: Name of the app accessing location
            
        Returns:
            Access tracking result
        """
        if app_name in self.apps_with_access:
            self.apps_with_access[app_name]["access_count"] += 1
            self.apps_with_access[app_name]["last_access"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "app_name": app_name,
                "access_count": self.apps_with_access[app_name]["access_count"],
                "permission": self.apps_with_access[app_name]["permission"]
            }
        else:
            return {
                "success": False,
                "error": "App not found in permissions",
                "app_name": app_name
            }
    
    def get_location_history(self, hours: int = 24) -> List[Dict]:
        """
        Get location history for specified period
        
        Args:
            hours: Number of hours of history
            
        Returns:
            Location history entries
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter history by time (simplified for demo)
        return self.location_history[-50:] if self.location_history else []
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates in kilometers
        Uses Haversine formula
        
        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate
            
        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return round(distance, 2)
    
    def get_privacy_assessment(self) -> Dict:
        """
        Get comprehensive location privacy assessment
        
        Returns:
            Privacy score and recommendations
        """
        score = 0
        issues = []
        recommendations = []
        
        # Spoofing enabled (30 points)
        if self.spoofing_enabled:
            score += 30
        else:
            issues.append("Real location exposed")
            recommendations.append("Enable location spoofing for maximum privacy")
        
        # Accuracy level (40 points max)
        score += self._get_privacy_score_for_accuracy(self.accuracy_level) * 0.4
        
        if self.accuracy_level == LocationAccuracy.EXACT:
            issues.append("Using exact location precision")
            recommendations.append("Reduce location accuracy to street or city level")
        
        # App permissions (30 points)
        if not self.apps_with_access:
            score += 30
        else:
            always_allowed = sum(1 for app in self.apps_with_access.values() 
                               if app.get("permission") == "always")
            if always_allowed > 0:
                issues.append(f"{always_allowed} apps have 'always' location access")
                recommendations.append("Change app permissions to 'while using' or 'never'")
            
            app_score = max(0, 30 - (always_allowed * 10))
            score += app_score
        
        # Frequent tracking detection
        total_accesses = sum(app.get("access_count", 0) for app in self.apps_with_access.values())
        if total_accesses > 100:
            issues.append("High frequency of location tracking")
            recommendations.append("Review and restrict location access for apps")
        
        return {
            "privacy_score": int(score),
            "max_score": 100,
            "grade": self._get_privacy_grade(score),
            "status": "protected" if score >= 70 else "exposed",
            "issues": issues,
            "recommendations": recommendations,
            "details": {
                "spoofing_enabled": self.spoofing_enabled,
                "accuracy_level": self.accuracy_level,
                "apps_with_access": len(self.apps_with_access),
                "total_location_accesses": total_accesses
            }
        }
    
    def _get_privacy_grade(self, score: int) -> str:
        """Convert privacy score to letter grade"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def get_available_spoof_locations(self) -> List[Dict]:
        """Get list of available cities for spoofing"""
        return [
            {
                "city": city,
                "latitude": coords[0],
                "longitude": coords[1],
                "country": city.split(", ")[1] if ", " in city else "Unknown"
            }
            for city, coords in self.major_cities.items()
        ]
    
    def get_location_insights(self) -> Dict:
        """Get insights about location tracking and privacy"""
        assessment = self.get_privacy_assessment()
        
        insights = []
        
        # Spoofing status
        if self.spoofing_enabled:
            insights.append({
                "type": "positive",
                "title": "Location Spoofing Active",
                "message": f"Your location is spoofed to {self.spoofed_location.get('location_name', 'unknown')}"
            })
        else:
            insights.append({
                "type": "warning",
                "title": "Real Location Exposed",
                "message": "Apps can see your real location"
            })
        
        # App access warnings
        always_apps = [
            app for app, details in self.apps_with_access.items()
            if details.get("permission") == "always"
        ]
        if always_apps:
            insights.append({
                "type": "warning",
                "title": "Apps Tracking Always",
                "message": f"{len(always_apps)} apps track your location even when not in use"
            })
        
        # High access frequency
        high_access_apps = [
            (app, details.get("access_count", 0))
            for app, details in self.apps_with_access.items()
            if details.get("access_count", 0) > 20
        ]
        if high_access_apps:
            top_app = max(high_access_apps, key=lambda x: x[1])
            insights.append({
                "type": "info",
                "title": "High Location Access",
                "message": f"{top_app[0]} accessed location {top_app[1]} times"
            })
        
        return {
            "insights": insights,
            "privacy_assessment": assessment,
            "total_apps": len(self.apps_with_access),
            "spoofing_enabled": self.spoofing_enabled,
            "accuracy_level": self.accuracy_level
        }


# Singleton instance
location_service = LocationService()
