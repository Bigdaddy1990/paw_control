"""Utility functions for Paw Control integration."""
from __future__ import annotations

import re
import logging
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2
from typing import List, Dict, Tuple, Optional, Any

from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_NAME
from homeassistant.util import slugify

from .const import (
    MIN_DOG_NAME_LENGTH,
    MAX_DOG_NAME_LENGTH,
    MIN_DOG_WEIGHT,
    MAX_DOG_WEIGHT,
    MIN_DOG_AGE,
    MAX_DOG_AGE,
    DOG_NAME_PATTERN,
    GPS_ACCURACY_THRESHOLDS,
    VALIDATION_RULES,
)
from .exceptions import InvalidCoordinates, DataValidationError

_LOGGER = logging.getLogger(__name__)


def validate_dog_name(name: str) -> bool:
    """Validate dog name format and constraints."""
    if not name or not isinstance(name, str):
        return False
    
    name = name.strip()
    
    # Check length
    if len(name) < MIN_DOG_NAME_LENGTH or len(name) > MAX_DOG_NAME_LENGTH:
        return False
    
    # Check for valid characters (letters, numbers, spaces, common punctuation)
    if not re.match(r'^[a-zA-ZäöüÄÖÜß0-9\s\-_.]+$', name):
        return False
    
    # Must start with a letter
    if not name[0].isalpha():
        return False
    
    return True


def validate_weight(weight: float) -> bool:
    """Validate dog weight."""
    try:
        weight = float(weight)
        return MIN_DOG_WEIGHT <= weight <= MAX_DOG_WEIGHT
    except (ValueError, TypeError):
        return False


