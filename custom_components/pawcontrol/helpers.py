import json
import logging
import asyncio
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2
from typing import List, Dict, Tuple, Optional, Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.storage import Store
from homeassistant.exceptions import HomeAssistantError

from .const import (
    FEEDING_TYPES,
    MEAL_TYPES,
    ACTIVITY_TYPES,
    ICONS,
    DEFAULT_FEEDING_TIMES_DICT,
    ENTITIES,
    DOMAIN,
    CONF_DOG_NAME,
    VACCINATION_TYPES,
    VACCINATION_NAMES,
    VACCINATION_INTERVALS,
    CORE_VACCINES,
    OPTIONAL_VACCINES,
    HEALTH_STATUS_OPTIONS,
    MOOD_OPTIONS,
    GPS_PROVIDERS,
    VALIDATION_RULES,
    DEFAULT_SETTINGS,
    STATUS_MESSAGES,
    ACTIVITY_STATUS,
    DEFAULT_GPS_COORDINATES,
    NOTIFICATION_PRIORITIES,
    API_TIMEOUTS
)

_LOGGER = logging.getLogger(__name__)

# Ultra-enhanced configuration for maximum success
ENTITY_CREATION_TIMEOUT = 60.0
DOMAIN_CREATION_DELAY = 2.0
MAX_RETRIES_PER_ENTITY = 8
BATCH_SIZE = 4
VERIFICATION_DELAY = 3.0
SYSTEM_STABILITY_WAIT = 5.0
INTER_BATCH_DELAY = 4.0
MAX_DOMAIN_RETRIES = 3

# =========================
# RECOVERY INTEGRATION: EXCEPTIONS
# =========================

class PawControlError(HomeAssistantError):
    """Base exception for Paw Control."""

class GPSError(PawControlError):
    """GPS-related errors."""

class InvalidCoordinates(PawControlError):
    """Invalid GPS coordinates."""

class DataCollectionError(PawControlError):
    """Data collection errors."""

class HealthMonitoringError(PawControlError):
    """Health monitoring errors."""

# =========================
# RECOVERY INTEGRATION: UTILITY FUNCTIONS
# =========================

def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """Calculate distance between two GPS points using Haversine formula."""
    lat1, lon1 = point1
    lat2, lon2 = point2
    
    # Earth's radius in meters
    R = 6371000
    
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    
    a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validate GPS coordinates."""
    try:
        lat = float(latitude)
        lon = float(longitude)
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except (ValueError, TypeError):
        return False

def validate_health_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate health data against rules."""
    errors = {}
    
    for field, rules in VALIDATION_RULES.items():
        if field in data:
            value = data[field]
            try:
                numeric_value = float(value)
                if numeric_value < rules["min"] or numeric_value > rules["max"]:
                    if field not in errors:
                        errors[field] = []
                    errors[field].append(f"Value {numeric_value} outside range {rules['min']}-{rules['max']} {rules['unit']}")
            except (ValueError, TypeError):
                if field not in errors:
                    errors[field] = []
                errors[field].append(f"Invalid numeric value: {value}")
    
    return errors

def format_duration(minutes: int) -> str:
    """Format duration in minutes to human readable string."""
    if minutes < 60:
        return f"{minutes} min"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if remaining_minutes == 0:
        return f"{hours}h"
    return f"{hours}h {remaining_minutes}min"

def get_time_since_last(timestamp_str: str) -> Optional[timedelta]:
    """Get time since last timestamp."""
    if not timestamp_str or timestamp_str in ["unknown", "unavailable"]:
        return None
    
    try:
        last_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return datetime.now() - last_time.replace(tzinfo=None)
    except (ValueError, AttributeError):
        return None

def determine_current_status(feeding_data: Dict, activity_data: Dict, health_data: Dict) -> str:
    """Determine current overall status."""
    # Emergency check
    if health_data.get("emergency_mode", False):
        return STATUS_MESSAGES["emergency"]
    
    # Health check
    health_status = health_data.get("status", "good")
    if health_status in ["sick", "very_sick", "emergency"]:
        return STATUS_MESSAGES["concern"]
    
    # Activity completion check
    fed_today = feeding_data.get("fed_today", False)
    walked_today = activity_data.get("walked_today", False)
    
    if fed_today and walked_today:
        return STATUS_MESSAGES["excellent"]
    elif fed_today or walked_today:
        return STATUS_MESSAGES["good"]
    else:
        return STATUS_MESSAGES["needs_attention"]

