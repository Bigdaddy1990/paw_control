from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfMass, UnitOfTime, PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.event import Event

from .const import (
    DOMAIN,
    ICON_DOG,
    ICON_FOOD,
    ICON_WALK,
    ICON_HEALTH,
    ICON_MOOD_HAPPY,
    ICON_WEIGHT,
    ICON_PLAY,
    ICON_TRAINING,
    ICON_BELL,
    ICON_STATUS,
    ATTR_DOG_NAME,
    ATTR_DOG_BREED,
    ATTR_DOG_AGE,
    ATTR_DOG_WEIGHT,
    ATTR_LAST_UPDATED,
    ATTR_FOOD_TYPE,
    ATTR_FOOD_AMOUNT,
    ATTR_WALK_DURATION,
    ATTR_HEALTH_STATUS,
    ATTR_ACTIVITY_LEVEL,
    ATTR_MOOD,
    ATTR_STREAK_COUNT,
)
from .helpers import PawControlDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Status messages for different states
STATUS_MESSAGES = {
    "excellent": "🌟 Ausgezeichnet",
    "very_good": "😊 Sehr gut", 
    "good": "👍 Gut",
    "needs_attention": "⚠️ Braucht Aufmerksamkeit",
    "concern": "😟 Bedenklich",
    "emergency": "🚨 Notfall",
    "unknown": "❓ Unbekannt",
}