def validate_age(age: int) -> bool:
    """Validate dog age."""
    try:
        age = int(age)
        return MIN_DOG_AGE <= age <= MAX_DOG_AGE
    except (ValueError, TypeError):
        return False


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validate GPS coordinates."""
    try:
        lat = float(latitude)
        lon = float(longitude)
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except (ValueError, TypeError):
        return False


def validate_gps_accuracy(accuracy: float) -> bool:
    """Validate GPS accuracy value."""
    try:
        acc = float(accuracy)
        return 0 <= acc <= 1000  # Max 1000 meters
    except (ValueError, TypeError):
        return False


def calculate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """Calculate distance between two GPS coordinates in meters using Haversine formula."""
    if not validate_coordinates(coord1[0], coord1[1]) or not validate_coordinates(coord2[0], coord2[1]):
        raise InvalidCoordinates("Invalid GPS coordinates provided")
    
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    # Earth's radius in meters
    r = 6371000
    
    return r * c


def format_duration(minutes: int) -> str:
    """Format duration in minutes to human readable string."""
    if minutes < 60:
        return f"{minutes} min"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if remaining_minutes == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {remaining_minutes}min"


def format_distance(meters: float) -> str:
    """Format distance in meters to human readable string."""
    if meters < 1000:
        return f"{int(meters)}m"
    else:
        km = meters / 1000
        return f"{km:.1f}km"


def format_weight(kg: float) -> str:
    """Format weight to human readable string."""
    return f"{kg:.1f}kg"


def get_gps_accuracy_level(accuracy: float) -> str:
    """Get GPS accuracy level description."""
    if accuracy <= GPS_ACCURACY_THRESHOLDS["excellent"]:
        return "Ausgezeichnet"
    elif accuracy <= GPS_ACCURACY_THRESHOLDS["good"]:
        return "Gut"
    elif accuracy <= GPS_ACCURACY_THRESHOLDS["acceptable"]:
        return "Akzeptabel"
    else:
        return "Schlecht"


def calculate_dog_calories_per_day(weight_kg: float, activity_level: str = "normal") -> int:
    """Calculate daily calorie needs for a dog based on weight and activity level."""
    # Base formula: RER = 70 * (weight in kg)^0.75
    rer = 70 * (weight_kg ** 0.75)
    
    # Activity multipliers
    multipliers = {
        "very_low": 1.2,
        "low": 1.4,
        "normal": 1.6,
        "high": 1.8,
        "very_high": 2.0
    }
    
    multiplier = multipliers.get(activity_level, 1.6)
    return int(rer * multiplier)


def calculate_ideal_walk_duration(weight_kg: float, age_years: float, activity_level: str = "normal") -> int:
    """Calculate ideal daily walk duration in minutes."""
    # Base time per kg (adult dog)
    base_minutes_per_kg = 2
    
    # Age adjustments
    if age_years < 1:  # Puppy
        age_multiplier = 0.5
    elif age_years > 8:  # Senior
        age_multiplier = 0.7
    else:  # Adult
        age_multiplier = 1.0
    
    # Activity level adjustments
    activity_multipliers = {
        "very_low": 0.5,
        "low": 0.7,
        "normal": 1.0,
        "high": 1.3,
        "very_high": 1.5
    }
    
    activity_multiplier = activity_multipliers.get(activity_level, 1.0)
    
    # Calculate
    base_time = weight_kg * base_minutes_per_kg
    adjusted_time = base_time * age_multiplier * activity_multiplier
    
    # Reasonable bounds
    return max(15, min(180, int(adjusted_time)))


def validate_service_data(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """Validate service call data."""
    if not isinstance(data, dict):
        return False
    
    for field in required_fields:
        if field not in data:
            return False
    
    return True


def safe_float_convert(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int_convert(value: Any, default: int = 0) -> int:
    """Safely convert value to int."""
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def generate_entity_id(dog_name: str, entity_type: str, suffix: str) -> str:
    """Generate consistent entity ID."""
    dog_slug = slugify(dog_name)
    return f"{entity_type}.{dog_slug}_{suffix}"


def parse_coordinates_string(coord_string: str) -> Tuple[float, float]:
    """Parse coordinates from string format 'latitude,longitude'."""
    try:
        parts = coord_string.split(',')
        if len(parts) != 2:
            raise ValueError("Invalid coordinate format")
        
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
        
        if not validate_coordinates(lat, lon):
            raise ValueError("Invalid coordinate values")
        
        return lat, lon
        
    except (ValueError, IndexError) as e:
        raise InvalidCoordinates(f"Could not parse coordinates '{coord_string}': {e}")


def format_coordinates(latitude: float, longitude: float, precision: int = 6) -> str:
    """Format coordinates to string."""
    return f"{latitude:.{precision}f},{longitude:.{precision}f}"


def calculate_speed_kmh(distance_m: float, time_seconds: float) -> float:
    """Calculate speed in km/h from distance in meters and time in seconds."""
    if time_seconds <= 0:
        return 0.0
    
    # Convert to km/h
    speed_ms = distance_m / time_seconds
    speed_kmh = speed_ms * 3.6
    
    return round(speed_kmh, 1)


def estimate_calories_burned(distance_km: float, weight_kg: float, activity_intensity: str = "medium") -> int:
    """Estimate calories burned during activity."""
    # Base calories per km per kg
    base_cal_per_km_per_kg = 0.8
    
    # Intensity multipliers
    intensity_multipliers = {
        "low": 0.7,
        "medium": 1.0,
        "high": 1.4,
        "extreme": 1.8
    }
    
    multiplier = intensity_multipliers.get(activity_intensity, 1.0)
    calories = distance_km * weight_kg * base_cal_per_km_per_kg * multiplier
    
    return max(1, int(calories))


def time_since_last_activity(last_activity_time: str) -> timedelta:
    """Calculate time since last activity."""
    try:
        if not last_activity_time or last_activity_time in ["unknown", "unavailable"]:
            return timedelta(days=999)  # Very long time if unknown
        
        last_time = datetime.fromisoformat(last_activity_time.replace("Z", "+00:00"))
        return datetime.now() - last_time
        
    except (ValueError, TypeError):
        return timedelta(days=999)


def is_time_for_activity(last_activity_time: str, interval_hours: float) -> bool:
    """Check if enough time has passed for next activity."""
    time_since = time_since_last_activity(last_activity_time)
    return time_since >= timedelta(hours=interval_hours)


def get_activity_status_emoji(activity_type: str, completed: bool) -> str:
    """Get emoji for activity status."""
    activity_emojis = {
        "feeding": "🍽️",
        "walk": "🚶",
        "play": "🎾",
        "training": "🎓",
        "health": "🏥",
        "grooming": "✂️",
        "medication": "💊",
        "vet": "🩺"
    }
    
    emoji = activity_emojis.get(activity_type, "📝")
    status = "✅" if completed else "⏳"
    
    return f"{emoji} {status}"


def validate_data_against_rules(data: Dict[str, Any]) -> List[str]:
    """Validate data against defined validation rules."""
    errors = []
    
    for field, value in data.items():
        if field in VALIDATION_RULES:
            rule = VALIDATION_RULES[field]
            
            try:
                num_value = float(value)
                
                if num_value < rule["min"]:
                    errors.append(f"{field} must be at least {rule['min']} {rule['unit']}")
                elif num_value > rule["max"]:
                    errors.append(f"{field} must be at most {rule['max']} {rule['unit']}")
                    
            except (ValueError, TypeError):
                errors.append(f"{field} must be a valid number")
    
    return errors


def create_backup_filename(dog_name: str, backup_type: str = "full") -> str:
    """Create backup filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dog_slug = slugify(dog_name)
    return f"paw_control_{dog_slug}_{backup_type}_{timestamp}.json"