def calculate_distance_legacy(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on Earth (legacy function)."""
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    # Earth's radius in kilometers
    r = 6371
    
    return r * c

def is_within_geofence(current_lat: float, current_lon: float, 
                      home_lat: float, home_lon: float, radius_km: float) -> bool:
    """Check if current position is within geofence."""
    distance = calculate_distance_legacy(current_lat, current_lon, home_lat, home_lon)
    return distance <= radius_km

class PawControlDataUpdateCoordinator(DataUpdateCoordinator):
    """Enhanced class to manage fetching data from the Paw Control integration.
    
    VOLLSTÄNDIG INTEGRIERT: Original + Recovery Features + Part Extensions
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the coordinator."""
        self.dog_name = entry.data[CONF_DOG_NAME]
        self.hass = hass
        self.entry = entry
        self._store = Store(hass, 1, f"{DOMAIN}_{self.dog_name}")
        self._data = {}
        
        # RECOVERY INTEGRATION: Additional attributes
        self._gps_provider = None
        self._health_monitoring_enabled = True
        self._notification_enabled = True
        
        # Data caches (Recovery)
        self._cached_data = {}
        self._last_gps_update = None
        self._last_health_check = None
        self._activity_history = []
        self._health_history = []
        self._gps_history = []
        
        # Statistics tracking (Recovery)
        self._statistics = {
            "total_data_updates": 0,
            "successful_updates": 0,
            "failed_updates": 0,
            "last_update_duration": 0,
            "average_update_time": 0,
            "last_successful_update": None
        }

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.dog_name}",
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self):
        """Update data via library - ERWEITERT MIT RECOVERY FEATURES."""
        start_time = datetime.now()
        
        try:
            _LOGGER.debug("Starting comprehensive data update for %s", self.dog_name)
            
            # ORIGINAL: Collect data from various helper entities
            feeding_data = await self._collect_feeding_data()
            walking_data = await self._collect_walking_data()
            health_data = await self._collect_health_data()
            gps_data = await self._collect_gps_data()
            activity_data = await self._collect_activity_data()
            
            # RECOVERY INTEGRATION: Additional data collection
            dog_profile_data = await self._collect_dog_profile_data()
            status_data = await self._collect_status_data()
            statistics_data = await self._collect_statistics_data()
            notification_data = await self._collect_notification_data()
            
            data = {
                "status": "active",
                "last_update": datetime.now(),
                "dog_name": self.dog_name,
                # Original data
                "feeding": feeding_data,
                "walking": walking_data,
                "health": health_data,
                "gps": gps_data,
                "activities": activity_data,
                # Recovery integration
                "dog_profile": dog_profile_data,
                "system_status": status_data,
                "statistics": statistics_data,
                "notifications": notification_data,
                "last_updated": datetime.now().isoformat(),
                "update_count": self._statistics["total_data_updates"] + 1
            }
            
            # RECOVERY INTEGRATION: Analyze and enrich data
            data = await self._analyze_and_enrich_data(data)
            
            # Store data for persistence (Recovery)
            await self._store_data_persistent(data)
            
            # Update statistics (Recovery)
            update_duration = (datetime.now() - start_time).total_seconds()
            await self._update_statistics(update_duration, True)
            
            self._cached_data = data
            _LOGGER.debug("Data update completed successfully for %s in %.2fs", self.dog_name, update_duration)
            
            return data
            
        except Exception as exception:
            await self._update_statistics(0, False)
            _LOGGER.error("Error updating data for %s: %s", self.dog_name, exception)
            raise exception

    # =========================
    # RECOVERY INTEGRATION: DOG PROFILE DATA
    # =========================
    
    async def _collect_dog_profile_data(self) -> Dict[str, Any]:
        """Collect basic dog profile information."""
        try:
            profile_data = {}
            
            # Basic information
            breed_state = self.hass.states.get(f"input_text.{self.dog_name}_breed")
            if breed_state:
                profile_data["breed"] = breed_state.state
            
            # Age information
            age_years_state = self.hass.states.get(f"input_number.{self.dog_name}_age_years")
            if age_years_state and age_years_state.state not in ["unknown", "unavailable"]:
                profile_data["age_years"] = float(age_years_state.state)
            
            age_months_state = self.hass.states.get(f"input_number.{self.dog_name}_age_months")
            if age_months_state and age_months_state.state not in ["unknown", "unavailable"]:
                profile_data["age_months"] = int(float(age_months_state.state))
            
            # Weight information
            weight_state = self.hass.states.get(f"input_number.{self.dog_name}_weight")
            if weight_state and weight_state.state not in ["unknown", "unavailable"]:
                profile_data["weight"] = float(weight_state.state)
            
            # Size category
            size_state = self.hass.states.get(f"input_select.{self.dog_name}_size_category")
            if size_state:
                profile_data["size_category"] = size_state.state
            
            # Microchip and insurance
            microchip_state = self.hass.states.get(f"input_text.{self.dog_name}_microchip_id")
            if microchip_state:
                profile_data["microchip_id"] = microchip_state.state
            
            insurance_state = self.hass.states.get(f"input_text.{self.dog_name}_insurance_number")
            if insurance_state:
                profile_data["insurance_number"] = insurance_state.state
            
            profile_data["name"] = self.dog_name.title()
            profile_data["last_updated"] = datetime.now().isoformat()
            
            return profile_data

        except Exception as e:
            _LOGGER.error("Error collecting dog profile data for %s: %s", self.dog_name, e)
            return {"name": self.dog_name.title(), "error": str(e)}

    # =========================
    # ORIGINAL + ERWEITERTE FEEDING DATA COLLECTION
    # =========================

    async def _collect_feeding_data(self) -> Dict[str, Any]:
        """Collect feeding-related data - ERWEITERT MIT RECOVERY FEATURES."""
        try:
            feeding_data = {
                "daily_amount": 0,
                "streak": 0,
                "last_feeding": None,
                "feedings_today": {},
                # RECOVERY ERWEITERUNGEN
                "meals_today": {},
                "feeding_schedule": {},
                "nutrition_summary": {},
                "feeding_history": [],
                "next_feeding": None,
                "daily_total": 0
            }
            
            # Get daily food amount
            daily_amount_entity = f"input_number.{self.dog_name}_daily_food_amount"
            state = self.hass.states.get(daily_amount_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                feeding_data["daily_amount"] = float(state.state)
                feeding_data["daily_total"] = float(state.state)
            
            # Get feeding streak
            streak_entity = f"input_number.{self.dog_name}_feeding_streak"
            state = self.hass.states.get(streak_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                feeding_data["streak"] = int(float(state.state))
            
            # Get today's feedings - ERWEITERT
            total_food_today = 0
            meals_completed = 0
            
            for meal_type in FEEDING_TYPES:
                meal_data = {}
                
                # Check if meal was completed
                bool_entity = f"input_boolean.{self.dog_name}_feeding_{meal_type}"
                datetime_entity = f"input_datetime.{self.dog_name}_last_feeding_{meal_type}"
                
                bool_state = self.hass.states.get(bool_entity)
                datetime_state = self.hass.states.get(datetime_entity)
                
                meal_completed = bool_state.state == "on" if bool_state else False
                meal_data["completed"] = meal_completed
                
                if meal_completed:
                    meals_completed += 1
                
                if datetime_state and datetime_state.state not in ["unknown", "unavailable"]:
                    meal_data["last_time"] = datetime_state.state
                    meal_data["time_since"] = get_time_since_last(datetime_state.state)
                
                # Get feeding count
                count_state = self.hass.states.get(f"counter.{self.dog_name}_feeding_{meal_type}_count")
                if count_state and count_state.state not in ["unknown", "unavailable"]:
                    meal_data["count_today"] = int(count_state.state)
                
                # Get scheduled time
                if meal_type != "snack":
                    schedule_state = self.hass.states.get(f"input_datetime.{self.dog_name}_feeding_{meal_type}_time")
                    if schedule_state and schedule_state.state not in ["unknown", "unavailable"]:
                        meal_data["scheduled_time"] = schedule_state.state
                
                feeding_data["feedings_today"][meal_type] = meal_data
                feeding_data["meals_today"][meal_type] = meal_data  # Recovery compatibility
            
            # RECOVERY ERWEITERUNG: Nutrition summary
            feeding_data["nutrition_summary"] = {
                "total_food_grams": feeding_data["daily_total"],
                "estimated_calories": feeding_data["daily_total"] * 3.0,  # Average 3 kcal/g
                "meals_completed": meals_completed,
                "meals_remaining": len(FEEDING_TYPES) - meals_completed,
                "completion_percentage": (meals_completed / len(FEEDING_TYPES)) * 100
            }
            
            # Determine next feeding
            feeding_data["next_feeding"] = await self._calculate_next_feeding()
            
            # Get food preferences
            food_brand_state = self.hass.states.get(f"input_text.{self.dog_name}_food_brand")
            if food_brand_state:
                feeding_data["food_brand"] = food_brand_state.state
            
            allergies_state = self.hass.states.get(f"input_text.{self.dog_name}_food_allergies")
            if allergies_state:
                feeding_data["food_allergies"] = allergies_state.state
            
            treats_state = self.hass.states.get(f"input_text.{self.dog_name}_favorite_treats")
            if treats_state:
                feeding_data["favorite_treats"] = treats_state.state
            
            return feeding_data
            
        except Exception as e:
            _LOGGER.error("Error collecting feeding data for %s: %s", self.dog_name, e)
            return {"daily_amount": 0, "streak": 0, "feedings_today": {}}

    async def _collect_walking_data(self) -> Dict[str, Any]:
        """Collect walking-related data - ORIGINAL BEIBEHALTEN."""
        try:
            walking_data = {
                "daily_duration": 0,
                "daily_distance": 0,
                "walks_today": 0,
                "current_walk": {
                    "in_progress": False,
                    "distance": 0,
                    "duration": 0
                },
                "streak": 0,
            }
            
            # Get daily walk duration
            duration_entity = f"input_number.{self.dog_name}_daily_walk_duration"
            state = self.hass.states.get(duration_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                walking_data["daily_duration"] = float(state.state)
            
            # Get daily walk distance
            distance_entity = f"input_number.{self.dog_name}_walk_distance_today"
            state = self.hass.states.get(distance_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                walking_data["daily_distance"] = float(state.state)
            
            # Get walks count today
            count_entity = f"input_number.{self.dog_name}_walks_count_today"
            state = self.hass.states.get(count_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                walking_data["walks_today"] = int(float(state.state))
            
            # Check if walk is in progress
            progress_entity = f"input_boolean.{self.dog_name}_walk_in_progress"
            state = self.hass.states.get(progress_entity)
            walking_data["current_walk"]["in_progress"] = state.state == "on" if state else False
            
            if walking_data["current_walk"]["in_progress"]:
                # Get current walk stats
                current_distance_entity = f"input_number.{self.dog_name}_current_walk_distance"
                current_duration_entity = f"input_number.{self.dog_name}_current_walk_duration"
                
                distance_state = self.hass.states.get(current_distance_entity)
                duration_state = self.hass.states.get(current_duration_entity)
                
                if distance_state and distance_state.state not in ["unknown", "unavailable"]:
                    walking_data["current_walk"]["distance"] = float(distance_state.state)
                    
                if duration_state and duration_state.state not in ["unknown", "unavailable"]:
                    walking_data["current_walk"]["duration"] = float(duration_state.state)
            
            # Get walk streak
            streak_entity = f"input_number.{self.dog_name}_walk_streak"
            state = self.hass.states.get(streak_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                walking_data["streak"] = int(float(state.state))
            
            return walking_data
            
        except Exception as e:
            _LOGGER.error("Error collecting walking data for %s: %s", self.dog_name, e)
            return {"daily_duration": 0, "daily_distance": 0, "walks_today": 0, "current_walk": {"in_progress": False}}

    # =========================
    # ORIGINAL HEALTH & GPS DATA COLLECTION (ERWEITERT)
    # =========================

    async def _collect_health_data(self) -> Dict[str, Any]:
        """Collect health-related data - ERWEITERT MIT RECOVERY FEATURES."""
        try:
            health_data = {
                "weight": 0,
                "temperature": 38.5,
                "health_score": 0,
                "last_vet_visit": None,
                "next_vet_appointment": None,
                "health_status": "unknown",
                "mood": "unknown",
                # RECOVERY ERWEITERUNGEN
                "current_status": {},
                "vital_signs": {},
                "medication": {},
                "veterinary": {},
                "vaccination": {},
                "symptoms": {},
                "health_score_detailed": {},
                "alerts": [],
                "emergency_mode": False
            }
            
            # Get weight
            weight_entity = f"input_number.{self.dog_name}_weight"
            state = self.hass.states.get(weight_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                health_data["weight"] = float(state.state)
                health_data["vital_signs"]["weight"] = float(state.state)
            
            # Get temperature
            temp_entity = f"input_number.{self.dog_name}_temperature"
            state = self.hass.states.get(temp_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                health_data["temperature"] = float(state.state)
                health_data["vital_signs"]["temperature"] = float(state.state)
            
            # Get health score
            score_entity = f"input_number.{self.dog_name}_health_score"
            state = self.hass.states.get(score_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                health_data["health_score"] = float(state.state)
                health_data["health_score_detailed"]["overall"] = int(float(state.state))
            
            # Get health status
            status_entity = f"input_select.{self.dog_name}_health_status"
            state = self.hass.states.get(status_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                health_data["health_status"] = state.state
                health_data["current_status"]["overall"] = state.state
            
            # Get mood
            mood_entity = f"input_select.{self.dog_name}_mood"
            state = self.hass.states.get(mood_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                health_data["mood"] = state.state
            
            # RECOVERY: Current health status details
            feeling_well_state = self.hass.states.get(f"input_boolean.{self.dog_name}_feeling_well")
            health_data["current_status"]["feeling_well"] = feeling_well_state.state == "on" if feeling_well_state else True
            
            appetite_state = self.hass.states.get(f"input_boolean.{self.dog_name}_appetite_normal")
            health_data["current_status"]["appetite_normal"] = appetite_state.state == "on" if appetite_state else True
            
            energy_state = self.hass.states.get(f"input_boolean.{self.dog_name}_energy_normal")
            health_data["current_status"]["energy_normal"] = energy_state.state == "on" if energy_state else True
            
            # RECOVERY: Additional vital signs
            heart_rate_state = self.hass.states.get(f"input_number.{self.dog_name}_heart_rate")
            if heart_rate_state and heart_rate_state.state not in ["unknown", "unavailable"]:
                health_data["vital_signs"]["heart_rate"] = int(float(heart_rate_state.state))
            
            # RECOVERY: Medication information
            medication_given_state = self.hass.states.get(f"input_boolean.{self.dog_name}_medication_given")
            health_data["medication"]["given_today"] = medication_given_state.state == "on" if medication_given_state else False
            
            # Get vet visit dates
            last_vet_entity = f"input_datetime.{self.dog_name}_last_vet_visit"
            next_vet_entity = f"input_datetime.{self.dog_name}_next_vet_appointment"
            
            last_state = self.hass.states.get(last_vet_entity)
            next_state = self.hass.states.get(next_vet_entity)
            
            if last_state and last_state.state not in ["unknown", "unavailable"]:
                health_data["last_vet_visit"] = last_state.state
                health_data["veterinary"]["last_visit"] = last_state.state
                
            if next_state and next_state.state not in ["unknown", "unavailable"]:
                health_data["next_vet_appointment"] = next_state.state
                health_data["veterinary"]["next_appointment"] = next_state.state
            
            # Emergency mode check
            emergency_state = self.hass.states.get(f"input_boolean.{self.dog_name}_emergency_mode")
            health_data["emergency_mode"] = emergency_state.state == "on" if emergency_state else False
            
            # Generate health alerts
            health_data["alerts"] = await self._generate_health_alerts(health_data)
            
            return health_data
            
        except Exception as e:
            _LOGGER.error("Error collecting health data for %s: %s", self.dog_name, e)
            raise HealthMonitoringError(f"Failed to collect health data: {e}")

    async def _collect_gps_data(self) -> Dict[str, Any]:
        """Collect GPS and location data - KORRIGIERT."""
        try:
            gps_data = {
                "current_location": {
                    "latitude": 0,
                    "longitude": 0,
                    "accuracy": 0
                },
                "home_location": {
                    "latitude": 0,
                    "longitude": 0
                },
                "tracking_enabled": False,
                "battery_level": 100,
                "signal_strength": 100,
            }
            
            # Get current location
            lat_entity = f"input_number.{self.dog_name}_current_latitude"
            lon_entity = f"input_number.{self.dog_name}_current_longitude"
            
            lat_state = self.hass.states.get(lat_entity)
            lon_state = self.hass.states.get(lon_entity)
            
            if lat_state and lat_state.state not in ["unknown", "unavailable"]:
                gps_data["current_location"]["latitude"] = float(lat_state.state)
                
            if lon_state and lon_state.state not in ["unknown", "unavailable"]:
                gps_data["current_location"]["longitude"] = float(lon_state.state)
            
            # Get home location
            home_lat_entity = f"input_number.{self.dog_name}_home_latitude"
            home_lon_entity = f"input_number.{self.dog_name}_home_longitude"
            
            home_lat_state = self.hass.states.get(home_lat_entity)
            home_lon_state = self.hass.states.get(home_lon_entity)
            
            if home_lat_state and home_lat_state.state not in ["unknown", "unavailable"]:
                gps_data["home_location"]["latitude"] = float(home_lat_state.state)
                
            if home_lon_state and home_lon_state.state not in ["unknown", "unavailable"]:
                gps_data["home_location"]["longitude"] = float(home_lon_state.state)
            
            # Check if GPS tracking is enabled
            tracking_entity = f"input_boolean.{self.dog_name}_gps_tracking_enabled"
            state = self.hass.states.get(tracking_entity)
            gps_data["tracking_enabled"] = state.state == "on" if state else False
            
            # Get GPS device stats
            battery_entity = f"input_number.{self.dog_name}_gps_battery_level"
            signal_entity = f"input_number.{self.dog_name}_gps_signal_strength"
            
            battery_state = self.hass.states.get(battery_entity)
            signal_state = self.hass.states.get(signal_entity)
            
            if battery_state and battery_state.state not in ["unknown", "unavailable"]:
                gps_data["battery_level"] = float(battery_state.state)
                
            if signal_state and signal_state.state not in ["unknown", "unavailable"]:
                gps_data["signal_strength"] = float(signal_state.state)
            
            return gps_data
            
        except Exception as e:
            _LOGGER.error("Error collecting GPS data for %s: %s", self.dog_name, e)
            return {"current_location": {"latitude": 0, "longitude": 0}, "tracking_enabled": False}

    async def _collect_activity_data(self) -> Dict[str, Any]:
        """Collect activity-related data - ORIGINAL."""
        try:
            activity_data = {
                "playtime_today": 0,
                "training_sessions": 0,
                "sleep_hours": 8,
                "mood": "😊",
                "energy_level": 7,
                "stress_level": 3,
                "socialization_score": 75,
            }
            
            # Get playtime duration
            playtime_entity = f"input_number.{self.dog_name}_daily_play_duration"
            state = self.hass.states.get(playtime_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                activity_data["playtime_today"] = float(state.state)
            
            # Get training sessions count
            training_entity = f"counter.{self.dog_name}_training_count"
            state = self.hass.states.get(training_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                activity_data["training_sessions"] = int(state.state)
            
            # Get sleep hours
            sleep_entity = f"input_number.{self.dog_name}_sleep_hours"
            state = self.hass.states.get(sleep_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                activity_data["sleep_hours"] = float(state.state)
            
            # Get energy level
            energy_entity = f"input_number.{self.dog_name}_energy_level"
            state = self.hass.states.get(energy_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                activity_data["energy_level"] = float(state.state)
            
            # Get stress level
            stress_entity = f"input_number.{self.dog_name}_stress_level"
            state = self.hass.states.get(stress_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                activity_data["stress_level"] = float(state.state)
            
            # Get socialization score
            social_entity = f"input_number.{self.dog_name}_socialization_score"
            state = self.hass.states.get(social_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                activity_data["socialization_score"] = float(state.state)
            
            return activity_data
            
        except Exception as e:
            _LOGGER.error("Error collecting activity data for %s: %s", self.dog_name, e)
            return {"playtime_today": 0, "training_sessions": 0, "sleep_hours": 8}

    # =========================
    # RECOVERY INTEGRATION: STATUS & STATISTICS
    # =========================
    
    async def _collect_status_data(self) -> Dict[str, Any]:
        """Collect overall status and system information."""
        try:
            status_data = {
                "system_status": {},
                "modes": {},
                "alerts": [],
                "overall_status": "unknown",
                "completion_metrics": {},
                "attention_needed": False
            }
            
            # System modes
            visitor_mode_state = self.hass.states.get(f"input_boolean.{self.dog_name}_visitor_mode_input")
            status_data["modes"]["visitor_mode"] = visitor_mode_state.state == "on" if visitor_mode_state else False
            
            emergency_mode_state = self.hass.states.get(f"input_boolean.{self.dog_name}_emergency_mode")
            status_data["modes"]["emergency_mode"] = emergency_mode_state.state == "on" if emergency_mode_state else False
            
            auto_reminders_state = self.hass.states.get(f"input_boolean.{self.dog_name}_auto_reminders")
            status_data["modes"]["auto_reminders"] = auto_reminders_state.state == "on" if auto_reminders_state else False
            
            weather_alerts_state = self.hass.states.get(f"input_boolean.{self.dog_name}_weather_alerts")
            status_data["modes"]["weather_alerts"] = weather_alerts_state.state == "on" if weather_alerts_state else False
            
            # Check if attention is needed
            needs_attention_state = self.hass.states.get(f"input_boolean.{self.dog_name}_needs_attention")
            status_data["attention_needed"] = needs_attention_state.state == "on" if needs_attention_state else False
            
            # Daily completion metrics
            completion_metrics = {}
            
            # Feeding completion
            feeding_completed = 0
            for meal_type in FEEDING_TYPES:
                meal_state = self.hass.states.get(f"input_boolean.{self.dog_name}_feeding_{meal_type}")
                if meal_state and meal_state.state == "on":
                    feeding_completed += 1
            
            completion_metrics["feeding"] = {
                "completed": feeding_completed,
                "total": len(FEEDING_TYPES),
                "percentage": (feeding_completed / len(FEEDING_TYPES)) * 100
            }
            
            # Activity completion
            activity_tasks = ["outside", "walked_today", "played_today"]
            activity_completed = 0
            for task in activity_tasks:
                task_state = self.hass.states.get(f"input_boolean.{self.dog_name}_{task}")
                if task_state and task_state.state == "on":
                    activity_completed += 1
            
            completion_metrics["activities"] = {
                "completed": activity_completed,
                "total": len(activity_tasks),
                "percentage": (activity_completed / len(activity_tasks)) * 100
            }
            
            # Overall completion
            total_tasks = len(FEEDING_TYPES) + len(activity_tasks)
            total_completed = feeding_completed + activity_completed
            completion_metrics["overall"] = {
                "completed": total_completed,
                "total": total_tasks,
                "percentage": (total_completed / total_tasks) * 100
            }
            
            status_data["completion_metrics"] = completion_metrics
            
            # Determine overall status
            if status_data["modes"]["emergency_mode"]:
                status_data["overall_status"] = "emergency"
            elif completion_metrics["overall"]["percentage"] >= 80:
                status_data["overall_status"] = "excellent"
            elif completion_metrics["overall"]["percentage"] >= 60:
                status_data["overall_status"] = "good"
            elif completion_metrics["overall"]["percentage"] >= 40:
                status_data["overall_status"] = "needs_attention"
            else:
                status_data["overall_status"] = "concern"
            
            return status_data

        except Exception as e:
            _LOGGER.error("Error collecting status data for %s: %s", self.dog_name, e)
            return {"error": str(e), "overall_status": "unknown"}

    async def _collect_statistics_data(self) -> Dict[str, Any]:
        """Collect system statistics and performance data."""
        try:
            return {
                "coordinator_stats": self._statistics.copy(),
                "data_quality": {
                    "last_successful_update": self._statistics.get("last_successful_update"),
                    "success_rate": (self._statistics["successful_updates"] / max(1, self._statistics["total_data_updates"])) * 100,
                    "average_update_time": self._statistics["average_update_time"]
                },
                "entity_counts": {
                    "total_entities": 143,  # As defined in const.py
                    "active_entities": await self._count_active_entities(),
                    "entities_with_data": await self._count_entities_with_data()
                },
                "data_freshness": {
                    "last_feeding_update": await self._get_last_feeding_update(),
                    "last_activity_update": await self._get_last_activity_update(),
                    "last_gps_update": await self._get_last_gps_update()
                }
            }

        except Exception as e:
            _LOGGER.error("Error collecting statistics data for %s: %s", self.dog_name, e)
            return {"error": str(e)}

    async def _collect_notification_data(self) -> Dict[str, Any]:
        """Collect notification and alert information."""
        try:
            notification_data = {
                "pending_notifications": [],
                "recent_alerts": [],
                "notification_settings": {},
                "priority_alerts": []
            }
            
            # Check for pending notifications based on various conditions
            pending = []
            
            # Feeding reminders
            for meal_type in FEEDING_TYPES:
                meal_state = self.hass.states.get(f"input_boolean.{self.dog_name}_feeding_{meal_type}")
                if not meal_state or meal_state.state != "on":
                    # Check if it's time for this meal
                    if meal_type != "snack":
                        schedule_state = self.hass.states.get(f"input_datetime.{self.dog_name}_feeding_{meal_type}_time")
                        if schedule_state and schedule_state.state not in ["unknown", "unavailable"]:
                            # Simple time-based reminder logic
                            current_hour = datetime.now().hour
                            meal_hour_map = {"morning": 7, "lunch": 12, "evening": 18}
                            if current_hour >= meal_hour_map.get(meal_type, 12):
                                pending.append({
                                    "type": "feeding_reminder",
                                    "meal_type": meal_type,
                                    "message": f"Zeit für {MEAL_TYPES[meal_type]}",
                                    "priority": "normal"
                                })
            
            # Health alerts
            emergency_state = self.hass.states.get(f"input_boolean.{self.dog_name}_emergency_mode")
            if emergency_state and emergency_state.state == "on":
                pending.append({
                    "type": "emergency_alert",
                    "message": "NOTFALLMODUS AKTIV",
                    "priority": "critical"
                })
            
            # GPS alerts
            gps_enabled_state = self.hass.states.get(f"input_boolean.{self.dog_name}_gps_tracking_enabled")
            if gps_enabled_state and gps_enabled_state.state == "on":
                signal_state = self.hass.states.get(f"input_number.{self.dog_name}_gps_signal_strength")
                if signal_state and signal_state.state not in ["unknown", "unavailable"]:
                    signal_strength = float(signal_state.state)
                    if signal_strength < 20:
                        pending.append({
                            "type": "gps_alert",
                            "message": f"GPS Signal schwach ({signal_strength:.0f}%)",
                            "priority": "high"
                        })
                
                battery_state = self.hass.states.get(f"input_number.{self.dog_name}_gps_battery_level")
                if battery_state and battery_state.state not in ["unknown", "unavailable"]:
                    battery_level = float(battery_state.state)
                    if battery_level < 20:
                        pending.append({
                            "type": "battery_alert",
                            "message": f"GPS Akku niedrig ({battery_level:.0f}%)",
                            "priority": "high"
                        })
            
            notification_data["pending_notifications"] = pending
            
            # Separate priority alerts
            notification_data["priority_alerts"] = [n for n in pending if n["priority"] in ["high", "critical"]]
            
            return notification_data

        except Exception as e:
            _LOGGER.error("Error collecting notification data for %s: %s", self.dog_name, e)
            return {"error": str(e), "pending_notifications": []}

    # =========================
    # RECOVERY INTEGRATION: ANALYSIS & ENRICHMENT METHODS
    # =========================

    async def _analyze_and_enrich_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze collected data and add intelligent insights."""
        try:
            # Add behavioral patterns
            data["behavioral_analysis"] = await self._analyze_behavioral_patterns(data)
            
            # Add health insights
            data["health_insights"] = await self._generate_health_insights(data.get("health", {}))
            
            # Add activity recommendations
            data["activity_recommendations"] = await self._generate_activity_recommendations(
                data.get("activities", {}).get("daily_summary", {}),
                data.get("activities", {}).get("current_activities", {})
            )
            
            # Add GPS analytics
            if data.get("gps", {}).get("tracking_status", {}).get("enabled", False):
                data["gps_analytics"] = await self._analyze_gps_patterns(data.get("gps", {}))
            
            # Calculate overall wellness score
            data["wellness_score"] = await self._calculate_wellness_score(data)
            
            # Generate daily summary
            data["daily_summary"] = await self._generate_daily_summary(data)
            
            return data

        except Exception as e:
            _LOGGER.error("Error analyzing and enriching data for %s: %s", self.dog_name, e)
            data["analysis_error"] = str(e)
            return data

    async def _analyze_behavioral_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze behavioral patterns from collected data."""
        try:
            patterns = {
                "feeding_patterns": {},
                "activity_patterns": {},
                "mood_trends": {},
                "sleep_patterns": {},
                "anomalies": []
            }
            
            # Analyze feeding patterns
            feeding_data = data.get("feeding", {})
            if feeding_data:
                meals_today = feeding_data.get("meals_today", {})
                completed_meals = sum(1 for meal in meals_today.values() if meal.get("completed", False))
                
                patterns["feeding_patterns"] = {
                    "regularity_score": (completed_meals / len(FEEDING_TYPES)) * 100,
                    "preferred_meal_times": await self._analyze_meal_timing(meals_today),
                    "appetite_consistency": await self._analyze_appetite_consistency(feeding_data)
                }
            
            # Analyze activity patterns
            activity_data = data.get("activities", {})
            if activity_data:
                daily_summary = activity_data.get("daily_summary", {})
                patterns["activity_patterns"] = {
                    "activity_level": await self._categorize_activity_level(daily_summary),
                    "preferred_activities": await self._identify_preferred_activities(daily_summary),
                    "energy_distribution": await self._analyze_energy_distribution(activity_data)
                }
            
            # Analyze mood trends
            mood = activity_data.get("mood", "😊 Glücklich")
            energy_level = activity_data.get("energy_level", "Normal")
            patterns["mood_trends"] = {
                "current_mood": mood,
                "energy_level": energy_level,
                "mood_stability": await self._assess_mood_stability(mood, energy_level)
            }
            
            return patterns

        except Exception as e:
            _LOGGER.error("Error analyzing behavioral patterns for %s: %s", self.dog_name, e)
            return {"error": str(e)}

    async def _generate_health_insights(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate health insights from health data."""
        try:
            insights = {
                "health_trends": {},
                "risk_factors": [],
                "recommendations": [],
                "alerts": []
            }
            
            # Analyze vital signs
            vital_signs = health_data.get("vital_signs", {})
            if vital_signs:
                # Weight analysis
                weight = vital_signs.get("weight")
                if weight:
                    size_category = await self._get_size_category()
                    weight_status = await self._assess_weight_status(weight, size_category)
                    insights["health_trends"]["weight_status"] = weight_status
                
                # Temperature analysis
                temperature = vital_signs.get("temperature")
                if temperature:
                    temp_status = await self._assess_temperature_status(temperature)
                    insights["health_trends"]["temperature_status"] = temp_status
                    if temp_status != "normal":
                        insights["alerts"].append(f"Körpertemperatur: {temperature}°C ({temp_status})")
                
                # Heart rate analysis
                heart_rate = vital_signs.get("heart_rate")
                if heart_rate:
                    hr_status = await self._assess_heart_rate_status(heart_rate)
                    insights["health_trends"]["heart_rate_status"] = hr_status
            
            # Analyze health scores
            health_scores = health_data.get("health_score", {})
            if health_scores:
                overall_score = health_scores.get("overall", 8)
                if overall_score < 5:
                    insights["risk_factors"].append("Niedriger Gesundheitsscore")
                    insights["recommendations"].append("Tierarztbesuch empfohlen")
            
            # Medication analysis
            medication = health_data.get("medication", {})
            if medication.get("given_today", False):
                insights["health_trends"]["medication_compliance"] = "good"
            else:
                last_medication = medication.get("time_since")
                if last_medication and last_medication.days > 1:
                    insights["alerts"].append("Medikament möglicherweise vergessen")
            
            # Vaccination status analysis
            vaccination = health_data.get("vaccination", {})
            overall_vacc_status = vaccination.get("overall_status", "")
            if "überfällig" in overall_vacc_status.lower():
                insights["risk_factors"].append("Impfungen überfällig")
                insights["recommendations"].append("Impftermin vereinbaren")
            
            return insights

        except Exception as e:
            _LOGGER.error("Error generating health insights for %s: %s", self.dog_name, e)
            return {"error": str(e)}

    async def _calculate_wellness_score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall wellness score from all data."""
        try:
            score_components = {
                "feeding": 0,
                "activity": 0,
                "health": 0,
                "gps_safety": 0
            }
            
            # Feeding score (0-25 points)
            feeding_data = data.get("feeding", {})
            if feeding_data:
                nutrition_summary = feeding_data.get("nutrition_summary", {})
                completion_pct = nutrition_summary.get("completion_percentage", 0)
                score_components["feeding"] = min(25, (completion_pct / 100) * 25)
            
            # Activity score (0-25 points)
            activity_data = data.get("activities", {})
            if activity_data:
                daily_summary = activity_data.get("daily_summary", {})
                walk_duration = daily_summary.get("walk_duration", 0)
                play_duration = daily_summary.get("play_duration", 0)
                
                # Ideal: 60+ min walk, 30+ min play
                activity_score = min(25, (walk_duration / 60) * 15 + (play_duration / 30) * 10)
                score_components["activity"] = activity_score
            
            # Health score (0-35 points)
            health_data = data.get("health", {})
            if health_data:
                health_scores = health_data.get("health_score", {})
                overall_health = health_scores.get("overall", 8)
                happiness = health_scores.get("happiness", 8)
                
                health_score = (overall_health / 10) * 20 + (happiness / 10) * 15
                score_components["health"] = health_score
            
            # GPS Safety score (0-15 points)
            gps_data = data.get("gps", {})
            if gps_data:
                tracking_enabled = gps_data.get("tracking_status", {}).get("enabled", False)
                device_status = gps_data.get("device_status", {})
                signal_strength = device_status.get("signal_strength", 0)
                battery_level = device_status.get("battery_level", 0)
                
                if tracking_enabled:
                    gps_score = 5  # Base score for tracking enabled
                    gps_score += (signal_strength / 100) * 5  # Signal strength
                    gps_score += (battery_level / 100) * 5     # Battery level
                    score_components["gps_safety"] = min(15, gps_score)
            
            # Calculate total score
            total_score = sum(score_components.values())
            
            # Determine wellness level
            if total_score >= 85:
                wellness_level = "Ausgezeichnet"
            elif total_score >= 70:
                wellness_level = "Sehr gut"
            elif total_score >= 55:
                wellness_level = "Gut"
            elif total_score >= 40:
                wellness_level = "Verbesserungsbedarf"
            else:
                wellness_level = "Aufmerksamkeit erforderlich"
            
            return {
                "total_score": round(total_score, 1),
                "wellness_level": wellness_level,
                "components": score_components,
                "recommendations": await self._generate_wellness_recommendations(score_components)
            }

        except Exception as e:
            _LOGGER.error("Error calculating wellness score for %s: %s", self.dog_name, e)
            return {"error": str(e), "total_score": 0}

async def _create_input_datetimes(hass: HomeAssistant, dog_name: str) -> Dict[str, Any]:
    """Create input_datetime entities for comprehensive time tracking."""
    
    datetime_entities = [
        # Last activities
        (f"{dog_name}_last_feeding_morning", "Letztes Frühstück", True, True, None, ICONS["morning"]),
        (f"{dog_name}_last_feeding_lunch", "Letztes Mittagessen", True, True, None, ICONS["lunch"]),
        (f"{dog_name}_last_feeding_evening", "Letztes Abendessen", True, True, None, ICONS["evening"]),
        (f"{dog_name}_last_feeding_snack", "Letztes Leckerli", True, True, None, ICONS["snack"]),
        (f"{dog_name}_last_outside", "Letztes Mal draußen", True, True, None, ICONS["outside"]),
        (f"{dog_name}_last_walk", "Letzter Spaziergang", True, True, None, ICONS["walk"]),
        (f"{dog_name}_last_play", "Letztes Spielen", True, True, None, ICONS["play"]),
        (f"{dog_name}_last_training", "Letztes Training", True, True, None, ICONS["training"]),
        (f"{dog_name}_last_poop", "Letztes Geschäft", True, True, None, ICONS["poop"]),
        (f"{dog_name}_last_activity", "Letzte Aktivität", True, True, None, ICONS["status"]),
        (f"{dog_name}_last_door_ask", "Letzte Türfrage", True, True, None, "mdi:door"),

        # Feeding times
        (f"{dog_name}_feeding_morning_time", "Frühstück Zeit", True, False, DEFAULT_FEEDING_TIMES_DICT["morning"], ICONS["morning"]),
        (f"{dog_name}_feeding_lunch_time", "Mittagessen Zeit", True, False, DEFAULT_FEEDING_TIMES_DICT["lunch"], ICONS["lunch"]),
        (f"{dog_name}_feeding_evening_time", "Abendessen Zeit", True, False, DEFAULT_FEEDING_TIMES_DICT["evening"], ICONS["evening"]),
        
        # Health & veterinary
        (f"{dog_name}_last_vet_visit", "Letzter Tierarztbesuch", True, True, None, ICONS["vet"]),
        (f"{dog_name}_next_vet_appointment", "Nächster Tierarzttermin", True, True, None, ICONS["vet"]),
        (f"{dog_name}_last_grooming", "Letzte Pflege", True, True, None, ICONS["grooming"]),
        (f"{dog_name}_next_grooming", "Nächste Pflege", True, True, None, ICONS["grooming"]),
        (f"{dog_name}_last_weight_check", "Letzte Gewichtskontrolle", True, True, None, "mdi:weight-kilogram"), 
        
        # Medication tracking
        (f"{dog_name}_last_medication", "Letzte Medikamentengabe", True, True, None, ICONS["medication"]),
        (f"{dog_name}_next_medication", "Nächste Medikamentengabe", True, True, None, ICONS["medication"]),
        
        # Special dates
        (f"{dog_name}_birth_date", "Geburtsdatum", False, True, None, ICONS["dog"]),
        
        # *** IMPFUNGS-TRACKING ***
        # Allgemeine Impfungen
        (f"{dog_name}_last_vaccination", "Letzte Impfung", True, True, None, "mdi:needle"),
        (f"{dog_name}_next_vaccination", "Nächste Impfung", True, True, None, "mdi:needle"),
        
        # Spezifische Impfungen
        (f"{dog_name}_last_rabies_vaccination", "Letzte Tollwut-Impfung", True, True, None, "mdi:needle"),
        (f"{dog_name}_next_rabies_vaccination", "Nächste Tollwut-Impfung", True, True, None, "mdi:needle"),
        (f"{dog_name}_last_distemper_vaccination", "Letzte Staupe-Impfung", True, True, None, "mdi:needle"),
        (f"{dog_name}_next_distemper_vaccination", "Nächste Staupe-Impfung", True, True, None, "mdi:needle"),
        (f"{dog_name}_last_hepatitis_vaccination", "Letzte Hepatitis-Impfung", True, True, None, "mdi:needle"),
        (f"{dog_name}_next_hepatitis_vaccination", "Nächste Hepatitis-Impfung", True, True, None, "mdi:needle"),
    ]

    return await _create_helpers_for_domain_ultra_robust(hass, "input_datetime", datetime_entities, dog_name)

async def _create_input_texts(hass: HomeAssistant, dog_name: str) -> Dict[str, Any]:
    """Create input_text entities for comprehensive information storage."""
    
    text_entities = [
        # Basic information
        (f"{dog_name}_notes", "Allgemeine Notizen", 255, ICONS["notes"]),
        (f"{dog_name}_daily_notes", "Tagesnotizen", 255, ICONS["notes"]),
        (f"{dog_name}_behavior_notes", "Verhaltensnotizen", 255, ICONS["notes"]),
        
        # Dog information
        (f"{dog_name}_breed", "Rasse", 100, ICONS["dog"]),
        (f"{dog_name}_color", "Farbe/Markierungen", 100, ICONS["dog"]),
        (f"{dog_name}_microchip_id", "Mikrochip ID", 50, "mdi:chip"),
        (f"{dog_name}_insurance_number", "Versicherungsnummer", 100, "mdi:shield"),
        
        # Contact information
        (f"{dog_name}_emergency_contact", "Notfallkontakt", 255, ICONS["emergency"]),
        (f"{dog_name}_vet_contact", "Tierarzt Kontakt", 255, ICONS["vet"]),
        (f"{dog_name}_backup_contact", "Ersatzkontakt", 200, "mdi:phone"),
        
        # Health tracking
        (f"{dog_name}_health_notes", "Gesundheitsnotizen", 500, ICONS["health"]),
        (f"{dog_name}_medication_notes", "Medikamenten Notizen", 500, ICONS["medication"]),
        (f"{dog_name}_allergies", "Allergien", 255, ICONS["health"]),
        (f"{dog_name}_symptoms", "Aktuelle Symptome", 255, ICONS["health"]),

        # *** IMPFUNGS-AUFZEICHNUNGEN ***
        (f"{dog_name}_vaccination_records", "Impfaufzeichnungen", 500, "mdi:needle"),
        (f"{dog_name}_vaccination_notes", "Impfnotizen", 255, "mdi:needle"),
        (f"{dog_name}_rabies_vaccination_batch", "Tollwut-Impfstoff Charge", 100, "mdi:needle"),
        (f"{dog_name}_distemper_vaccination_batch", "Staupe-Impfstoff Charge", 100, "mdi:needle"),
        (f"{dog_name}_vaccination_veterinarian", "Impftierarzt", 150, ICONS["vet"]),
        (f"{dog_name}_vaccination_location", "Impfort", 150, "mdi:map-marker"),
        
        # Activity tracking
        (f"{dog_name}_last_activity_notes", "Letzte Aktivität Notizen", 255, ICONS["notes"]),
        (f"{dog_name}_walk_notes", "Spaziergang Notizen", 255, ICONS["walk"]),
        (f"{dog_name}_play_notes", "Spiel Notizen", 255, ICONS["play"]),
        (f"{dog_name}_training_notes", "Training Notizen", 255, ICONS["training"]),
        
        # GPS & Location tracking
        (f"{dog_name}_current_location", "Aktuelle Position", 100, "mdi:map-marker"),
        (f"{dog_name}_home_coordinates", "Heimat Koordinaten", 100, "mdi:home-map-marker"),
        (f"{dog_name}_favorite_walks", "Lieblings Spaziergänge", 500, ICONS["walk"]),
        (f"{dog_name}_current_walk_route", "Aktuelle Spaziergang Route", 1000, "mdi:route"),
        (f"{dog_name}_walk_history_today", "Heutige Spaziergänge", 1000, ICONS["walk"]),
        (f"{dog_name}_gps_tracker_status", "GPS Tracker Status", 100, "mdi:crosshairs-gps"),
        
        # Visitor information
        (f"{dog_name}_visitor_name", "Besuchername", 100, ICONS["visitor"]),
        (f"{dog_name}_visitor_contact", "Besucher Kontakt", 200, ICONS["visitor"]),
        (f"{dog_name}_visitor_notes", "Besucher Notizen", 255, ICONS["visitor"]),
        (f"{dog_name}_visitor_instructions", "Anweisungen für Besucher", 255, ICONS["visitor"]),
        
        # Food preferences
        (f"{dog_name}_food_brand", "Futtermarke", 100, ICONS["food"]),
        (f"{dog_name}_food_allergies", "Futterallergien", 255, ICONS["food"]),
        (f"{dog_name}_favorite_treats", "Lieblingsleckerli", 255, ICONS["snack"]),
        (f"{dog_name}_feeding_instructions", "Fütterungsanweisungen", 255, ICONS["food"]),
    ]
    
    return await _create_helpers_for_domain_ultra_robust(hass, "input_text", text_entities, dog_name)


async def _create_input_numbers(hass: HomeAssistant, dog_name: str) -> Dict[str, Any]:
    """Create input_number entities for comprehensive metric tracking."""
    
    number_entities = [
        # Basic measurements
        (f"{dog_name}_weight", "Gewicht", 0.1, 0, 100, 10, "kg", ICONS["weight"]),
        (f"{dog_name}_target_weight", "Zielgewicht", 0.1, 0, 100, 10, "kg", "mdi:target"),
        (f"{dog_name}_height", "Größe", 1, 10, 100, 50, "cm", "mdi:ruler"),
        (f"{dog_name}_length", "Länge", 1, 20, 150, 80, "cm", "mdi:ruler"),
        
        # Health metrics
        (f"{dog_name}_temperature", "Temperatur", 0.1, 35, 42, 38.5, "°C", ICONS["health"]),
        (f"{dog_name}_heart_rate", "Herzfrequenz", 1, 60, 200, 100, "bpm", "mdi:heart-pulse"),
        (f"{dog_name}_health_score", "Gesundheits Score", 0.1, 0, 10, 8, "Punkte", ICONS["health"]),
        
        # Daily metrics
        (f"{dog_name}_daily_food_amount", "Tägliche Futtermenge", 10, 0, 2000, 400, "g", ICONS["food"]),
        (f"{dog_name}_daily_water_amount", "Tägliche Wassermenge", 50, 0, 3000, 500, "ml", "mdi:cup-water"),
        (f"{dog_name}_daily_walk_duration", "Tägliche Spaziergang Dauer", 1, 0, 300, 60, "min", ICONS["walk"]),
        (f"{dog_name}_daily_play_duration", "Tägliche Spielzeit", 1, 0, 180, 30, "min", ICONS["play"]),
        (f"{dog_name}_daily_training_duration", "Tägliche Trainingszeit", 1, 0, 120, 15, "min", ICONS["training"]),
        (f"{dog_name}_sleep_hours", "Schlafstunden", 0.5, 0, 24, 12, "h", "mdi:sleep"),
        
        # GPS & Location metrics
        (f"{dog_name}_current_walk_distance", "Aktuelle Spaziergang Distanz", 0.1, 0, 50, 0, "km", ICONS["walk"]),
        (f"{dog_name}_current_walk_duration", "Aktuelle Spaziergang Dauer", 1, 0, 300, 0, "min", ICONS["walk"]),
        (f"{dog_name}_current_walk_speed", "Aktuelle Geschwindigkeit", 0.1, 0, 20, 0, "km/h", "mdi:speedometer"),
        (f"{dog_name}_walk_distance_today", "Heutige Spaziergang Distanz", 0.1, 0, 30, 0, "km", ICONS["walk"]),
        (f"{dog_name}_walks_count_today", "Anzahl Spaziergänge heute", 1, 0, 20, 0, "count", ICONS["walk"]),
        (f"{dog_name}_calories_burned_walk", "Verbrannte Kalorien Spaziergang", 10, 0, 1000, 0, "kcal", "mdi:fire"),
        (f"{dog_name}_gps_battery_level", "GPS Tracker Akku", 1, 0, 100, 100, "%", "mdi:battery"),
        (f"{dog_name}_gps_signal_strength", "GPS Signal Stärke", 1, 0, 100, 100, "%", "mdi:signal"),
        (f"{dog_name}_home_latitude", "Heimat Breitengrad", 0.000001, -90, 90, 52.233333, "°", "mdi:latitude"),
        (f"{dog_name}_home_longitude", "Heimat Längengrad", 0.000001, -180, 180, 8.966667, "°", "mdi:longitude"),
        (f"{dog_name}_current_latitude", "Aktuelle Breite", 0.000001, -90, 90, 52.233333, "°", "mdi:latitude"),
        (f"{dog_name}_current_longitude", "Aktuelle Länge", 0.000001, -180, 180, 8.966667, "°", "mdi:longitude"),
        
        # Age and lifespan
        (f"{dog_name}_age_years", "Alter", 0.1, 0, 30, 5, "Jahre", ICONS["dog"]),
        (f"{dog_name}_age_months", "Alter", 1, 0, 360, 60, "Monate", ICONS["dog"]),
        (f"{dog_name}_expected_lifespan", "Erwartete Lebenszeit", 1, 8, 25, 14, "Jahre", ICONS["dog"]),
        
        # Behavioral metrics
        (f"{dog_name}_stress_level", "Stress Level", 1, 0, 10, 3, "level", "mdi:emoticon-neutral"),
        (f"{dog_name}_energy_level", "Energie Level", 1, 0, 10, 7, "level", ICONS["play"]),
        (f"{dog_name}_socialization_score", "Sozialisation Score", 1, 0, 100, 75, "points", "mdi:account-group"),
        (f"{dog_name}_happiness_score", "Glücks Score", 0.1, 0, 10, 8, "Punkte", ICONS["mood"]),
        (f"{dog_name}_appetite_score", "Appetit Score", 0.1, 0, 10, 8, "Punkte", ICONS["food"]),
        
        # Tracking & statistics
        (f"{dog_name}_days_since_vet", "Tage seit Tierarzt", 1, 0, 1000, 0, "days", ICONS["vet"]),
        (f"{dog_name}_days_since_grooming", "Tage seit Pflege", 1, 0, 365, 0, "days", ICONS["grooming"]),
        (f"{dog_name}_feeding_streak", "Fütterungs Serie", 1, 0, 1000, 0, "days", ICONS["food"]),
        (f"{dog_name}_walk_streak", "Spaziergang Serie", 1, 0, 1000, 0, "days", ICONS["walk"]),
    ]
    
    return await _create_helpers_for_domain_ultra_robust(hass, "input_number", number_entities, dog_name)


async def _create_input_selects(hass: HomeAssistant, dog_name: str) -> Dict[str, Any]:
    """Create input_select entities for comprehensive categorical tracking."""
    
    select_entities = [
        # Core status selects
        (f"{dog_name}_health_status", "Gesundheitsstatus", [
            "Ausgezeichnet", "Sehr gut", "Gut", "Durchschnittlich", "Schlecht", "Krank"
        ], "Gut", ICONS["health"]),
        
        # *** IMPFSTATUS-AUSWAHLEN ***
        (f"{dog_name}_vaccination_status", "Impfstatus", [
            "Vollständig", "Aktuell", "Auffrischung fällig", "Überfällig", "Ungeimpft", "Teilweise"
        ], "Vollständig", "mdi:needle"),
        
        (f"{dog_name}_rabies_vaccination_status", "Tollwut-Impfstatus", [
            "Aktuell", "Auffrischung fällig", "Überfällig", "Nie geimpft", "Unbekannt"
        ], "Aktuell", "mdi:needle"),
        
        (f"{dog_name}_distemper_vaccination_status", "Staupe-Impfstatus", [
            "Aktuell", "Auffrischung fällig", "Überfällig", "Nie geimpft", "Unbekannt"
        ], "Aktuell", "mdi:needle"),

        (f"{dog_name}_mood", "Stimmung", [
            "😄 Sehr fröhlich", "😊 Fröhlich", "😐 Neutral", "😟 Traurig", "😠 Ärgerlich", "😴 Müde"
        ], "😊 Fröhlich", ICONS["mood"]),
        
        (f"{dog_name}_activity_level", "Aktivitätslevel", [
            "Sehr niedrig", "Niedrig", "Normal", "Hoch", "Sehr hoch"
        ], "Normal", ICONS["play"]),
        
        (f"{dog_name}_appetite_level", "Appetit Level", [
            "Kein Appetit", "Wenig Appetit", "Normal", "Guter Appetit", "Sehr hungrig"
        ], "Normal", ICONS["food"]),
        
        (f"{dog_name}_energy_level_category", "Energie Kategorie", [
            "Sehr müde", "Müde", "Normal", "Energiegeladen", "Hyperaktiv"
        ], "Normal", ICONS["play"]),
        
        # Size and physical characteristics
        (f"{dog_name}_size_category", "Größenkategorie", [
            "Toy (< 4kg)", "Klein (4-10kg)", "Mittel (10-25kg)", "Groß (25-45kg)", "Riesig (> 45kg)"
        ], "Mittel (10-25kg)", ICONS["dog"]),
        
        (f"{dog_name}_coat_type", "Felltyp", [
            "Kurzhaar", "Langhaar", "Stockhaar", "Drahthaar", "Locken", "Haarlos"
        ], "Kurzhaar", ICONS["grooming"]),
        
        # Age group
        (f"{dog_name}_age_group", "Altersgruppe", [
            "Welpe (< 6 Monate)", "Junghund (6-18 Monate)", "Erwachsen (1-7 Jahre)", 
            "Senior (7-10 Jahre)", "Hochbetagt (> 10 Jahre)"
        ], "Erwachsen (1-7 Jahre)", ICONS["dog"]),
        
        # Training and behavior
        (f"{dog_name}_training_level", "Trainingslevel", [
            "Anfänger", "Grundlagen", "Fortgeschritten", "Experte", "Profi"
        ], "Grundlagen", ICONS["training"]),
        
        (f"{dog_name}_obedience_level", "Gehorsam Level", [
            "Sehr niedrig", "Niedrig", "Durchschnittlich", "Gut", "Ausgezeichnet"
        ], "Durchschnittlich", ICONS["training"]),
        
        # Environmental preferences
        (f"{dog_name}_weather_preference", "Wetter Präferenz", [
            "Sonnig", "Bewölkt", "Regnerisch", "Schnee", "Alle Wetter"
        ], "Sonnig", "mdi:weather-sunny"),
        
        (f"{dog_name}_seasonal_mode", "Jahreszeit Modus", [
            "Frühling", "Sommer", "Herbst", "Winter"
        ], "Sommer", "mdi:calendar"),
        
        # Emergency and special situations
        (f"{dog_name}_emergency_level", "Notfall Level", [
            "Normal", "Leichte Sorge", "Überwachung", "Dringend", "Kritisch"
        ], "Normal", ICONS["emergency"]),
              
        # Living situation and social
        (f"{dog_name}_living_situation", "Wohnsituation", [
            "Wohnung", "Haus mit Garten", "Haus mit großem Garten", "Bauernhof", "Andere"
        ], "Haus mit Garten", "mdi:home"),
        
        (f"{dog_name}_socialization", "Sozialverhalten", [
            "Sehr schüchtern", "Schüchtern", "Normal", "Gesellig", "Sehr gesellig"
        ], "Normal", ICONS["dog"]),
    ]
    
    return await _create_helpers_for_domain_ultra_robust(hass, "input_select", select_entities, dog_name)


async def _create_helpers_for_domain_ultra_robust(
    hass: HomeAssistant, 
    domain: str, 
    entities: List[Tuple], 
    dog_name: str
) -> Dict[str, Any]:
    """Create helpers for a specific domain with GUARANTEED success."""
    
    results = {
        "created": 0,
        "skipped": 0,
        "failed": 0,
        "failed_entities": [],
        "domain": domain,
        "retry_details": {},
        "verification_details": {}
    }
    
    _LOGGER.info("🔧 Creating %d %s entities for %s (ULTRA-ROBUST MODE)", 
                len(entities), domain, dog_name)
    
    # PROCESS IN ULTRA-SMALL BATCHES
    for batch_start in range(0, len(entities), BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, len(entities))
        batch = entities[batch_start:batch_end]
        
        _LOGGER.debug("📦 Processing batch %d-%d for %s", batch_start + 1, batch_end, domain)
        
        for entity_data in batch:
            entity_name = entity_data[0]
            friendly_name = entity_data[1]
            entity_id = f"{domain}.{entity_name}"
            
            # SKIP CHECK WITH ULTRA-VERIFICATION
            if await _ultra_entity_exists_check(hass, entity_id):
                _LOGGER.debug("⏭️ Entity %s already exists, skipping", entity_id)
                results["skipped"] += 1
                continue
            
            # ULTRA-ENHANCED RETRY MECHANISM
            success = False
            retry_details = []
            
            for attempt in range(MAX_RETRIES_PER_ENTITY):
                attempt_start = datetime.now()
                
                try:
                    # BUILD SERVICE DATA WITH VALIDATION
                    service_data = await _build_service_data_ultra_safe(domain, entity_data, dog_name)
                    
                    # PRE-CREATION VALIDATION
                    if not await _validate_service_data(hass, domain, service_data):
                        retry_details.append(f"Attempt {attempt + 1}: Invalid service data")
                        continue
                    
                    # ULTRA-SAFE SERVICE CALL
                    await asyncio.wait_for(
                        hass.services.async_call(domain, "create", service_data, blocking=True),
                        timeout=ENTITY_CREATION_TIMEOUT
                    )
                    
                    # EXTENDED VERIFICATION WAIT
                    await asyncio.sleep(VERIFICATION_DELAY)
                    
                    # COMPREHENSIVE ENTITY VERIFICATION
                    verification_result = await _ultra_verify_entity_creation(hass, entity_id, service_data)
                    
                    if verification_result["exists"] and verification_result["correct_state"]:
                        attempt_duration = (datetime.now() - attempt_start).total_seconds()
                        _LOGGER.debug("✅ Created %s: %s (%.2fs)", domain, entity_id, attempt_duration)
                        
                        results["created"] += 1
                        results["verification_details"][entity_id] = verification_result
                        success = True
                        break
                    else:
                        retry_details.append(f"Attempt {attempt + 1}: Verification failed - {verification_result}")
                        _LOGGER.warning("⚠️ Entity %s verification failed (attempt %d/%d): %s", 
                                      entity_id, attempt + 1, MAX_RETRIES_PER_ENTITY, verification_result)
                        
                except asyncio.TimeoutError:
                    retry_details.append(f"Attempt {attempt + 1}: Timeout after {ENTITY_CREATION_TIMEOUT}s")
                    _LOGGER.warning("⏱️ Timeout creating %s (attempt %d/%d): %s", 
                                   domain, attempt + 1, MAX_RETRIES_PER_ENTITY, entity_id)
                    
                except Exception as e:
                    retry_details.append(f"Attempt {attempt + 1}: Exception - {str(e)}")
                    _LOGGER.warning("❌ Error creating %s (attempt %d/%d): %s - %s", 
                                   domain, attempt + 1, MAX_RETRIES_PER_ENTITY, entity_id, e)
                
                # EXPONENTIAL BACKOFF WITH JITTER
                if attempt < MAX_RETRIES_PER_ENTITY - 1:
                    base_delay = 2.0 ** attempt  # 2s, 4s, 8s, 16s, 32s...
                    jitter = 0.5 * (attempt + 1)  # Add jitter to prevent thundering herd
                    total_delay = min(base_delay + jitter, 60.0)  # Cap at 60s
                    
                    _LOGGER.debug("⏳ Waiting %.1fs before retry %d", total_delay, attempt + 2)
                    await asyncio.sleep(total_delay)
            
            # RECORD RESULTS
            if success:
                results["retry_details"][entity_id] = {
                    "attempts": len(retry_details) + 1,
                    "details": retry_details,
                    "final_status": "success"
                }
            else:
                _LOGGER.error("❌ FAILED to create %s after %d attempts: %s", 
                             domain, MAX_RETRIES_PER_ENTITY, entity_id)
                results["failed"] += 1
                results["failed_entities"].append(entity_id)
                results["retry_details"][entity_id] = {
                    "attempts": MAX_RETRIES_PER_ENTITY,
                    "details": retry_details,
                    "final_status": "failed"
                }
            
            # INTER-ENTITY STABILIZATION
            await asyncio.sleep(DOMAIN_CREATION_DELAY)
        
        # INTER-BATCH STABILIZATION
        if batch_end < len(entities):
            _LOGGER.debug("⏳ Inter-batch stabilization...")
            await asyncio.sleep(INTER_BATCH_DELAY)
    
    success_rate = ((results["created"] + results["skipped"]) / len(entities)) * 100 if entities else 100
    
    _LOGGER.info("📊 Domain %s results for %s: %d created, %d skipped, %d failed (%.1f%% success)", 
                 domain, dog_name, results["created"], results["skipped"], 
                 results["failed"], success_rate)
    
    if results["failed_entities"]:
        _LOGGER.error("❌ Failed entities in %s: %s", domain, results["failed_entities"])
    
    return results


# Continue with remaining utility functions...
async def _ultra_entity_exists_check(hass: HomeAssistant, entity_id: str) -> bool:
    """Ultra-thorough entity existence check."""
    try:
        # Check 1: State registry
        state = hass.states.get(entity_id)
        if state and state.state not in ["unknown", "unavailable"]:
            return True
        
        # Check 2: Wait and re-check (for eventual consistency)
        await asyncio.sleep(1.0)
        state = hass.states.get(entity_id)
        if state and state.state not in ["unknown", "unavailable"]:
            return True
        
        return False
        
    except Exception as e:
        _LOGGER.debug("Error in entity existence check for %s: %s", entity_id, e)
        return False


async def _build_service_data_ultra_safe(domain: str, entity_data: Tuple, dog_name: str) -> Dict[str, Any]:
    """Build service data with ultra-safe validation."""
    
    if not entity_data or len(entity_data) < 2:
        raise ValueError(f"Invalid entity data: {entity_data}")
    
    entity_name = entity_data[0]
    friendly_name = entity_data[1]
    
    # Validate entity name
    if not entity_name or not isinstance(entity_name, str):
        raise ValueError(f"Invalid entity name: {entity_name}")
    
    if not friendly_name or not isinstance(friendly_name, str):
        raise ValueError(f"Invalid friendly name: {friendly_name}")
    
    # Sanitize names
    entity_name = str(entity_name).strip()
    friendly_name = str(friendly_name).strip()
    dog_name = str(dog_name).strip()
    
    service_data = {
        "name": f"{dog_name.title()} {friendly_name}",
    }
    
    try:
        if domain == "input_boolean":
            icon = entity_data[2] if len(entity_data) > 2 else "mdi:dog"
            service_data.update({
                "icon": str(icon) if icon else "mdi:dog"
            })
            
        elif domain == "counter":
            icon = entity_data[2] if len(entity_data) > 2 else "mdi:counter"
            service_data.update({
                "initial": 0,
                "step": 1,
                "minimum": 0,
                "maximum": 999999,  # Very high maximum
                "icon": str(icon) if icon else "mdi:counter",
                "restore": True
            })
            
        elif domain == "input_datetime":
            if len(entity_data) < 6:
                raise ValueError(f"Insufficient data for input_datetime: {entity_data}")
            
            has_time, has_date, initial = entity_data[2], entity_data[3], entity_data[4]
            icon = entity_data[5] if len(entity_data) > 5 else "mdi:calendar-clock"
            
            service_data.update({
                "has_time": bool(has_time),
                "has_date": bool(has_date),
                "icon": str(icon) if icon else "mdi:calendar-clock"
            })
            
            if initial and str(initial) not in ["None", "null", ""]:
                service_data["initial"] = str(initial)
                
        elif domain == "input_text":
            max_length = entity_data[2] if len(entity_data) > 2 else 255
            icon = entity_data[3] if len(entity_data) > 3 else "mdi:text"
            
            service_data.update({
                "max": max(1, min(int(max_length), 255)),  # Clamp between 1-255
                "initial": "",
                "icon": str(icon) if icon else "mdi:text",
                "mode": "text"
            })
            
        elif domain == "input_number":
            if len(entity_data) < 8:
                raise ValueError(f"Insufficient data for input_number: {entity_data}")
            
            step, min_val, max_val, initial, unit = entity_data[2:7]
            icon = entity_data[7] if len(entity_data) > 7 else "mdi:numeric"
            
            # Validate and sanitize numeric values
            step = max(0.01, float(step))
            min_val = float(min_val)
            max_val = max(min_val + step, float(max_val))
            initial = max(min_val, min(max_val, float(initial)))
            
            service_data.update({
                "min": min_val,
                "max": max_val,
                "step": step,
                "initial": initial,
                "unit_of_measurement": str(unit) if unit else "",
                "icon": str(icon) if icon else "mdi:numeric",
                "mode": "slider"
            })
            
        elif domain == "input_select":
            if len(entity_data) < 4:
                raise ValueError(f"Insufficient data for input_select: {entity_data}")
            
            options, initial = entity_data[2], entity_data[3]
            icon = entity_data[4] if len(entity_data) > 4 else "mdi:format-list-bulleted"
            
            # Validate options
            if not options or not isinstance(options, (list, tuple)):
                options = ["Option 1", "Option 2"]
            
            options_list = [str(opt) for opt in options if opt]
            if not options_list:
                options_list = ["Option 1"]
            
            # Validate initial
            initial_str = str(initial) if initial else options_list[0]
            if initial_str not in options_list:
                initial_str = options_list[0]
            
            service_data.update({
                "options": options_list,
                "initial": initial_str,
                "icon": str(icon) if icon else "mdi:format-list-bulleted"
            })
        
        return service_data
        
    except Exception as e:
        _LOGGER.error("Error building service data for %s %s: %s", domain, entity_name, e)
        raise ValueError(f"Failed to build service data: {e}")


async def _validate_service_data(hass: HomeAssistant, domain: str, service_data: Dict[str, Any]) -> bool:
    """Validate service data before creation."""
    try:
        # Basic validation
        if not service_data or not isinstance(service_data, dict):
            return False
        
        if "name" not in service_data or not service_data["name"]:
            return False
        
        # Domain-specific validation
        if domain == "input_number":
            min_val = service_data.get("min", 0)
            max_val = service_data.get("max", 100)
            initial = service_data.get("initial", 0)
            step = service_data.get("step", 1)
            
            if min_val >= max_val:
                return False
            if initial < min_val or initial > max_val:
                return False
            if step <= 0:
                return False
                
        elif domain == "input_select":
            options = service_data.get("options", [])
            initial = service_data.get("initial", "")
            
            if not options or not isinstance(options, list):
                return False
            if initial not in options:
                return False
        
        return True
        
    except Exception as e:
        _LOGGER.debug("Service data validation error: %s", e)
        return False


async def _ultra_verify_entity_creation(hass: HomeAssistant, entity_id: str, expected_data: Dict[str, Any]) -> Dict[str, Any]:
    """Ultra-comprehensive entity verification."""
    
    verification_result = {
        "exists": False,
        "correct_state": False,
        "attributes_match": False,
        "details": {},
        "errors": []
    }
    
    try:
        # Check 1: Basic existence
        state = hass.states.get(entity_id)
        if not state:
            verification_result["errors"].append("Entity not found in state registry")
            return verification_result
        
        verification_result["exists"] = True
        verification_result["details"]["state"] = state.state
        verification_result["details"]["attributes"] = dict(state.attributes)
        
        # Check 2: State validity
        if state.state in ["unknown", "unavailable"]:
            # Wait and re-check
            await asyncio.sleep(2.0)
            state = hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                verification_result["correct_state"] = True
            else:
                verification_result["errors"].append(f"Invalid state: {state.state if state else 'None'}")
        else:
            verification_result["correct_state"] = True
        
        # Check 3: Attributes validation
        if state and state.attributes:
            expected_name = expected_data.get("name", "")
            actual_name = state.attributes.get("friendly_name", "")
            
            if expected_name and expected_name == actual_name:
                verification_result["attributes_match"] = True
            elif expected_name and expected_name in actual_name:
                verification_result["attributes_match"] = True
                verification_result["details"]["name_partial_match"] = True
            else:
                verification_result["errors"].append(f"Name mismatch: expected '{expected_name}', got '{actual_name}'")
        
        return verification_result
        
    except Exception as e:
        verification_result["errors"].append(f"Verification exception: {e}")
        return verification_result


def _calculate_final_success_rate(results: Dict[str, Any]) -> float:
    """Calculate the final success rate across all domains."""
    try:
        total_attempted = results["total_created"] + results["total_failed"]
        if total_attempted == 0:
            return 100.0  # No entities to create
        
        # Success includes created + skipped (already existing)
        total_successful = results["total_created"] + results["total_skipped"]
        total_processed = total_successful + results["total_failed"]
        
        if total_processed == 0:
            return 100.0
        
        success_rate = (total_successful / total_processed) * 100
        return round(success_rate, 2)
        
    except Exception as e:
        _LOGGER.error("Error calculating success rate: %s", e)
        return 0.0


async def _send_ultra_completion_notification(hass: HomeAssistant, dog_name: str, 
                                            results: Dict[str, Any], success_rate: float) -> None:
    """Send ultra-detailed completion notification."""
    try:
        # Determine notification style based on success rate
        if success_rate >= 100.0:
            icon = "🎯"
            title = f"{icon} PERFEKT - {dog_name.title()}"
            message = f"✅ 100% ERFOLG!\n{results['total_created']} Entitäten erstellt\n{results['total_skipped']} bereits vorhanden"
        elif success_rate >= 95.0:
            icon = "🏆"
            title = f"{icon} EXZELLENT - {dog_name.title()}"
            message = f"🌟 {success_rate:.1f}% Erfolg!\n{results['total_created']} erstellt, {results['total_failed']} fehlgeschlagen"
        else:
            icon = "⚠️"
            title = f"{icon} ABGESCHLOSSEN - {dog_name.title()}"
            message = f"⚡ {success_rate:.1f}% Erfolg!\n{results['total_created']} erstellt, {results['total_failed']} fehlgeschlagen"
        
        await hass.services.async_call(
            "persistent_notification", "create",
            {
                "title": title,
                "message": message,
                "notification_id": f"paw_control_setup_{dog_name}_{datetime.now().timestamp()}",
            },
            blocking=False
        )
        
    except Exception as e:
        _LOGGER.error("Error sending completion notification: %s", e)


async def _send_error_notification(hass: HomeAssistant, dog_name: str, error: str) -> None:
    """Send error notification."""
    try:
        await hass.services.async_call(
            "persistent_notification", "create",
            {
                "title": f"🚨 FEHLER - Paw Control {dog_name.title()}",
                "message": f"❌ Kritischer Fehler beim Setup:\n\n{error}\n\nBitte Logs prüfen und erneut versuchen.",
                "notification_id": f"paw_control_error_{dog_name}_{datetime.now().timestamp()}",
            },
            blocking=False
        )
    except Exception as e:
        _LOGGER.error("Error sending error notification: %s", e)

    # =========================
    # ADDITIONAL HELPER METHODS FOR ANALYSIS
    # =========================

    async def _generate_health_alerts(self, health_data: Dict[str, Any]) -> List[str]:
        """Generate health alerts based on current health data."""
        try:
            alerts = []
            
            # Emergency mode check
            if health_data.get("emergency_mode", False):
                alerts.append("🚨 NOTFALLMODUS AKTIV")
            
            # Vital signs checks
            vital_signs = health_data.get("vital_signs", {})
            
            temperature = vital_signs.get("temperature")
            if temperature:
                if temperature < 37.5 or temperature > 39.5:
                    alerts.append(f"🌡️ Körpertemperatur auffällig: {temperature}°C")
            
            # Health status check
            current_status = health_data.get("current_status", {})
            if not current_status.get("feeling_well", True):
                alerts.append("😟 Hund fühlt sich nicht wohl")
            
            if not current_status.get("appetite_normal", True):
                alerts.append("🍽️ Appetit nicht normal")
            
            # Medication check
            medication = health_data.get("medication", {})
            if medication.get("time_since"):
                days_since = medication["time_since"].days
                if days_since > 1:
                    alerts.append(f"💊 Medikament seit {days_since} Tagen nicht gegeben")
            
            # Vaccination alerts
            vaccination = health_data.get("vaccination", {})
            for vacc_type in ["rabies", "distemper", "hepatitis"]:
                status = vaccination.get(f"{vacc_type}_status", "")
                if "überfällig" in status.lower():
                    alerts.append(f"💉 {vacc_type.title()} Impfung überfällig")
            
            return alerts

        except Exception as e:
            _LOGGER.error("Error generating health alerts: %s", e)
            return ["Fehler beim Generieren von Gesundheitswarnungen"]

    async def _generate_activity_recommendations(self, daily_summary: Dict[str, Any], current_activities: Dict[str, Any]) -> List[str]:
        """Generate activity recommendations based on current status."""
        try:
            recommendations = []
            
            walk_duration = daily_summary.get("walk_duration", 0)
            play_duration = daily_summary.get("play_duration", 0)
            is_outside = current_activities.get("is_outside", False)
            walk_in_progress = current_activities.get("walk_in_progress", False)
            
            # Walk recommendations
            if walk_duration < 30 and not walk_in_progress:
                if is_outside:
                    recommendations.append("🚶 Spaziergang starten - bereits draußen!")
                else:
                    recommendations.append("🚶 Zeit für einen Spaziergang")
            elif walk_duration >= 60:
                recommendations.append("✅ Tägliches Gehziel erreicht!")
            
            # Play recommendations
            if play_duration < 15:
                recommendations.append("🎾 Spielzeit einplanen")
            elif play_duration >= 30:
                recommendations.append("✅ Ausreichend gespielt heute!")
            
            # Time-based recommendations
            current_hour = datetime.now().hour
            if 6 <= current_hour <= 9 and walk_duration == 0:
                recommendations.append("🌅 Morgenspaziergang empfohlen")
            elif 17 <= current_hour <= 20 and walk_duration < 45:
                recommendations.append("🌆 Abendspaziergang einplanen")
            
            return recommendations

        except Exception as e:
            _LOGGER.error("Error generating activity recommendations: %s", e)
            return ["Fehler beim Generieren von Empfehlungen"]

    async def _analyze_meal_timing(self, meals_today: Dict[str, Any]) -> Dict[str, str]:
        """Analyze preferred meal timing patterns."""
        try:
            preferred_times = {}
            
            for meal_type, meal_data in meals_today.items():
                if meal_data.get("completed", False) and meal_data.get("last_time"):
                    try:
                        meal_time = datetime.fromisoformat(meal_data["last_time"].replace("Z", "+00:00"))
                        preferred_times[meal_type] = meal_time.strftime("%H:%M")
                    except ValueError:
                        pass
            
            return preferred_times

        except Exception as e:
            _LOGGER.error("Error analyzing meal timing: %s", e)
            return {}

    async def _analyze_appetite_consistency(self, feeding_data: Dict[str, Any]) -> str:
        """Analyze appetite consistency."""
        try:
            nutrition_summary = feeding_data.get("nutrition_summary", {})
            completion_pct = nutrition_summary.get("completion_percentage", 0)
            
            if completion_pct >= 80:
                return "Sehr gut"
            elif completion_pct >= 60:
                return "Gut"
            elif completion_pct >= 40:
                return "Mittelmäßig"
            else:
                return "Schlecht"

        except Exception as e:
            _LOGGER.error("Error analyzing appetite consistency: %s", e)
            return "Unbekannt"

    async def _categorize_activity_level(self, daily_summary: Dict[str, Any]) -> str:
        """Categorize daily activity level."""
        try:
            walk_duration = daily_summary.get("walk_duration", 0)
            play_duration = daily_summary.get("play_duration", 0)
            total_activity = walk_duration + play_duration
            
            if total_activity >= 90:
                return "Sehr hoch"
            elif total_activity >= 60:
                return "Hoch"
            elif total_activity >= 30:
                return "Normal"
            elif total_activity >= 15:
                return "Niedrig"
            else:
                return "Sehr niedrig"

        except Exception as e:
            _LOGGER.error("Error categorizing activity level: %s", e)
            return "Unbekannt"

    async def _identify_preferred_activities(self, daily_summary: Dict[str, Any]) -> List[str]:
        """Identify preferred activities based on duration."""
        try:
            activities = []
            
            walk_duration = daily_summary.get("walk_duration", 0)
            play_duration = daily_summary.get("play_duration", 0)
            training_duration = daily_summary.get("training_duration", 0)
            
            activity_scores = [
                ("Spaziergang", walk_duration),
                ("Spielen", play_duration),
                ("Training", training_duration)
            ]
            
            # Sort by duration and return top activities
            activity_scores.sort(key=lambda x: x[1], reverse=True)
            
            for activity, duration in activity_scores:
                if duration > 0:
                    activities.append(f"{activity} ({format_duration(int(duration))})")
            
            return activities[:2]  # Return top 2 activities

        except Exception as e:
            _LOGGER.error("Error identifying preferred activities: %s", e)
            return []

    async def _analyze_energy_distribution(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how energy is distributed throughout the day."""
        try:
            daily_summary = activity_data.get("daily_summary", {})
            current_activities = activity_data.get("current_activities", {})
            
            total_activity_time = (
                daily_summary.get("walk_duration", 0) +
                daily_summary.get("play_duration", 0) +
                daily_summary.get("training_duration", 0)
            )
            
            energy_distribution = {
                "total_active_time": total_activity_time,
                "currently_active": (
                    current_activities.get("walk_in_progress", False) or
                    current_activities.get("training_active", False) or
                    current_activities.get("is_outside", False)
                ),
                "energy_level": activity_data.get("energy_level", "Normal"),
                "activity_balance": "good" if 30 <= total_activity_time <= 120 else "needs_adjustment"
            }
            
            return energy_distribution

        except Exception as e:
            _LOGGER.error("Error analyzing energy distribution: %s", e)
            return {}

    async def _assess_mood_stability(self, mood: str, energy_level: str) -> str:
        """Assess mood stability based on current indicators."""
        try:
            # Extract mood indicators
            if "😄" in mood or "😊" in mood:
                mood_score = 5  # Very positive
            elif "🙂" in mood:
                mood_score = 4  # Positive
            elif "😐" in mood:
                mood_score = 3  # Neutral
            elif "😴" in mood:
                mood_score = 2  # Tired
            else:
                mood_score = 1  # Negative
            
            # Energy level factor
            if energy_level in ["Energiegeladen", "Lebhaft"]:
                energy_score = 5
            elif energy_level == "Normal":
                energy_score = 3
            else:
                energy_score = 1
            
            # Combined stability assessment
            combined_score = (mood_score + energy_score) / 2
            
            if combined_score >= 4:
                return "Sehr stabil"
            elif combined_score >= 3:
                return "Stabil"
            elif combined_score >= 2:
                return "Mittelmäßig"
            else:
                return "Instabil"

        except Exception as e:
            _LOGGER.error("Error assessing mood stability: %s", e)
            return "Unbekannt"

    async def _get_size_category(self) -> str:
        """Get dog size category for health assessments."""
        try:
            size_state = self.hass.states.get(f"input_select.{self.dog_name}_size_category")
            return size_state.state if size_state else "Mittel (10-25kg)"
        except Exception:
            return "Mittel (10-25kg)"

    async def _assess_weight_status(self, weight: float, size_category: str) -> str:
        """Assess weight status based on size category."""
        try:
            # Define healthy weight ranges by size category
            weight_ranges = {
                "Toy (bis 4kg)": (1.0, 4.0),
                "Klein (4-10kg)": (4.0, 10.0),
                "Mittel (10-25kg)": (10.0, 25.0),
                "Groß (25-40kg)": (25.0, 40.0),
                "Riesig (über 40kg)": (40.0, 80.0)
            }
            
            min_weight, max_weight = weight_ranges.get(size_category, (10.0, 25.0))
            
            if weight < min_weight * 0.9:
                return "Untergewicht"
            elif weight > max_weight * 1.1:
                return "Übergewicht"
            elif min_weight <= weight <= max_weight:
                return "Normal"
            else:
                return "Grenzwertig"

        except Exception as e:
            _LOGGER.error("Error assessing weight status: %s", e)
            return "Unbekannt"

    async def _assess_temperature_status(self, temperature: float) -> str:
        """Assess temperature status."""
        try:
            if 38.0 <= temperature <= 39.0:
                return "normal"
            elif 37.5 <= temperature < 38.0 or 39.0 < temperature <= 39.5:
                return "grenzwertig"
            else:
                return "auffällig"
        except Exception:
            return "unbekannt"

    async def _assess_heart_rate_status(self, heart_rate: int) -> str:
        """Assess heart rate status."""
        try:
            if 70 <= heart_rate <= 120:
                return "normal"
            elif 60 <= heart_rate < 70 or 120 < heart_rate <= 140:
                return "grenzwertig"
            else:
                return "auffällig"
        except Exception:
            return "unbekannt"

    async def _generate_wellness_recommendations(self, score_components: Dict[str, float]) -> List[str]:
        """Generate wellness recommendations based on score components."""
        try:
            recommendations = []
            
            if score_components["feeding"] < 15:
                recommendations.append("🍽️ Fütterungsroutine verbessern")
            
            if score_components["activity"] < 15:
                recommendations.append("🚶 Mehr Bewegung und Spiel")
            
            if score_components["health"] < 20:
                recommendations.append("🏥 Gesundheitscheck empfohlen")
            
            if score_components["gps_safety"] < 8:
                recommendations.append("📍 GPS-Tracking optimieren")
            
            if not recommendations:
                recommendations.append("✅ Alle Bereiche in gutem Zustand!")
            
            return recommendations

        except Exception as e:
            _LOGGER.error("Error generating wellness recommendations: %s", e)
            return ["Fehler beim Generieren von Empfehlungen"]

    async def _generate_daily_summary(self, data: Dict[str, Any]) -> str:
        """Generate a human-readable daily summary."""
        try:
            summary_parts = []
            
            # Feeding summary
            feeding = data.get("feeding", {}).get("nutrition_summary", {})
            meals_completed = feeding.get("meals_completed", 0)
            summary_parts.append(f"🍽️ {meals_completed} Mahlzeiten")
            
            # Activity summary
            activities = data.get("activities", {}).get("daily_summary", {})
            walk_duration = activities.get("walk_duration", 0)
            if walk_duration > 0:
                summary_parts.append(f"🚶 {format_duration(int(walk_duration))} spaziert")
            
            # Health summary
            health = data.get("health", {}).get("current_status", {})
            if health.get("feeling_well", True):
                summary_parts.append("😊 Fühlt sich wohl")
            else:
                summary_parts.append("😟 Benötigt Aufmerksamkeit")
            
            # GPS summary
            gps = data.get("gps", {})
            if gps.get("tracking_enabled", False):
                battery = gps.get("battery_level", 0)
                if battery > 0:
                    summary_parts.append(f"📍 GPS aktiv ({battery:.0f}%)")
            
            # Wellness score
            wellness = data.get("wellness_score", {})
            wellness_level = wellness.get("wellness_level", "Unbekannt")
            total_score = wellness.get("total_score", 0)
            summary_parts.append(f"💯 {wellness_level} ({total_score:.0f}/100)")
            
            return " | ".join(summary_parts)

        except Exception as e:
            _LOGGER.error("Error generating daily summary: %s", e)
            return "Fehler beim Generieren der Zusammenfassung"

    async def _analyze_gps_patterns(self, gps_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze GPS usage patterns."""
        try:
            patterns = {
                "usage_efficiency": "unknown",
                "tracking_consistency": "unknown",
                "location_patterns": {},
                                          
            }
            
            # Device health analysis
            battery_level = gps_data.get("battery_level", 0)
            signal_strength = gps_data.get("signal_strength", 0)
            
            if signal_strength >= 80 and battery_level >= 50:
                patterns["device_health"] = "excellent"
            elif signal_strength >= 60 and battery_level >= 30:
                patterns["device_health"] = "good"
            elif signal_strength >= 40 and battery_level >= 20:
                patterns["device_health"] = "acceptable"
            else:
                patterns["device_health"] = "needs_attention"
            
            # Usage efficiency
            tracking_enabled = gps_data.get("tracking_enabled", False)
            
            if tracking_enabled:
                patterns["usage_efficiency"] = "optimal"
            else:
                patterns["usage_efficiency"] = "unused"
            
            return patterns

        except Exception as e:
            _LOGGER.error("Error analyzing GPS patterns: %s", e)
            return {"error": str(e)}

    async def _get_last_feeding_update(self) -> Optional[str]:
        """Get timestamp of last feeding-related update."""
        try:
            latest_time = None
            
            for meal_type in FEEDING_TYPES:
                entity_id = f"input_datetime.{self.dog_name}_last_feeding_{meal_type}"
                state = self.hass.states.get(entity_id)
                if state and state.state not in ["unknown", "unavailable"]:
                    try:
                        feeding_time = datetime.fromisoformat(state.state.replace("Z", "+00:00"))
                        if latest_time is None or feeding_time > latest_time:
                            latest_time = feeding_time
                    except ValueError:
                        continue
            
            return latest_time.isoformat() if latest_time else None

        except Exception as e:
            _LOGGER.error("Error getting last feeding update: %s", e)
            return None

    async def _get_last_activity_update(self) -> Optional[str]:
        """Get timestamp of last activity-related update."""
        try:
            latest_time = None
            
            activity_entities = ["last_walk", "last_play", "last_training", "last_outside"]
            
            for activity in activity_entities:
                entity_id = f"input_datetime.{self.dog_name}_{activity}"
                state = self.hass.states.get(entity_id)
                if state and state.state not in ["unknown", "unavailable"]:
                    try:
                        activity_time = datetime.fromisoformat(state.state.replace("Z", "+00:00"))
                        if latest_time is None or activity_time > latest_time:
                            latest_time = activity_time
                    except ValueError:
                        continue
            
            return latest_time.isoformat() if latest_time else None

        except Exception as e:
            _LOGGER.error("Error getting last activity update: %s", e)
            return None

    async def _get_last_gps_update(self) -> Optional[str]:
        """Get timestamp of last GPS-related update."""
        try:
            # Check GPS tracker status for last update info
            tracker_status_state = self.hass.states.get(f"input_text.{self.dog_name}_gps_tracker_status")
            if tracker_status_state and tracker_status_state.state not in ["unknown", "unavailable"]:
                # Try to extract timestamp from status message
                status_text = tracker_status_state.state
                if "um" in status_text:
                    # Extract time from status like "Manuell aktualisiert um 14:30"
                    return f"Heute {status_text.split('um')[-1].strip()}"
            
            # Fallback: return current time if GPS is enabled
            gps_enabled_state = self.hass.states.get(f"input_boolean.{self.dog_name}_gps_tracking_enabled")
            if gps_enabled_state and gps_enabled_state.state == "on":
                return datetime.now().isoformat()
            
            return None

        except Exception as e:
            _LOGGER.error("Error getting last GPS update: %s", e)
            return None


# =========================
# ENTITY CREATION FUNCTIONS (ORIGINAL - VOLLSTÄNDIG BEIBEHALTEN)
# =========================

async def async_create_helpers(hass: HomeAssistant, dog_name: str, config: dict) -> None:
    """Create all helper entities with ULTRA-ROBUST reliability."""
    
    try:
        _LOGGER.info("🚀 Starting ULTRA-ROBUST helper entity creation for %s", dog_name)
        
        # PHASE 1: ULTRA PRE-FLIGHT CHECKS
        if not await _ultra_preflight_checks(hass):
            _LOGGER.error("❌ Ultra pre-flight checks failed, aborting helper creation")
            return
        
        # PHASE 2: SYSTEM STABILIZATION
        _LOGGER.info("⏳ Waiting for system stabilization...")
        await asyncio.sleep(SYSTEM_STABILITY_WAIT)
        
        # PHASE 3: ULTRA-ROBUST ENTITY CREATION
        creation_steps = [
            ("input_boolean", _create_input_booleans),
            ("counter", _create_counters),
            ("input_datetime", _create_input_datetimes),
            ("input_text", _create_input_texts),
            ("input_number", _create_input_numbers),
            ("input_select", _create_input_selects),
        ]
        
        total_steps = len(creation_steps)
        overall_results = {
            "total_created": 0,
            "total_skipped": 0,
            "total_failed": 0,
            "domain_results": {},
            "retry_attempts": 0
        }
        
        # DOMAIN-BY-DOMAIN CREATION WITH RETRY
        for step_num, (domain, creation_func) in enumerate(creation_steps, 1):
            _LOGGER.info("📊 Step %d/%d: Creating %s entities for %s", 
                        step_num, total_steps, domain, dog_name)
            
            try:
                domain_results = await creation_func(hass, dog_name)
                
                # UPDATE OVERALL RESULTS
                overall_results["domain_results"][domain] = domain_results
                overall_results["total_created"] += domain_results["created"]
                overall_results["total_skipped"] += domain_results["skipped"]
                overall_results["total_failed"] += domain_results["failed"]
                
                total_attempted = domain_results["created"] + domain_results["failed"]
                success_rate = (domain_results["created"] / total_attempted) * 100 if total_attempted > 0 else 100.0
                
                _LOGGER.info("✅ %s: %d created, %d skipped, %d failed (%.1f%% success)", 
                           domain, domain_results["created"], 
                           domain_results["skipped"], domain_results["failed"],
                           success_rate)
                
            except Exception as e:
                _LOGGER.error("❌ Critical error creating %s entities: %s", domain, e)
                overall_results["domain_results"][domain] = {
                    "created": 0, "skipped": 0, "failed": 999, "error": str(e)
                }
            
            # INTER-DOMAIN STABILIZATION
            if step_num < total_steps:
                _LOGGER.debug("⏳ Inter-domain stabilization wait...")
                await asyncio.sleep(INTER_BATCH_DELAY)
        
        # PHASE 4: SUCCESS ANALYSIS
        total_success_rate = _calculate_final_success_rate(overall_results)
        
        _LOGGER.info("🎯 ULTRA-ROBUST Helper creation completed for %s", dog_name)
        _LOGGER.info("📊 Final Statistics: %d created, %d skipped, %d failed", 
                    overall_results["total_created"],
                    overall_results["total_skipped"], 
                    overall_results["total_failed"])
        _LOGGER.info("🏆 FINAL SUCCESS RATE: %.2f%%", total_success_rate)
        
        # SEND COMPLETION NOTIFICATION
        await _send_ultra_completion_notification(hass, dog_name, overall_results, total_success_rate)
        
    except Exception as e:
        _LOGGER.error("❌ CRITICAL ERROR in ultra-robust helper creation for %s: %s", dog_name, e)
        await _send_error_notification(hass, dog_name, str(e))
        raise


async def _ultra_preflight_checks(hass: HomeAssistant) -> bool:
    """Ultra-comprehensive pre-flight checks."""
    
    required_domains = [
        "input_boolean", "counter", "input_datetime", 
        "input_text", "input_number", "input_select"
    ]
    
    _LOGGER.info("🔍 Performing ULTRA pre-flight checks...")
    
    # CHECK 1: Domain Service Availability
    missing_domains = []
    for domain in required_domains:
        if not hass.services.has_service(domain, "create"):
            missing_domains.append(domain)
    
    if missing_domains:
        _LOGGER.error("❌ Missing required domains: %s", missing_domains)
        return False
    
    _LOGGER.debug("✅ All required domains available")
    
    # CHECK 2: System Service Responsiveness
    try:
        test_start = datetime.now()
        await asyncio.wait_for(
            hass.services.async_call("system_log", "write", {
                "message": "Paw Control ULTRA pre-flight check",
                "level": "debug"
            }, blocking=True),
            timeout=15.0
        )
        response_time = (datetime.now() - test_start).total_seconds()
        _LOGGER.debug("✅ System responsiveness: %.2fs", response_time)
        
        if response_time > 10.0:
            _LOGGER.warning("⚠️ Slow system response detected: %.2fs", response_time)
            
    except Exception as e:
        _LOGGER.error("❌ System responsiveness test failed: %s", e)
        return False
    
    _LOGGER.info("✅ ULTRA pre-flight checks passed")
    return True


# Entity creation functions - Enhanced versions from Paw Control

async def _create_input_booleans(hass: HomeAssistant, dog_name: str) -> Dict[str, Any]:
    """Create input_boolean entities with ultra-reliability."""
    
    boolean_entities = [
        # Core feeding booleans
        (f"{dog_name}_feeding_morning", "Frühstück", ICONS["morning"]),
        (f"{dog_name}_feeding_lunch", "Mittagessen", ICONS["lunch"]),
        (f"{dog_name}_feeding_evening", "Abendessen", ICONS["evening"]),
        (f"{dog_name}_feeding_snack", "Leckerli", ICONS["snack"]),
        
        # Core activity booleans
        (f"{dog_name}_outside", "War draußen", ICONS["outside"]),
        (f"{dog_name}_was_dog", "War es der Hund?", ICONS["dog"]),
        (f"{dog_name}_poop_done", "Geschäft gemacht", ICONS["poop"]),
        
        # System booleans
        (f"{dog_name}_visitor_mode_input", "Besuchsmodus", ICONS["visitor"]),
        (f"{dog_name}_emergency_mode", "Notfallmodus", ICONS["emergency"]),
        (f"{dog_name}_medication_given", "Medikament gegeben", ICONS["medication"]),
        
        # Health & wellbeing booleans
        (f"{dog_name}_feeling_well", "Fühlt sich wohl", ICONS["health"]),
        (f"{dog_name}_appetite_normal", "Normaler Appetit", ICONS["food"]),
        (f"{dog_name}_energy_normal", "Normale Energie", ICONS["play"]),
        
        # *** IMPFUNGS-BOOLEANS ***
        (f"{dog_name}_vaccination_due", "Impfung fällig", "mdi:needle"),
        (f"{dog_name}_vaccination_overdue", "Impfung überfällig", "mdi:needle"),
        (f"{dog_name}_rabies_current", "Tollwut-Impfung aktuell", "mdi:needle"),
        (f"{dog_name}_core_vaccines_current", "Grundimmunisierung aktuell", "mdi:needle"),
        (f"{dog_name}_vaccination_reminder_sent", "Impferinnerung gesendet", "mdi:needle"),
        
        # Feature toggles
        (f"{dog_name}_auto_reminders", "Automatische Erinnerungen", ICONS["bell"]),
        (f"{dog_name}_tracking_enabled", "Tracking aktiviert", ICONS["status"]),
        (f"{dog_name}_weather_alerts", "Wetter-Warnungen", "mdi:weather-partly-cloudy"),
        
        # GPS tracking booleans
        (f"{dog_name}_walk_in_progress", "Spaziergang aktiv", "mdi:walk"),
        (f"{dog_name}_auto_walk_detection", "Auto-Spaziergang Erkennung", "mdi:radar"),
        (f"{dog_name}_gps_tracking_enabled", "GPS-Tracking aktiviert", "mdi:crosshairs-gps"),
        
        # Additional useful booleans
        (f"{dog_name}_walked_today", "Heute Gassi gewesen", ICONS["walk"]),
        (f"{dog_name}_played_today", "Heute gespielt", ICONS["play"]),
        (f"{dog_name}_socialized_today", "Heute sozialisiert", "mdi:account-group"),
    ]
    
    return await _create_helpers_for_domain_ultra_robust(hass, "input_boolean", boolean_entities, dog_name)

async def _create_counters(hass: HomeAssistant, dog_name: str) -> Dict[str, Any]:
    """Create counter entities with comprehensive tracking."""
    
    counter_entities = [
        # Feeding counters
        (f"{dog_name}_feeding_morning_count", "Frühstück Anzahl", ICONS["morning"]),
        (f"{dog_name}_feeding_lunch_count", "Mittagessen Anzahl", ICONS["lunch"]),
        (f"{dog_name}_feeding_evening_count", "Abendessen Anzahl", ICONS["evening"]),
        (f"{dog_name}_feeding_snack_count", "Leckerli Anzahl", ICONS["snack"]),
        
        # Activity counters
        (f"{dog_name}_outside_count", "Draußen Anzahl", ICONS["outside"]),
        (f"{dog_name}_walk_count", "Spaziergang Anzahl", ICONS["walk"]),
        (f"{dog_name}_play_count", "Spielzeit Anzahl", ICONS["play"]),
        (f"{dog_name}_training_count", "Training Anzahl", ICONS["training"]),
        (f"{dog_name}_poop_count", "Geschäft Anzahl", ICONS["poop"]),
        
        # Health counters
        (f"{dog_name}_vet_visits_count", "Tierarztbesuche", ICONS["vet"]),
        (f"{dog_name}_medication_count", "Medikamente Anzahl", ICONS["medication"]),
        (f"{dog_name}_grooming_count", "Pflege Anzahl", ICONS["grooming"]),
        
        # *** IMPFUNGS-ZÄHLER ***
        (f"{dog_name}_total_vaccinations_count", "Impfungen gesamt", "mdi:needle"),
        (f"{dog_name}_rabies_vaccinations_count", "Tollwut-Impfungen", "mdi:needle"), 
        (f"{dog_name}_distemper_vaccinations_count", "Staupe-Impfungen", "mdi:needle"),
        (f"{dog_name}_hepatitis_vaccinations_count", "Hepatitis-Impfungen", "mdi:needle"),
         
        # Summary counters
        (f"{dog_name}_activity_count", "Aktivitäten gesamt", ICONS["status"]),
        (f"{dog_name}_emergency_calls", "Notfälle", ICONS["emergency"]),
        (f"{dog_name}_daily_score", "Tages-Score", "mdi:star"),
        
        # Social & behavioral counters
        (f"{dog_name}_social_interactions", "Soziale Kontakte", "mdi:account-group"),
        (f"{dog_name}_behavior_incidents", "Verhaltensereignisse", "mdi:alert-outline"),
        (f"{dog_name}_rewards_given", "Belohnungen", "mdi:gift"),
    ]
    
    return await _create_helpers_for_domain_ultra_robust(hass, "counter", counter_entities, dog_name)
    # =========================
    # RECOVERY INTEGRATION: HELPER METHODS
    # =========================

    async def _calculate_next_feeding(self) -> Optional[str]:
        """Calculate next feeding time."""
        try:
            current_time = datetime.now()
            current_hour = current_time.hour
            
            # Check feeding schedule
            feeding_times = {
                "morning": 7,
                "lunch": 12,
                "evening": 18
            }
            
            for meal_type, hour in feeding_times.items():
                if current_hour < hour:
                    # Check if meal is not already completed
                    meal_state = self.hass.states.get(f"input_boolean.{self.dog_name}_feeding_{meal_type}")
                    if not meal_state or meal_state.state != "on":
                        return f"{hour:02d}:00 - {MEAL_TYPES[meal_type]}"
            
            # If all meals for today are scheduled, return tomorrow's breakfast
            return "07:00 - Frühstück (morgen)"

        except Exception as e:
            _LOGGER.error("Error calculating next feeding: %s", e)
            return None

    async def _count_active_entities(self) -> int:
        """Count entities that have non-default states."""
        try:
            active_count = 0
            
            # Check input_boolean entities
            boolean_entities = [
                "feeding_morning", "feeding_lunch", "feeding_evening", "feeding_snack",
                "outside", "walked_today", "played_today", "poop_done",
                "gps_tracking_enabled", "visitor_mode_input", "emergency_mode"
            ]
            
            for entity_suffix in boolean_entities:
                entity_id = f"input_boolean.{self.dog_name}_{entity_suffix}"
                state = self.hass.states.get(entity_id)
                if state and state.state == "on":
                    active_count += 1
            
            return active_count

        except Exception as e:
            _LOGGER.error("Error counting active entities: %s", e)
            return 0

    async def _count_entities_with_data(self) -> int:
        """Count entities that have any data (not unknown/unavailable)."""
        try:
            entities_with_data = 0
            
            # Sample of key entities to check
            key_entities = [
                f"input_number.{self.dog_name}_weight",
                f"input_number.{self.dog_name}_daily_food_amount", 
                f"input_select.{self.dog_name}_health_status",
                f"input_select.{self.dog_name}_mood",
                f"input_text.{self.dog_name}_breed",
                f"counter.{self.dog_name}_walk_count"
            ]
            
            for entity_id in key_entities:
                state = self.hass.states.get(entity_id)
                if state and state.state not in ["unknown", "unavailable", ""]:
                    entities_with_data += 1
            
            return entities_with_data

        except Exception as e:
            _LOGGER.error("Error counting entities with data: %s", e)
            return 0

    # =========================
    # RECOVERY INTEGRATION: STORAGE METHODS
    # =========================

    async def _store_data_persistent(self, data: Dict[str, Any]) -> None:
        """Store data persistently for historical analysis."""
        try:
            # Create a simplified version for storage
            storage_data = {
                "timestamp": datetime.now().isoformat(),
                "dog_name": self.dog_name,
                "feeding_summary": data.get("feeding", {}).get("nutrition_summary", {}),
                "walking_summary": {
                    "daily_duration": data.get("walking", {}).get("daily_duration", 0),
                    "daily_distance": data.get("walking", {}).get("daily_distance", 0),
                    "walks_today": data.get("walking", {}).get("walks_today", 0)
                },
                "health_summary": {
                    "weight": data.get("health", {}).get("weight", 0),
                    "health_score": data.get("health", {}).get("health_score", 0),
                    "health_status": data.get("health", {}).get("health_status", "unknown")
                },
                "wellness_score": data.get("wellness_score", {}),
                "status": data.get("system_status", {}).get("overall_status", "unknown")
            }
            
            await self._store.async_save(storage_data)
            _LOGGER.debug("Data stored persistently for %s", self.dog_name)

        except Exception as e:
            _LOGGER.error("Error storing persistent data for %s: %s", self.dog_name, e)

    async def _update_statistics(self, update_duration: float, success: bool) -> None:
        """Update coordinator statistics."""
        try:
            self._statistics["total_data_updates"] += 1
            if success:
                self._statistics["successful_updates"] += 1
                self._statistics["last_update_duration"] = update_duration
                self._statistics["last_successful_update"] = datetime.now().isoformat()
                
                # Calculate running average
                total_time = self._statistics["average_update_time"] * (self._statistics["successful_updates"] - 1)
                self._statistics["average_update_time"] = (total_time + update_duration) / self._statistics["successful_updates"]
            else:
                self._statistics["failed_updates"] += 1

        except Exception as e:
            _LOGGER.error("Error updating statistics: %s", e)

    # =========================
    # RECOVERY INTEGRATION: PUBLIC METHODS FOR EXTERNAL ACCESS
    # =========================

    async def get_current_data(self) -> Dict[str, Any]:
        """Get current cached data without triggering update."""
        return self._cached_data.copy() if self._cached_data else {}

    async def force_refresh(self) -> None:
        """Force immediate data refresh."""
        try:
            await self.async_request_refresh()
            _LOGGER.info("Forced data refresh completed for %s", self.dog_name)
        except Exception as e:
            _LOGGER.error("Error during forced refresh for %s: %s", self.dog_name, e)
            raise

    async def get_health_summary(self) -> Dict[str, Any]:
        """Get condensed health summary."""
        if not hasattr(self, '_cached_data') or not self._cached_data:
            await self.force_refresh()
        
        health_data = self._cached_data.get("health", {})
        return {
            "status": health_data.get("current_status", {}).get("overall", "unknown"),
            "vital_signs": health_data.get("vital_signs", {}),
            "alerts": health_data.get("alerts", []),
            "medication_due": not health_data.get("medication", {}).get("given_today", False),
            "emergency_mode": health_data.get("emergency_mode", False)
        }

    async def get_activity_summary(self) -> Dict[str, Any]:
        """Get condensed activity summary."""
        if not hasattr(self, '_cached_data') or not self._cached_data:
            await self.force_refresh()
        
        activity_data = self._cached_data.get("activities", {})
        return {
            "daily_summary": activity_data.get("daily_summary", {}),
            "current_activities": activity_data.get("current_activities", {}),
            "goals_progress": activity_data.get("goals_progress", {}),
            "recommendations": activity_data.get("recommendations", [])
        }

    async def get_gps_summary(self) -> Dict[str, Any]:
        """Get condensed GPS summary."""
        if not hasattr(self, '_cached_data') or not self._cached_data:
            await self.force_refresh()
        
        gps_data = self._cached_data.get("gps", {})
        return {
            "tracking_enabled": gps_data.get("tracking_enabled", False),
            "current_location": gps_data.get("current_location", {}),
            "device_status": {
                "battery_level": gps_data.get("battery_level", 0),
                "signal_strength": gps_data.get("signal_strength", 0)
            },
            "home_location": gps_data.get("home_location", {})
        }

    async def get_feeding_summary(self) -> Dict[str, Any]:
        """Get condensed feeding summary."""
        if not hasattr(self, '_cached_data') or not self._cached_data:
            await self.force_refresh()
        
        feeding_data = self._cached_data.get("feeding", {})
        return {
            "meals_today": feeding_data.get("meals_today", {}),
            "nutrition_summary": feeding_data.get("nutrition_summary", {}),
            "next_feeding": feeding_data.get("next_feeding"),
            "daily_total": feeding_data.get("daily_total", 0)
        }

    async def get_wellness_score(self) -> Dict[str, Any]:
        """Get current wellness score."""
        if not hasattr(self, '_cached_data') or not self._cached_data:
            await self.force_refresh()
        
        return self._cached_data.get("wellness_score", {
            "total_score": 0,
            "wellness_level": "Unbekannt",
            "error": "Keine Daten verfügbar"
        })

    # =========================
    # ORIGINAL SERVICE METHODS (ALLE BEIBEHALTEN)
    # =========================

    # Service methods with enhanced functionality
    async def async_feed_dog(self, call_data: dict) -> None:
        """Handle feed dog service call with data tracking."""
        try:
            food_type = call_data.get("food_type", "Trockenfutter")
            amount = call_data.get("food_amount", 100)
            notes = call_data.get("notes", "")
            
            # Store feeding event
            await self._store_feeding_event(food_type, amount, notes)
            
            # Update feeding streak
            await self._update_feeding_streak()
            
            _LOGGER.info("Feed dog service completed for %s: %s (%dg)", self.dog_name, food_type, amount)
            
        except Exception as e:
            _LOGGER.error("Error in feed dog service for %s: %s", self.dog_name, e)

    async def async_start_walk(self, call_data: dict) -> None:
        """Handle start walk service call with GPS tracking."""
        try:
            walk_type = call_data.get("walk_type", "Normal")
            location = call_data.get("location", "")
            notes = call_data.get("notes", "")
            
            # Start walk tracking
            walk_data = {
                "start_time": datetime.now(),
                "walk_type": walk_type,
                "location": location,
                "notes": notes,
                "route_points": []
            }
            
            await self._store_walk_start(walk_data)
            
            _LOGGER.info("Start walk service completed for %s: %s", self.dog_name, walk_type)
            
        except Exception as e:
            _LOGGER.error("Error in start walk service for %s: %s", self.dog_name, e)

    async def async_end_walk(self, call_data: dict) -> None:
        """Handle end walk service call with statistics."""
        try:
            rating = call_data.get("rating", 5)
            notes = call_data.get("notes", "")
            duration = call_data.get("duration")
            
            # End walk tracking and calculate stats
            walk_stats = await self._calculate_walk_stats(duration, rating, notes)
            await self._store_walk_end(walk_stats)
            
            # Update walk streak
            await self._update_walk_streak()
            
            _LOGGER.info("End walk service completed for %s: duration=%s, rating=%d", 
                        self.dog_name, duration, rating)
            
        except Exception as e:
            _LOGGER.error("Error in end walk service for %s: %s", self.dog_name, e)

    async def async_log_health_data(self, call_data: dict) -> None:
        """Handle log health data service call with trend analysis."""
        try:
            weight = call_data.get("weight")
            temperature = call_data.get("temperature")
            energy_level = call_data.get("energy_level")
            symptoms = call_data.get("symptoms", "")
            notes = call_data.get("notes", "")
            
            # Store health data with timestamp
            health_entry = {
                "timestamp": datetime.now(),
                "weight": weight,
                "temperature": temperature,
                "energy_level": energy_level,
                "symptoms": symptoms,
                "notes": notes
            }
            
            await self._store_health_data(health_entry)
            
            # Analyze trends and update health score
            await self._update_health_score()
            
            _LOGGER.info("Health data logged for %s", self.dog_name)
            
        except Exception as e:
            _LOGGER.error("Error logging health data for %s: %s", self.dog_name, e)

    async def async_update_gps_simple(self, call_data: dict) -> None:
        """Handle simple GPS update."""
        try:
            latitude = call_data.get("latitude")
            longitude = call_data.get("longitude")
            accuracy = call_data.get("accuracy", 0)
            source_info = call_data.get("source_info", "manual")
            
            # Store GPS location
            gps_entry = {
                "timestamp": datetime.now(),
                "latitude": latitude,
                "longitude": longitude,
                "accuracy": accuracy,
                "source": source_info
            }
            
            await self._store_gps_location(gps_entry)
            
            # Check if dog is within geofence
            await self._check_geofence(latitude, longitude)
            
            _LOGGER.info("GPS updated for %s: %.6f, %.6f", self.dog_name, latitude, longitude)
            
        except Exception as e:
            _LOGGER.error("Error updating GPS for %s: %s", self.dog_name, e)

    # =========================
    # ORIGINAL STORAGE HELPER METHODS (ALLE BEIBEHALTEN)
    # =========================

    async def _store_feeding_event(self, food_type: str, amount: int, notes: str) -> None:
        """Store feeding event in persistent storage."""
        try:
            if not self._store:
                return
            
            data = await self._store.async_load() or {}
            
            if "feeding_events" not in data:
                data["feeding_events"] = []
            
            event = {
                "timestamp": datetime.now().isoformat(),
                "food_type": food_type,
                "amount": amount,
                "notes": notes
            }
            
            data["feeding_events"].append(event)
            
            # Keep only last 100 events
            if len(data["feeding_events"]) > 100:
                data["feeding_events"] = data["feeding_events"][-100:]
            
            await self._store.async_save(data)
            
        except Exception as e:
            _LOGGER.error("Error storing feeding event: %s", e)

    async def _store_walk_start(self, walk_data: dict) -> None:
        """Store walk start data."""
        try:
            if not self._store:
                return
            
            data = await self._store.async_load() or {}
            data["current_walk"] = {
                "start_time": walk_data["start_time"].isoformat(),
                "walk_type": walk_data["walk_type"],
                "location": walk_data["location"],
                "notes": walk_data["notes"],
                "route_points": []
            }
            
            await self._store.async_save(data)
            
        except Exception as e:
            _LOGGER.error("Error storing walk start: %s", e)

    async def _calculate_walk_stats(self, duration: Optional[int], rating: int, notes: str) -> Dict[str, Any]:
        """Calculate walk statistics and return them."""
        try:
            stats = {
                "end_time": datetime.now(),
                "duration": duration or 0,
                "rating": rating,
                "notes": notes,
                "distance": 0,
                "average_speed": 0,
                "calories_burned": 0
            }
            
            # Get current walk distance if available
            distance_entity = f"input_number.{self.dog_name}_current_walk_distance"
            state = self.hass.states.get(distance_entity)
            if state and state.state not in ["unknown", "unavailable"]:
                stats["distance"] = float(state.state)
            
            # Calculate average speed (km/h)
            if stats["duration"] > 0 and stats["distance"] > 0:
                stats["average_speed"] = (stats["distance"] / (stats["duration"] / 60))
            
            # Estimate calories burned (rough calculation)
            if stats["distance"] > 0:
                # Approximate: 0.5 calories per kg of body weight per km
                weight_entity = f"input_number.{self.dog_name}_weight"
                weight_state = self.hass.states.get(weight_entity)
                if weight_state and weight_state.state not in ["unknown", "unavailable"]:
                    weight = float(weight_state.state)
                    stats["calories_burned"] = int(stats["distance"] * weight * 0.5)
            
            return stats
            
        except Exception as e:
            _LOGGER.error("Error calculating walk stats: %s", e)
            return {"end_time": datetime.now(), "duration": 0, "rating": rating}

    async def _store_walk_end(self, walk_stats: Dict[str, Any]) -> None:
        """Store walk end data and statistics."""
        try:
            if not self._store:
                return
            
            data = await self._store.async_load() or {}
            
            # Get current walk data
            current_walk = data.get("current_walk", {})
            
            # Complete walk record
            completed_walk = {
                **current_walk,
                "end_time": walk_stats["end_time"].isoformat(),
                "duration": walk_stats["duration"],
                "distance": walk_stats["distance"],
                "rating": walk_stats["rating"],
                "average_speed": walk_stats["average_speed"],
                "calories_burned": walk_stats["calories_burned"],
                "notes": walk_stats["notes"]
            }
            
            # Add to walk history
            if "walk_history" not in data:
                data["walk_history"] = []
            
            data["walk_history"].append(completed_walk)
            
            # Keep only last 50 walks
            if len(data["walk_history"]) > 50:
                data["walk_history"] = data["walk_history"][-50:]
            
            # Clear current walk
            data["current_walk"] = None
            
            await self._store.async_save(data)
            
        except Exception as e:
            _LOGGER.error("Error storing walk end: %s", e)

    async def _store_health_data(self, health_entry: Dict[str, Any]) -> None:
        """Store health data entry."""
        try:
            if not self._store:
                return
            
            data = await self._store.async_load() or {}
            
            if "health_history" not in data:
                data["health_history"] = []
            
            # Convert datetime to string for JSON serialization
            entry = {
                "timestamp": health_entry["timestamp"].isoformat(),
                "weight": health_entry["weight"],
                "temperature": health_entry["temperature"],
                "energy_level": health_entry["energy_level"],
                "symptoms": health_entry["symptoms"],
                "notes": health_entry["notes"]
            }
            
            data["health_history"].append(entry)
            
            # Keep only last 100 entries
            if len(data["health_history"]) > 100:
                data["health_history"] = data["health_history"][-100:]
            
            await self._store.async_save(data)
            
        except Exception as e:
            _LOGGER.error("Error storing health data: %s", e)

    async def _store_gps_location(self, gps_entry: Dict[str, Any]) -> None:
        """Store GPS location entry."""
        try:
            if not self._store:
                return
            
            data = await self._store.async_load() or {}
            
            if "gps_history" not in data:
                data["gps_history"] = []
            
            entry = {
                "timestamp": gps_entry["timestamp"].isoformat(),
                "latitude": gps_entry["latitude"],
                "longitude": gps_entry["longitude"],
                "accuracy": gps_entry["accuracy"],
                "source": gps_entry["source"]
            }
            
            data["gps_history"].append(entry)
            
            # Keep only last 500 GPS points
            if len(data["gps_history"]) > 500:
                data["gps_history"] = data["gps_history"][-500:]
            
            await self._store.async_save(data)
            
        except Exception as e:
            _LOGGER.error("Error storing GPS location: %s", e)

    async def _update_feeding_streak(self) -> None:
        """Update feeding streak based on recent activity."""
        try:
            # Implementation to calculate feeding streaks
            # This would check if feeding occurred daily
            pass
        except Exception as e:
            _LOGGER.error("Error updating feeding streak: %s", e)

    async def _update_walk_streak(self) -> None:
        """Update walk streak based on recent activity."""
        try:
            # Implementation to calculate walk streaks
            # This would check if walks occurred daily
            pass
        except Exception as e:
            _LOGGER.error("Error updating walk streak: %s", e)

    async def _update_health_score(self) -> None:
        """Update health score based on recent data."""
        try:
            # Implementation to calculate health score
            # Based on weight trends, temperature, symptoms, etc.
            pass
        except Exception as e:
            _LOGGER.error("Error updating health score: %s", e)

    async def _check_geofence(self, latitude: float, longitude: float) -> None:
        """Check if dog is within defined geofence."""
        try:
            # Get home coordinates
            home_lat_entity = f"input_number.{self.dog_name}_home_latitude"
            home_lon_entity = f"input_number.{self.dog_name}_home_longitude"
            
            home_lat_state = self.hass.states.get(home_lat_entity)
            home_lon_state = self.hass.states.get(home_lon_entity)
            
            if (home_lat_state and home_lat_state.state not in ["unknown", "unavailable"] and
                home_lon_state and home_lon_state.state not in ["unknown", "unavailable"]):
                
                home_lat = float(home_lat_state.state)
                home_lon = float(home_lon_state.state)
                
                # Calculate distance from home
                distance = calculate_distance((latitude, longitude), (home_lat, home_lon))
                
                # Check if outside geofence (default 0.1 km = 100m)
                geofence_radius = 100.0  # meters
                
                if distance > geofence_radius:
                    # Dog is outside geofence - could trigger alert
                    _LOGGER.info("Dog %s is outside geofence: %.3f m from home", 
                               self.dog_name, distance)
                
        except Exception as e:
            _LOGGER.error("Error checking geofence: %s", e)