ACTIVITY_STATUS = {
    "all_done": "✅ Alles erledigt",
    "partially_done": "📝 Teilweise erledigt", 
    "needs_feeding": "🍽️ Fütterung ausstehend",
    "needs_walk": "🚶 Spaziergang ausstehend",
    "needs_both": "⏰ Fütterung & Spaziergang ausstehend",
    "visitor_mode": "👥 Besuchsmodus aktiv",
    "emergency": "🚨 Notfallmodus aktiv",
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    dog_name = coordinator.dog_name
    
    entities = [
        # Core status sensors
        PawControlStatusSensor(coordinator, dog_name),
        PawControlActivityStatusSensor(coordinator, dog_name),
        PawControlDailySummarySensor(coordinator, dog_name),
        
        # Feeding sensors
        PawControlLastFedSensor(coordinator, dog_name),
        PawControlNextFeedingSensor(coordinator, dog_name),
        PawControlFeedingStreakSensor(coordinator, dog_name),
        PawControlDailyFoodAmountSensor(coordinator, dog_name),
        
        # Walking sensors
        PawControlLastWalkSensor(coordinator, dog_name),
        PawControlNextWalkSensor(coordinator, dog_name),
        PawControlWalkStreakSensor(coordinator, dog_name),
        PawControlDailyWalkDurationSensor(coordinator, dog_name),
        
        # Health sensors
        PawControlHealthStatusSensor(coordinator, dog_name),
        PawControlWeightTrackingSensor(coordinator, dog_name),
        PawControlHealthScoreSensor(coordinator, dog_name),
        PawControlTemperatureSensor(coordinator, dog_name),
        
        # Activity sensors
        PawControlActivityLevelSensor(coordinator, dog_name),
        PawControlMoodSensor(coordinator, dog_name),
        PawControlTrainingSessionsSensor(coordinator, dog_name),
        PawControlPlaytimeTodaySensor(coordinator, dog_name),
        PawControlSleepHoursSensor(coordinator, dog_name),
        
        # Statistics sensors
        PawControlWeeklySummarySensor(coordinator, dog_name),
        PawControlLastActivitySensor(coordinator, dog_name),
        PawControlWaterConsumptionSensor(coordinator, dog_name),
        
        # GPS sensors
        PawControlGPSStatusSensor(coordinator, dog_name),
        PawControlCurrentLocationSensor(coordinator, dog_name),
        PawControlWalkDistanceTodaySensor(coordinator, dog_name),
        PawControlCurrentWalkSensor(coordinator, dog_name),
    ]
    
    async_add_entities(entities)


class PawControlSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Paw Control sensors."""

    def __init__(
        self,
        coordinator: PawControlDataUpdateCoordinator,
        dog_name: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._dog_name = dog_name
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{DOMAIN}_{dog_name.lower()}_{sensor_type}"
        self._attr_name = f"{dog_name} {sensor_type.replace('_', ' ').title()}"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._dog_name.lower())},
            "name": f"Paw Control - {self._dog_name}",
            "manufacturer": "Paw Control",
            "model": "Dog Management System",
            "sw_version": "1.3.0",
        }

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            ATTR_DOG_NAME: self._dog_name,
            ATTR_LAST_UPDATED: datetime.now().isoformat(),
        }


class PawControlStatusSensor(PawControlSensorBase):
    """Sensor for overall dog status."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "health_status")
        self._attr_icon = ICON_HEALTH

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        try:
            # Get health status from input_select
            entity_id = f"input_select.{self._dog_name}_health_status"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                return state.state
            
            return "Gut"  # Default status
            
        except Exception as e:
            _LOGGER.error("Error updating health status sensor for %s: %s", self._dog_name, e)
            return "Unbekannt"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = super().extra_state_attributes
        
        try:
            # Add health-related information
            attrs.update({
                "temperature": self._get_number_value(f"input_number.{self._dog_name}_temperature"),
                "weight": self._get_number_value(f"input_number.{self._dog_name}_weight"),
                "health_score": self._get_number_value(f"input_number.{self._dog_name}_health_score"),
                "last_vet_visit": self._get_datetime_value(f"input_datetime.{self._dog_name}_last_vet_visit"),
                "next_vet_visit": self._get_datetime_value(f"input_datetime.{self._dog_name}_next_vet_appointment"),
                "feeling_well": self._get_boolean_state(f"input_boolean.{self._dog_name}_feeling_well"),
                "appetite_normal": self._get_boolean_state(f"input_boolean.{self._dog_name}_appetite_normal"),
            })
            
        except Exception as e:
            _LOGGER.error("Error getting health status attributes for %s: %s", self._dog_name, e)
            
        return attrs

    def _get_number_value(self, entity_id: str) -> float:
        """Get number value."""
        state = self.hass.states.get(entity_id)
        try:
            return float(state.state) if state and state.state not in ["unknown", "unavailable"] else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _get_datetime_value(self, entity_id: str) -> str | None:
        """Get datetime value."""
        state = self.hass.states.get(entity_id)
        if state and state.state not in ["unknown", "unavailable"]:
            return state.state
        return None

    def _get_boolean_state(self, entity_id: str) -> bool:
        """Get boolean state."""
        state = self.hass.states.get(entity_id)
        return state.state == "on" if state else False


class PawControlWeightTrackingSensor(PawControlSensorBase):
    """Sensor for weight tracking."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "weight")
        self._attr_icon = ICON_WEIGHT
        self._attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
        self._attr_device_class = SensorDeviceClass.WEIGHT
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        try:
            entity_id = f"input_number.{self._dog_name}_weight"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                return float(state.state)
            
            return None
            
        except (ValueError, TypeError) as e:
            _LOGGER.error("Error updating weight sensor for %s: %s", self._dog_name, e)
            return None


class PawControlHealthScoreSensor(PawControlSensorBase):
    """Sensor for health score."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "health_score")
        self._attr_icon = ICON_HEALTH
        self._attr_native_unit_of_measurement = "points"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        try:
            entity_id = f"input_number.{self._dog_name}_health_score"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                return int(float(state.state))
            
            return 85  # Default good health score
            
        except (ValueError, TypeError) as e:
            _LOGGER.error("Error updating health score sensor for %s: %s", self._dog_name, e)
            return None


class PawControlTemperatureSensor(PawControlSensorBase):
    """Sensor for body temperature."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "temperature")
        self._attr_icon = "mdi:thermometer"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        try:
            entity_id = f"input_number.{self._dog_name}_temperature"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                return float(state.state)
            
            return None
            
        except (ValueError, TypeError) as e:
            _LOGGER.error("Error updating temperature sensor for %s: %s", self._dog_name, e)
            return None


class PawControlActivityLevelSensor(PawControlSensorBase):
    """Sensor for activity level."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "activity_level")
        self._attr_icon = ICON_PLAY

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        try:
            entity_id = f"input_select.{self._dog_name}_activity_level"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                return state.state
            
            return "Normal"
            
        except Exception as e:
            _LOGGER.error("Error updating activity level sensor for %s: %s", self._dog_name, e)
            return "Unbekannt"


class PawControlMoodSensor(PawControlSensorBase):
    """Sensor for mood."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "mood")
        self._attr_icon = ICON_MOOD_HAPPY

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        try:
            entity_id = f"input_select.{self._dog_name}_mood"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                return state.state
            
            return "😊 Fröhlich"
            
        except Exception as e:
            _LOGGER.error("Error updating mood sensor for %s: %s", self._dog_name, e)
            return "😐 Neutral"


class PawControlFeedingStreakSensor(PawControlSensorBase):
    """Sensor for feeding streak."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "feeding_streak")
        self._attr_icon = ICON_FOOD
        self._attr_native_unit_of_measurement = "days"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        try:
            entity_id = f"input_number.{self._dog_name}_feeding_streak"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                return int(float(state.state))
            
            # Calculate streak based on daily feeding pattern
            # This is a simplified calculation
            return 1
            
        except (ValueError, TypeError) as e:
            _LOGGER.error("Error updating feeding streak sensor for %s: %s", self._dog_name, e)
            return None


class PawControlWalkStreakSensor(PawControlSensorBase):
    """Sensor for walking streak."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "walk_streak")
        self._attr_icon = ICON_WALK
        self._attr_native_unit_of_measurement = "days"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        try:
            entity_id = f"input_number.{self._dog_name}_walk_streak"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                return int(float(state.state))
            
            return 1
            
        except (ValueError, TypeError) as e:
            _LOGGER.error("Error updating walk streak sensor for %s: %s", self._dog_name, e)
            return None


class PawControlDailyFoodAmountSensor(PawControlSensorBase):
    """Sensor for daily food amount."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "daily_food_amount")
        self._attr_icon = ICON_FOOD
        self._attr_native_unit_of_measurement = "g"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        try:
            entity_id = f"input_number.{self._dog_name}_daily_food_amount"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                return int(float(state.state))
            
            return 0
            
        except (ValueError, TypeError) as e:
            _LOGGER.error("Error updating daily food amount sensor for %s: %s", self._dog_name, e)
            return None


class PawControlDailyWalkDurationSensor(PawControlSensorBase):
    """Sensor for daily walk duration."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "daily_walk_duration")
        self._attr_icon = ICON_WALK
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        try:
            entity_id = f"input_number.{self._dog_name}_daily_walk_duration"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                return int(float(state.state))
            
            return 0
            
        except (ValueError, TypeError) as e:
            _LOGGER.error("Error updating daily walk duration sensor for %s: %s", self._dog_name, e)
            return None


class PawControlWaterConsumptionSensor(PawControlSensorBase):
    """Sensor for water consumption."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "water_consumption")
        self._attr_icon = "mdi:water"
        self._attr_native_unit_of_measurement = "ml"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        try:
            entity_id = f"input_number.{self._dog_name}_daily_water_amount"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                return int(float(state.state))
            
            return 0
            
        except (ValueError, TypeError) as e:
            _LOGGER.error("Error updating water consumption sensor for %s: %s", self._dog_name, e)
            return None


class PawControlSleepHoursSensor(PawControlSensorBase):
    """Sensor for sleep hours."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "sleep_hours")
        self._attr_icon = "mdi:sleep"
        self._attr_native_unit_of_measurement = "h"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        # Placeholder for sleep tracking - would need actual sleep monitoring
        return 8.0


class PawControlTrainingSessionsSensor(PawControlSensorBase):
    """Sensor for training sessions."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "training_sessions")
        self._attr_icon = ICON_TRAINING
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        try:
            entity_id = f"counter.{self._dog_name}_training_count"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                return int(state.state)
            
            return 0
            
        except (ValueError, TypeError) as e:
            _LOGGER.error("Error updating training sessions sensor for %s: %s", self._dog_name, e)
            return None


class PawControlPlaytimeTodaySensor(PawControlSensorBase):
    """Sensor for playtime today."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "playtime_today")
        self._attr_icon = ICON_PLAY
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        try:
            entity_id = f"input_number.{self._dog_name}_daily_play_duration"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                return float(state.state)
            
            return 0.0
            
        except (ValueError, TypeError) as e:
            _LOGGER.error("Error updating playtime today sensor for %s: %s", self._dog_name, e)
            return None


class PawControlWeeklySummarySensor(PawControlSensorBase):
    """Sensor for weekly summary."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "weekly_summary")
        self._attr_icon = "mdi:calendar-week"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        try:
            # Get weekly activity counter
            entity_id = f"counter.{self._dog_name}_weekly_activities"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                activities = int(state.state)
                return f"📅 {activities} Aktivitäten diese Woche"
            
            return "📅 Wöchentliche Daten sammeln..."
            
        except (ValueError, TypeError) as e:
            _LOGGER.error("Error updating weekly summary sensor for %s: %s", self._dog_name, e)
            return "📅 Daten nicht verfügbar"


class PawControlLastActivitySensor(PawControlSensorBase):
    """Sensor for last activity."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "last_activity")
        self._attr_icon = ICON_STATUS
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        """Return the state of the sensor."""
        try:
            # Check various activity timestamps and return the most recent
            activity_times = []
            
            activity_entities = [
                f"input_datetime.{self._dog_name}_last_outside",
                f"input_datetime.{self._dog_name}_last_feeding_morning",
                f"input_datetime.{self._dog_name}_last_feeding_lunch",
                f"input_datetime.{self._dog_name}_last_feeding_evening",
                f"input_datetime.{self._dog_name}_last_walk",
                f"input_datetime.{self._dog_name}_last_play",
                f"input_datetime.{self._dog_name}_last_training",
            ]
            
            for entity_id in activity_entities:
                state = self.hass.states.get(entity_id)
                if state and state.state not in ["unknown", "unavailable"]:
                    try:
                        activity_times.append(datetime.fromisoformat(state.state.replace("Z", "+00:00")))
                    except ValueError:
                        continue
            
            if activity_times:
                return max(activity_times)
            
            return None
            
        except Exception as e:
            _LOGGER.error("Error updating last activity sensor for %s: %s", self._dog_name, e)
            return None


# GPS Sensors

class PawControlGPSStatusSensor(PawControlSensorBase):
    """Sensor for GPS tracking status."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "gps_status")
        self._attr_icon = "mdi:crosshairs-gps"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        try:
            # Check if GPS tracking is enabled
            gps_enabled_entity = f"input_boolean.{self._dog_name}_gps_tracking_enabled"
            gps_enabled_state = self.hass.states.get(gps_enabled_entity)
            gps_enabled = gps_enabled_state.state == "on" if gps_enabled_state else False
            
            if not gps_enabled:
                return "🔴 GPS deaktiviert"
            
            # Check GPS signal strength
            signal_entity = f"input_number.{self._dog_name}_gps_signal_strength"
            signal_state = self.hass.states.get(signal_entity)
            
            if signal_state and signal_state.state not in ["unknown", "unavailable"]:
                signal_strength = float(signal_state.state)
                if signal_strength >= 80:
                    return "🟢 GPS stark"
                elif signal_strength >= 50:
                    return "🟡 GPS mittelmäßig"
                elif signal_strength >= 20:
                    return "🟠 GPS schwach"
                else:
                    return "🔴 GPS sehr schwach"
            
            return "🟡 GPS Status unbekannt"
            
        except Exception as e:
            _LOGGER.error("Error updating GPS status sensor for %s: %s", self._dog_name, e)
            return "🔴 GPS Fehler"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = super().extra_state_attributes
        
        try:
            attrs.update({
                "gps_enabled": self._get_boolean_state(f"input_boolean.{self._dog_name}_gps_tracking_enabled"),
                "signal_strength": self._get_number_value(f"input_number.{self._dog_name}_gps_signal_strength"),
                "battery_level": self._get_number_value(f"input_number.{self._dog_name}_gps_battery_level"),
                "walk_in_progress": self._get_boolean_state(f"input_boolean.{self._dog_name}_walk_in_progress"),
                "auto_detection": self._get_boolean_state(f"input_boolean.{self._dog_name}_auto_walk_detection"),
            })
            
        except Exception as e:
            _LOGGER.error("Error getting GPS status attributes for %s: %s", self._dog_name, e)
            
        return attrs

    def _get_number_value(self, entity_id: str) -> float:
        """Get number value."""
        state = self.hass.states.get(entity_id)
        try:
            return float(state.state) if state and state.state not in ["unknown", "unavailable"] else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _get_boolean_state(self, entity_id: str) -> bool:
        """Get boolean state."""
        state = self.hass.states.get(entity_id)
        return state.state == "on" if state else False


class PawControlCurrentLocationSensor(PawControlSensorBase):
    """Sensor for current location."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "current_location")
        self._attr_icon = "mdi:map-marker"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        try:
            entity_id = f"input_text.{self._dog_name}_current_location"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable", ""]:
                return state.state
            
            return "Position unbekannt"
            
        except Exception as e:
            _LOGGER.error("Error updating current location sensor for %s: %s", self._dog_name, e)
            return "Fehler"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = super().extra_state_attributes
        
        try:
            # Parse coordinates if available
            location = self.native_value
            if location and location != "Position unbekannt" and "," in location:
                try:
                    lat_str, lon_str = location.split(",")
                    attrs.update({
                        "latitude": float(lat_str.strip()),
                        "longitude": float(lon_str.strip()),
                    })
                except (ValueError, IndexError):
                    pass
            
            attrs.update({
                "home_coordinates": self._get_text_value(f"input_text.{self._dog_name}_home_coordinates"),
                "gps_tracker_status": self._get_text_value(f"input_text.{self._dog_name}_gps_tracker_status"),
            })
            
        except Exception as e:
            _LOGGER.error("Error getting current location attributes for %s: %s", self._dog_name, e)
            
        return attrs

    def _get_text_value(self, entity_id: str) -> str:
        """Get text value."""
        state = self.hass.states.get(entity_id)
        if state and state.state not in ["unknown", "unavailable"]:
            return state.state
        return ""


class PawControlWalkDistanceTodaySensor(PawControlSensorBase):
    """Sensor for walk distance today."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "walk_distance_today")
        self._attr_icon = ICON_WALK
        self._attr_native_unit_of_measurement = "km"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        try:
            entity_id = f"input_number.{self._dog_name}_walk_distance_today"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                return round(float(state.state), 2)
            
            return 0.0
            
        except (ValueError, TypeError) as e:
            _LOGGER.error("Error updating walk distance today sensor for %s: %s", self._dog_name, e)
            return None


class PawControlCurrentWalkSensor(PawControlSensorBase):
    """Sensor for current walk information."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "current_walk")
        self._attr_icon = ICON_WALK

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        try:
            # Check if walk is in progress
            walk_progress_entity = f"input_boolean.{self._dog_name}_walk_in_progress"
            walk_progress_state = self.hass.states.get(walk_progress_entity)
            walk_in_progress = walk_progress_state.state == "on" if walk_progress_state else False
            
            if not walk_in_progress:
                return "🏠 Zuhause"
            
            # Get current walk stats
            distance_entity = f"input_number.{self._dog_name}_current_walk_distance"
            duration_entity = f"input_number.{self._dog_name}_current_walk_duration"
            
            distance_state = self.hass.states.get(distance_entity)
            duration_state = self.hass.states.get(duration_entity)
            
            distance = float(distance_state.state) if distance_state and distance_state.state not in ["unknown", "unavailable"] else 0.0
            duration = int(float(duration_state.state)) if duration_state and duration_state.state not in ["unknown", "unavailable"] else 0
            
            return f"🚶 {distance:.1f}km, {duration}min"
            
        except Exception as e:
            _LOGGER.error("Error updating current walk sensor for %s: %s", self._dog_name, e)
            return "❓ Unbekannt"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = super().extra_state_attributes
        
        try:
            attrs.update({
                "walk_in_progress": self._get_boolean_state(f"input_boolean.{self._dog_name}_walk_in_progress"),
                "current_distance": self._get_number_value(f"input_number.{self._dog_name}_current_walk_distance"),
                "current_duration": self._get_number_value(f"input_number.{self._dog_name}_current_walk_duration"),
                "current_speed": self._get_number_value(f"input_number.{self._dog_name}_current_walk_speed"),
                "calories_burned": self._get_number_value(f"input_number.{self._dog_name}_calories_burned_walk"),
                "walk_route": self._get_text_value(f"input_text.{self._dog_name}_current_walk_route"),
            })
            
        except Exception as e:
            _LOGGER.error("Error getting current walk attributes for %s: %s", self._dog_name, e)
            
        return attrs

    def _get_number_value(self, entity_id: str) -> float:
        """Get number value."""
        state = self.hass.states.get(entity_id)
        try:
            return float(state.state) if state and state.state not in ["unknown", "unavailable"] else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _get_boolean_state(self, entity_id: str) -> bool:
        """Get boolean state."""
        state = self.hass.states.get(entity_id)
        return state.state == "on" if state else False

    def _get_text_value(self, entity_id: str) -> str:
        """Get text value."""
        state = self.hass.states.get(entity_id)
        if state and state.state not in ["unknown", "unavailable"]:
            return state.state
        return ""
        super().__init__(coordinator, dog_name, "status")
        self._attr_icon = ICON_STATUS
        
        # Track entities for real-time updates
        self._feeding_entities = [
            f"input_boolean.{dog_name}_feeding_morning",
            f"input_boolean.{dog_name}_feeding_lunch", 
            f"input_boolean.{dog_name}_feeding_evening",
        ]
        
        # Set up state tracking
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, self._feeding_entities + [
                    f"input_boolean.{dog_name}_outside",
                    f"input_boolean.{dog_name}_visitor_mode_input",
                    f"input_boolean.{dog_name}_emergency_mode",
                    f"input_boolean.{dog_name}_needs_attention",
                ], self._handle_state_change
            )
        )

    @callback
    def _handle_state_change(self, event: Event) -> None:
        """Handle state changes."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        try:
            # Check emergency mode first
            emergency_state = self.hass.states.get(f"input_boolean.{self._dog_name}_emergency_mode")
            if emergency_state and emergency_state.state == "on":
                self._attr_native_value = STATUS_MESSAGES["emergency"]
                self._attr_icon = "mdi:alert"
                self._attr_extra_state_attributes = {
                    **self.extra_state_attributes,
                    "priority": "critical",
                    "emergency_active": True,
                    "status_code": "emergency",
                }
                return self._attr_native_value

            # Check visitor mode
            visitor_state = self.hass.states.get(f"input_boolean.{self._dog_name}_visitor_mode_input")
            if visitor_state and visitor_state.state == "on":
                self._attr_native_value = ACTIVITY_STATUS["visitor_mode"]
                self._attr_icon = "mdi:account-group"
                self._attr_extra_state_attributes = {
                    **self.extra_state_attributes,
                    "priority": "normal",
                    "visitor_mode": True,
                    "status_code": "visitor_mode",
                }
                return self._attr_native_value

            # Check if needs attention
            attention_state = self.hass.states.get(f"input_boolean.{self._dog_name}_needs_attention")
            needs_attention = attention_state.state == "on" if attention_state else False
            
            if needs_attention:
                self._attr_native_value = STATUS_MESSAGES["needs_attention"]
                self._attr_icon = "mdi:alert-circle"
                
                # Get attention reasons
                attention_reasons = []
                if attention_state and attention_state.attributes:
                    attention_reasons = attention_state.attributes.get("reasons", [])
                
                self._attr_extra_state_attributes = {
                    **self.extra_state_attributes,
                    "priority": "medium",
                    "needs_attention": True,
                    "attention_reasons": attention_reasons,
                    "status_code": "needs_attention",
                }
                return self._attr_native_value

            # Check feeding and activity progress
            fed_count = sum(
                1 for entity_id in self._feeding_entities
                if self.hass.states.get(entity_id) and self.hass.states.get(entity_id).state == "on"
            )
            
            outside_state = self.hass.states.get(f"input_boolean.{self._dog_name}_outside")
            was_outside = outside_state.state == "on" if outside_state else False
            
            poop_state = self.hass.states.get(f"input_boolean.{self._dog_name}_poop_done")
            poop_done = poop_state.state == "on" if poop_state else False

            # Determine status based on activities
            if fed_count >= 2 and was_outside and poop_done:
                status_value = STATUS_MESSAGES["excellent"]
                status_icon = "mdi:star"
                status_code = "excellent"
                priority = "low"
            elif fed_count >= 1 and was_outside:
                status_value = STATUS_MESSAGES["very_good"]
                status_icon = "mdi:check-circle"
                status_code = "very_good"
                priority = "low"
            elif fed_count >= 1 or was_outside:
                status_value = STATUS_MESSAGES["good"]
                status_icon = "mdi:check"
                status_code = "good"
                priority = "normal"
            else:
                status_value = STATUS_MESSAGES["needs_attention"]
                status_icon = "mdi:alert-circle"
                status_code = "needs_attention"
                priority = "medium"

            self._attr_native_value = status_value
            self._attr_icon = status_icon
            self._attr_extra_state_attributes = {
                **self.extra_state_attributes,
                "fed_count": fed_count,
                "was_outside": was_outside,
                "poop_done": poop_done,
                "priority": priority,
                "status_code": status_code,
                "completion_percentage": min(100, ((fed_count + (1 if was_outside else 0) + (1 if poop_done else 0)) / 5) * 100),
            }
            
            return self._attr_native_value
            
        except Exception as e:
            _LOGGER.error("Error updating status sensor for %s: %s", self._dog_name, e)
            return STATUS_MESSAGES["unknown"]


class PawControlActivityStatusSensor(PawControlSensorBase):
    """Sensor for activity status."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "activity_status")
        self._attr_icon = ICON_STATUS

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        try:
            # Check emergency mode
            emergency_state = self.hass.states.get(f"input_boolean.{self._dog_name}_emergency_mode")
            if emergency_state and emergency_state.state == "on":
                return ACTIVITY_STATUS["emergency"]

            # Check visitor mode
            visitor_state = self.hass.states.get(f"input_boolean.{self._dog_name}_visitor_mode_input")
            if visitor_state and visitor_state.state == "on":
                return ACTIVITY_STATUS["visitor_mode"]

            # Check feeding status
            fed_morning = self._get_boolean_state(f"input_boolean.{self._dog_name}_feeding_morning")
            fed_lunch = self._get_boolean_state(f"input_boolean.{self._dog_name}_feeding_lunch")
            fed_evening = self._get_boolean_state(f"input_boolean.{self._dog_name}_feeding_evening")
            
            # Check walking status
            was_outside = self._get_boolean_state(f"input_boolean.{self._dog_name}_outside")
            
            fed_any = fed_morning or fed_lunch or fed_evening
            
            if fed_any and was_outside:
                return ACTIVITY_STATUS["all_done"]
            elif fed_any or was_outside:
                return ACTIVITY_STATUS["partially_done"]
            elif not fed_any and not was_outside:
                return ACTIVITY_STATUS["needs_both"]
            elif not fed_any:
                return ACTIVITY_STATUS["needs_feeding"]
            elif not was_outside:
                return ACTIVITY_STATUS["needs_walk"]
            else:
                return ACTIVITY_STATUS["all_done"]
                
        except Exception as e:
            _LOGGER.error("Error updating activity status sensor for %s: %s", self._dog_name, e)
            return "❓ Unbekannt"

    def _get_boolean_state(self, entity_id: str) -> bool:
        """Get boolean state of an entity."""
        state = self.hass.states.get(entity_id)
        return state.state == "on" if state else False


class PawControlDailySummarySensor(PawControlSensorBase):
    """Sensor for daily summary."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "daily_summary")
        self._attr_icon = "mdi:calendar-today"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        try:
            # Get feeding counts
            morning_count = self._get_counter_value(f"counter.{self._dog_name}_feeding_morning_count")
            lunch_count = self._get_counter_value(f"counter.{self._dog_name}_feeding_lunch_count")
            evening_count = self._get_counter_value(f"counter.{self._dog_name}_feeding_evening_count")
            
            # Get activity counts
            walk_count = self._get_counter_value(f"counter.{self._dog_name}_walk_count")
            play_count = self._get_counter_value(f"counter.{self._dog_name}_play_count")
            training_count = self._get_counter_value(f"counter.{self._dog_name}_training_count")
            
            total_feedings = morning_count + lunch_count + evening_count
            total_activities = walk_count + play_count + training_count
            
            summary = f"🍽️ {total_feedings} Mahlzeiten, 🚶 {walk_count} Spaziergänge"
            if play_count > 0:
                summary += f", 🎾 {play_count} Spielzeit"
            if training_count > 0:
                summary += f", 🎓 {training_count} Training"
                
            return summary
            
        except Exception as e:
            _LOGGER.error("Error updating daily summary sensor for %s: %s", self._dog_name, e)
            return "📊 Daten nicht verfügbar"

    def _get_counter_value(self, entity_id: str) -> int:
        """Get counter value."""
        state = self.hass.states.get(entity_id)
        try:
            return int(state.state) if state else 0
        except (ValueError, TypeError):
            return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = super().extra_state_attributes
        
        try:
            # Add detailed breakdown
            attrs.update({
                "morning_feedings": self._get_counter_value(f"counter.{self._dog_name}_feeding_morning_count"),
                "lunch_feedings": self._get_counter_value(f"counter.{self._dog_name}_feeding_lunch_count"),
                "evening_feedings": self._get_counter_value(f"counter.{self._dog_name}_feeding_evening_count"),
                "walks": self._get_counter_value(f"counter.{self._dog_name}_walk_count"),
                "play_sessions": self._get_counter_value(f"counter.{self._dog_name}_play_count"),
                "training_sessions": self._get_counter_value(f"counter.{self._dog_name}_training_count"),
                "daily_food_amount": self._get_number_value(f"input_number.{self._dog_name}_daily_food_amount"),
                "daily_walk_duration": self._get_number_value(f"input_number.{self._dog_name}_daily_walk_duration"),
            })
            
        except Exception as e:
            _LOGGER.error("Error getting daily summary attributes for %s: %s", self._dog_name, e)
            
        return attrs

    def _get_number_value(self, entity_id: str) -> float:
        """Get number value."""
        state = self.hass.states.get(entity_id)
        try:
            return float(state.state) if state else 0.0
        except (ValueError, TypeError):
            return 0.0


class PawControlLastFedSensor(PawControlSensorBase):
    """Sensor for last feeding time."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "last_fed")
        self._attr_icon = ICON_FOOD
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        """Return the state of the sensor."""
        try:
            # Check all feeding times and return the most recent
            feeding_times = []
            
            for meal in ["morning", "lunch", "evening", "snack"]:
                entity_id = f"input_datetime.{self._dog_name}_last_feeding_{meal}"
                state = self.hass.states.get(entity_id)
                if state and state.state not in ["unknown", "unavailable"]:
                    try:
                        feeding_times.append(datetime.fromisoformat(state.state.replace("Z", "+00:00")))
                    except ValueError:
                        continue
            
            if feeding_times:
                return max(feeding_times)
            
            return None
            
        except Exception as e:
            _LOGGER.error("Error updating last fed sensor for %s: %s", self._dog_name, e)
            return None


class PawControlNextFeedingSensor(PawControlSensorBase):
    """Sensor for next feeding time."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "next_feeding")
        self._attr_icon = ICON_FOOD
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        """Return the state of the sensor."""
        try:
            now = datetime.now()
            today = now.date()
            
            # Get feeding times
            morning_time = self._get_time_value(f"input_datetime.{self._dog_name}_feeding_morning_time")
            lunch_time = self._get_time_value(f"input_datetime.{self._dog_name}_feeding_lunch_time")
            evening_time = self._get_time_value(f"input_datetime.{self._dog_name}_feeding_evening_time")
            
            # Create datetime objects for today
            feeding_times = []
            if morning_time:
                morning_dt = datetime.combine(today, morning_time)
                if morning_dt > now:
                    feeding_times.append(morning_dt)
                    
            if lunch_time:
                lunch_dt = datetime.combine(today, lunch_time)
                if lunch_dt > now:
                    feeding_times.append(lunch_dt)
                    
            if evening_time:
                evening_dt = datetime.combine(today, evening_time)
                if evening_dt > now:
                    feeding_times.append(evening_dt)
            
            # If no more feedings today, return tomorrow's morning feeding
            if not feeding_times and morning_time:
                tomorrow = today + timedelta(days=1)
                feeding_times.append(datetime.combine(tomorrow, morning_time))
            
            return min(feeding_times) if feeding_times else None
            
        except Exception as e:
            _LOGGER.error("Error updating next feeding sensor for %s: %s", self._dog_name, e)
            return None

    def _get_time_value(self, entity_id: str):
        """Get time value from input_datetime."""
        state = self.hass.states.get(entity_id)
        if state and state.state not in ["unknown", "unavailable"]:
            try:
                # Parse time from datetime string
                dt = datetime.fromisoformat(state.state.replace("Z", "+00:00"))
                return dt.time()
            except ValueError:
                return None
        return None


class PawControlLastWalkSensor(PawControlSensorBase):
    """Sensor for last walk time."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "last_walk")
        self._attr_icon = ICON_WALK
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        """Return the state of the sensor."""
        try:
            # Check last walk time
            entity_id = f"input_datetime.{self._dog_name}_last_walk"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                try:
                    return datetime.fromisoformat(state.state.replace("Z", "+00:00"))
                except ValueError:
                    return None
            
            # Fallback to last outside time
            entity_id = f"input_datetime.{self._dog_name}_last_outside"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                try:
                    return datetime.fromisoformat(state.state.replace("Z", "+00:00"))
                except ValueError:
                    return None
            
            return None
            
        except Exception as e:
            _LOGGER.error("Error updating last walk sensor for %s: %s", self._dog_name, e)
            return None


class PawControlNextWalkSensor(PawControlSensorBase):
    """Sensor for next recommended walk time."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "next_walk")
        self._attr_icon = ICON_WALK
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        """Return the state of the sensor."""
        try:
            now = datetime.now()
            
            # Get last walk time
            last_walk_entity = f"input_datetime.{self._dog_name}_last_walk"
            last_walk_state = self.hass.states.get(last_walk_entity)
            
            if last_walk_state and last_walk_state.state not in ["unknown", "unavailable"]:
                try:
                    last_walk = datetime.fromisoformat(last_walk_state.state.replace("Z", "+00:00"))
                    # Recommend next walk 4-6 hours after last walk
                    next_walk = last_walk + timedelta(hours=5)
                    return next_walk if next_walk > now else now + timedelta(hours=1)
                except ValueError:
                    pass
            
            # Default: next walk in 1 hour if no previous walk recorded
            return now + timedelta(hours=1)
            
        except Exception as e:
            _LOGGER.error("Error updating next walk sensor for %s: %s", self._dog_name, e)
            return None


class PawControlHealthStatusSensor(PawControlSensorBase):
    """Sensor for health status."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