def normalize_dog_name(name: str) -> str:
    """Normalize dog name for consistent use."""
    if not name:
        return ""
    
    # Remove extra whitespace and convert to title case
    normalized = " ".join(name.strip().split())
    return normalized.title()


def get_meal_time_category(hour: int) -> str:
    """Get meal category based on hour of day."""
    if 5 <= hour < 10:
        return "morning"
    elif 11 <= hour < 15:
        return "lunch"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "snack"


def calculate_dog_age_in_human_years(dog_age_years: float, size_category: str = "medium") -> int:
    """Calculate dog age in human equivalent years."""
    # Different aging rates by size
    if dog_age_years <= 2:
        # First 2 years are rapid aging
        human_years = dog_age_years * 10.5
    else:
        # After 2 years, aging rate depends on size
        size_multipliers = {
            "toy": 4,
            "small": 4.5,
            "medium": 5,
            "large": 5.5,
            "giant": 6
        }
        
        multiplier = size_multipliers.get(size_category, 5)
        human_years = 21 + (dog_age_years - 2) * multiplier
    
    return int(human_years)


def is_healthy_weight_for_breed(weight_kg: float, breed_size: str) -> bool:
    """Check if weight is healthy for breed size."""
    weight_ranges = {
        "toy": (1, 6),
        "small": (6, 12),
        "medium": (12, 27),
        "large": (27, 45),
        "giant": (45, 90)
    }
    
    if breed_size not in weight_ranges:
        return True  # Unknown breed, assume healthy
    
    min_weight, max_weight = weight_ranges[breed_size]
    return min_weight <= weight_kg <= max_weight


async def safe_service_call(hass: HomeAssistant, domain: str, service: str, data: dict) -> bool:
    """Make a safe service call with error handling."""
    try:
        entity_id = data.get("entity_id")
        
        # Check if service exists
        if not hass.services.has_service(domain, service):
            _LOGGER.debug("Service %s.%s not available", domain, service)
            return False
        
        # Check if entity exists (if specified)
        if entity_id and not hass.states.get(entity_id):
            _LOGGER.debug("Entity %s not found, skipping service call", entity_id)
            return False
        
        await hass.services.async_call(domain, service, data, blocking=True)
        return True
        
    except Exception as e:
        _LOGGER.debug("Service call %s.%s failed: %s", domain, service, e)
        return False


def extract_dog_name_from_entity_id(entity_id: str) -> str:
    """Extract dog name from entity_id."""
    try:
        # Remove domain prefix
        entity_name = entity_id.split(".", 1)[1] if "." in entity_id else entity_id
        
        # Extract dog name (first part before underscore)
        parts = entity_name.split("_")
        return parts[0] if parts else entity_name
        
    except (IndexError, AttributeError):
        return ""


def create_notification_id(dog_name: str, notification_type: str) -> str:
    """Create unique notification ID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dog_slug = slugify(dog_name)
    return f"paw_control_{dog_slug}_{notification_type}_{timestamp}"


def format_time_ago(dt: datetime) -> str:
    """Format datetime as 'time ago' string."""
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"vor {diff.days} Tag{'en' if diff.days > 1 else ''}"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"vor {hours} Stunde{'n' if hours > 1 else ''}"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"vor {minutes} Minute{'n' if minutes > 1 else ''}"
    else:
        return "gerade eben"


def get_health_status_color(status: str) -> str:
    """Get color for health status."""
    status_colors = {
        "ausgezeichnet": "green",
        "sehr gut": "lightgreen",
        "gut": "green",
        "normal": "blue",
        "unwohl": "orange",
        "krank": "red",
        "notfall": "darkred"
    }
    
    return status_colors.get(status.lower(), "gray")


def calculate_feeding_amount_by_weight(weight_kg: float, meals_per_day: int = 2) -> int:
    """Calculate daily feeding amount in grams based on weight."""
    # Rough guideline: 2-3% of body weight per day
    daily_amount = weight_kg * 25  # 2.5% in grams
    
    # Adjust for number of meals
    return int(daily_amount / meals_per_day)


def is_emergency_situation(health_data: Dict[str, Any]) -> bool:
    """Determine if health data indicates emergency situation."""
    emergency_indicators = [
        health_data.get("temperature", 0) > 41.0,  # High fever
        health_data.get("temperature", 0) < 37.0,  # Hypothermia
        health_data.get("heart_rate", 0) > 180,    # Tachycardia
        health_data.get("heart_rate", 0) < 50,     # Bradycardia
        "notfall" in str(health_data.get("health_status", "")).lower(),
        "emergency" in str(health_data.get("emergency_mode", "")).lower()
    ]
    
    return any(emergency_indicators)
