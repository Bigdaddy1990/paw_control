"""Utility functions for Paw Control."""
import logging
import re
from datetime import datetime, timezone
from math import radians, sin, cos, sqrt, atan2
from typing import Any, Optional, Union, Tuple

from .exceptions import InvalidCoordinates

_LOGGER = logging.getLogger(__name__)


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int."""
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """Safely convert value to string."""
    try:
        return str(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def format_timestamp(timestamp: Union[datetime, str], format_str: str = "%Y-%m-%d %H:%M") -> str:
    """Format timestamp for display."""
    try:
        if isinstance(timestamp, str):
            if 'T' in timestamp:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(timestamp)
        elif isinstance(timestamp, datetime):
            dt = timestamp
        else:
            return "Unbekannt"
        
        if dt.tzinfo == timezone.utc:
            dt = dt.replace(tzinfo=None)
        
        return dt.strftime(format_str)
    except (ValueError, AttributeError):
        return "Unbekannt"


def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """Calculate distance between two GPS points in meters using Haversine formula."""
    lat1, lon1 = point1
    lat2, lon2 = point2
    
    if not validate_coordinates(lat1, lon1) or not validate_coordinates(lat2, lon2):
        raise InvalidCoordinates("Invalid GPS coordinates provided")
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    R = 6371000  # Earth's radius in meters
    distance = R * c
    
    return distance


def calculate_calories(
    dog_weight: float,
    distance_km: float,
    duration_minutes: float,
    activity_type: str = "walking"
) -> float:
    """Calculate calories burned during activity."""
    if dog_weight <= 0 or distance_km < 0 or duration_minutes <= 0:
        return 0.0
    
    base_rate = 2.0  # Base metabolic rate for dogs (kcal/hour per kg)
    
    multipliers = {
        "walking": 3.0,
        "running": 5.0,
        "playing": 4.0,
        "swimming": 6.0,
    }
    
    multiplier = multipliers.get(activity_type.lower(), 3.0)
    duration_hours = duration_minutes / 60.0
    
    calories = dog_weight * base_rate * multiplier * duration_hours
    distance_factor = distance_km * 0.5
    calories += dog_weight * distance_factor
    
    return round(calories, 1)


def is_within_geofence(
    lat: float, 
    lon: float, 
    center_lat: float, 
    center_lon: float, 
    radius: float
) -> bool:
    """Check if coordinates are within geofence."""
    try:
        distance = calculate_distance((lat, lon), (center_lat, center_lon))
        return distance <= radius
    except InvalidCoordinates:
        return False


def normalize_dog_name(name: str) -> str:
    """Normalize dog name for entity IDs."""
    if not name:
        return ""
    
    normalized = re.sub(r'[^\w\s-]', '', name.lower())
    normalized = re.sub(r'[-\s]+', '_', normalized)
    normalized = normalized.strip('_')
    
    return normalized


def validate_coordinates(lat: float, lon: float) -> bool:
    """Validate GPS coordinates."""
    try:
        lat = float(lat)
        lon = float(lon)
        return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0
    except (ValueError, TypeError):
        return False


def validate_dog_name(name: str) -> bool:
    """Validate dog name."""
    if not isinstance(name, str):
        return False
    
    name = name.strip()
    if len(name) < 2 or len(name) > 50:
        return False
    
    if not re.match(r'^[a-zA-Z0-9\s\-]+$', name):
        return False
    
    return True


def get_entity_id(domain: str, dog_name: str, key: str) -> str:
    """Generate entity ID."""
    normalized_name = normalize_dog_name(dog_name)
    return f"{domain}.{normalized_name}_{key}"


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable string."""
    if seconds < 60:
        return f"{seconds} Sek"
    
    minutes = seconds // 60
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if hours > 0:
        return f"{hours} Std {remaining_minutes} Min"
    else:
        return f"{minutes} Min"


def calculate_walk_distance(gps_points: list) -> float:
    """Calculate total walk distance from GPS points."""
    if len(gps_points) < 2:
        return 0.0
    
    total_distance = 0.0
    
    for i in range(1, len(gps_points)):
        try:
            distance = calculate_distance(gps_points[i-1], gps_points[i])
            total_distance += distance
        except InvalidCoordinates:
            continue
    
    return round(total_distance / 1000, 2)  # Convert to kilometers


def validate_weight(weight: float) -> bool:
    """Validate dog weight."""
    try:
        weight = float(weight)
        return 0.5 <= weight <= 100.0
    except (ValueError, TypeError):
        return False


def validate_age(age: int) -> bool:
    """Validate dog age."""
    try:
        age = int(age)
        return 0 <= age <= 30
    except (ValueError, TypeError):
        return False


def parse_feeding_times(feeding_times_str: str) -> list:
    """Parse feeding times string into list of time objects."""
    times = []
    
    if not feeding_times_str:
        return times
    
    for time_str in feeding_times_str.split(','):
        time_str = time_str.strip()
        try:
            if ':' in time_str:
                hour, minute = time_str.split(':')
                hour = int(hour)
                minute = int(minute)
                
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    times.append(f"{hour:02d}:{minute:02d}")
        except (ValueError, IndexError):
            continue
    
    return sorted(times)