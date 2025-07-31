"""Number platform for Paw Control integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.number import NumberEntity, NumberDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ICONS, ATTR_DOG_NAME, ATTR_LAST_UPDATED, UNITS, STATE_CLASSES
from .coordinator import PawControlCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    dog_name = coordinator.dog_name
    
    entities = [
        # Physical metrics
        PawControlWeightNumber(coordinator, dog_name),
        PawControlAgeYearsNumber(coordinator, dog_name),
        PawControlTemperatureNumber(coordinator, dog_name),
        
        # Daily amounts and durations
        PawControlDailyFoodAmountNumber(coordinator, dog_name),
        PawControlDailyWalkDurationNumber(coordinator, dog_name),
        PawControlDailyPlayDurationNumber(coordinator, dog_name),
        
        # GPS and location
        PawControlGPSSignalStrengthNumber(coordinator, dog_name),
        PawControlGPSBatteryLevelNumber(coordinator, dog_name),
        PawControlHomeDistanceNumber(coordinator, dog_name),
        PawControlGeofenceRadiusNumber(coordinator, dog_name),
        
        # Walk statistics
        PawControlCurrentWalkDistanceNumber(coordinator, dog_name),
        PawControlCurrentWalkDurationNumber(coordinator, dog_name),
        PawControlCurrentWalkSpeedNumber(coordinator, dog_name),
        PawControlWalkDistanceTodayNumber(coordinator, dog_name),
        PawControlWalkDistanceWeeklyNumber(coordinator, dog_name),
        PawControlCaloriesBurnedWalkNumber(coordinator, dog_name),
        
        # Health scores
        PawControlHealthScoreNumber(coordinator, dog_name),
        PawControlHappinessScoreNumber(coordinator, dog_name),
        PawControlActivityScoreNumber(coordinator, dog_name),
    ]
    
    async_add_entities(entities)


class PawControlNumberBase(CoordinatorEntity, NumberEntity):
    """Base class for Paw Control number entities."""

    def __init__(
        self,
        coordinator: PawControlCoordinator,
        dog_name: str,
        number_type: str,
        entity_suffix: str,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._dog_name = dog_name
        self._number_type = number_type
        self._entity_suffix = entity_suffix
        self._helper_entity_id = f"input_number.{dog_name}_{entity_suffix}"
        self._attr_unique_id = f"{DOMAIN}_{dog_name.lower()}_{number_type}"
        self._attr_name = f"{dog_name.title()} {number_type.replace('_', ' ').title()}"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._dog_name.lower())},
            "name": f"Paw Control - {self._dog_name}",
            "manufacturer": "Paw Control",
            "model": "Dog Management System",
            "sw_version": "1.0.0",
        }

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            ATTR_DOG_NAME: self._dog_name,
            ATTR_LAST_UPDATED: datetime.now().isoformat(),
            "helper_entity": self._helper_entity_id,
        }

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        helper_state = self.hass.states.get(self._helper_entity_id)
        if helper_state and helper_state.state not in ["unknown", "unavailable"]:
            try:
                return float(helper_state.state)
            except (ValueError, TypeError):
                pass
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        try:
            await self.hass.services.async_call(
                "input_number", "set_value",
                {
                    "entity_id": self._helper_entity_id,
                    "value": value
                },
                blocking=True
            )
        except Exception as e:
            _LOGGER.error("Failed to set value for %s: %s", self._helper_entity_id, e)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.hass.states.get(self._helper_entity_id) is not None


# PHYSICAL METRICS

class PawControlWeightNumber(PawControlNumberBase):
    """Number entity for dog weight."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "weight", "weight")
        self._attr_icon = ICONS["weight"]
        self._attr_native_unit_of_measurement = UNITS["weight"]
        self._attr_device_class = NumberDeviceClass.WEIGHT
        self._attr_native_min_value = 0.5
        self._attr_native_max_value = 100.0
        self._attr_native_step = 0.1
        self._attr_mode = "slider"


class PawControlAgeYearsNumber(PawControlNumberBase):
    """Number entity for dog age in years."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "age_years", "age_years")
        self._attr_icon = "mdi:calendar"
        self._attr_native_unit_of_measurement = "Jahre"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 25
        self._attr_native_step = 0.1
        self._attr_mode = "slider"


class PawControlTemperatureNumber(PawControlNumberBase):
    """Number entity for dog temperature."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "temperature", "temperature")
        self._attr_icon = ICONS["temperature"]
        self._attr_native_unit_of_measurement = UNITS["temperature"]
        self._attr_device_class = NumberDeviceClass.TEMPERATURE
        self._attr_native_min_value = 35.0
        self._attr_native_max_value = 42.0
        self._attr_native_step = 0.1
        self._attr_mode = "slider"


# DAILY AMOUNTS AND DURATIONS

class PawControlDailyFoodAmountNumber(PawControlNumberBase):
    """Number entity for daily food amount."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "daily_food_amount", "daily_food_amount")
        self._attr_icon = ICONS["food"]
        self._attr_native_unit_of_measurement = UNITS["food_amount"]
        self._attr_native_min_value = 0
        self._attr_native_max_value = 2000
        self._attr_native_step = 10
        self._attr_mode = "slider"
        self._attr_state_class = STATE_CLASSES["total_increasing"]


class PawControlDailyWalkDurationNumber(PawControlNumberBase):
    """Number entity for daily walk duration."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "daily_walk_duration", "daily_walk_duration")
        self._attr_icon = ICONS["walk"]
        self._attr_native_unit_of_measurement = UNITS["duration_min"]
        self._attr_device_class = NumberDeviceClass.DURATION
        self._attr_native_min_value = 0
        self._attr_native_max_value = 480
        self._attr_native_step = 5
        self._attr_mode = "slider"
        self._attr_state_class = STATE_CLASSES["total_increasing"]


class PawControlDailyPlayDurationNumber(PawControlNumberBase):
    """Number entity for daily play duration."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "daily_play_duration", "daily_play_duration")
        self._attr_icon = ICONS["play"]
        self._attr_native_unit_of_measurement = UNITS["duration_min"]
        self._attr_device_class = NumberDeviceClass.DURATION
        self._attr_native_min_value = 0
        self._attr_native_max_value = 240
        self._attr_native_step = 5
        self._attr_mode = "slider"
        self._attr_state_class = STATE_CLASSES["total_increasing"]


# GPS AND LOCATION

class PawControlGPSSignalStrengthNumber(PawControlNumberBase):
    """Number entity for GPS signal strength."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "gps_signal_strength", "gps_signal_strength")
        self._attr_icon = ICONS["signal"]
        self._attr_native_unit_of_measurement = UNITS["percentage"]
        self._attr_device_class = NumberDeviceClass.SIGNAL_STRENGTH
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_mode = "slider"
        self._attr_state_class = STATE_CLASSES["measurement"]


class PawControlGPSBatteryLevelNumber(PawControlNumberBase):
    """Number entity for GPS battery level."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "gps_battery_level", "gps_battery_level")
        self._attr_icon = ICONS["battery"]
        self._attr_native_unit_of_measurement = UNITS["percentage"]
        self._attr_device_class = NumberDeviceClass.BATTERY
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_mode = "slider"
        self._attr_state_class = STATE_CLASSES["measurement"]


class PawControlHomeDistanceNumber(PawControlNumberBase):
    """Number entity for distance from home."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "home_distance", "home_distance")
        self._attr_icon = ICONS["home"]
        self._attr_native_unit_of_measurement = UNITS["distance_m"]
        self._attr_device_class = NumberDeviceClass.DISTANCE
        self._attr_native_min_value = 0
        self._attr_native_max_value = 10000
        self._attr_native_step = 1
        self._attr_mode = "slider"
        self._attr_state_class = STATE_CLASSES["measurement"]


class PawControlGeofenceRadiusNumber(PawControlNumberBase):
    """Number entity for geofence radius."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "geofence_radius", "geofence_radius")
        self._attr_icon = ICONS["location"]
        self._attr_native_unit_of_measurement = UNITS["distance_m"]
        self._attr_device_class = NumberDeviceClass.DISTANCE
        self._attr_native_min_value = 10
        self._attr_native_max_value = 1000
        self._attr_native_step = 10
        self._attr_mode = "slider"


# WALK STATISTICS

class PawControlCurrentWalkDistanceNumber(PawControlNumberBase):
    """Number entity for current walk distance."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "current_walk_distance", "current_walk_distance")
        self._attr_icon = ICONS["walk"]
        self._attr_native_unit_of_measurement = UNITS["distance_km"]
        self._attr_device_class = NumberDeviceClass.DISTANCE
        self._attr_native_min_value = 0
        self._attr_native_max_value = 50
        self._attr_native_step = 0.01
        self._attr_mode = "slider"
        self._attr_state_class = STATE_CLASSES["total_increasing"]


class PawControlCurrentWalkDurationNumber(PawControlNumberBase):
    """Number entity for current walk duration."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "current_walk_duration", "current_walk_duration")
        self._attr_icon = ICONS["walk"]
        self._attr_native_unit_of_measurement = UNITS["duration_min"]
        self._attr_device_class = NumberDeviceClass.DURATION
        self._attr_native_min_value = 0
        self._attr_native_max_value = 300
        self._attr_native_step = 1
        self._attr_mode = "slider"
        self._attr_state_class = STATE_CLASSES["total_increasing"]


class PawControlCurrentWalkSpeedNumber(PawControlNumberBase):
    """Number entity for current walk speed."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "current_walk_speed", "current_walk_speed")
        self._attr_icon = ICONS["walk"]
        self._attr_native_unit_of_measurement = UNITS["speed"]
        self._attr_device_class = NumberDeviceClass.SPEED
        self._attr_native_min_value = 0
        self._attr_native_max_value = 50
        self._attr_native_step = 0.1
        self._attr_mode = "slider"
        self._attr_state_class = STATE_CLASSES["measurement"]


class PawControlWalkDistanceTodayNumber(PawControlNumberBase):
    """Number entity for today's walk distance."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "walk_distance_today", "walk_distance_today")
        self._attr_icon = ICONS["statistics"]
        self._attr_native_unit_of_measurement = UNITS["distance_km"]
        self._attr_device_class = NumberDeviceClass.DISTANCE
        self._attr_native_min_value = 0
        self._attr_native_max_value = 50
        self._attr_native_step = 0.01
        self._attr_mode = "slider"
        self._attr_state_class = STATE_CLASSES["total_increasing"]


class PawControlWalkDistanceWeeklyNumber(PawControlNumberBase):
    """Number entity for weekly walk distance."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "walk_distance_weekly", "walk_distance_weekly")
        self._attr_icon = ICONS["statistics"]
        self._attr_native_unit_of_measurement = UNITS["distance_km"]
        self._attr_device_class = NumberDeviceClass.DISTANCE
        self._attr_native_min_value = 0
        self._attr_native_max_value = 200
        self._attr_native_step = 0.1
        self._attr_mode = "slider"
        self._attr_state_class = STATE_CLASSES["total_increasing"]


class PawControlCaloriesBurnedWalkNumber(PawControlNumberBase):
    """Number entity for calories burned during walks."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "calories_burned_walk", "calories_burned_walk")
        self._attr_icon = "mdi:fire"
        self._attr_native_unit_of_measurement = UNITS["calories"]
        self._attr_native_min_value = 0
        self._attr_native_max_value = 2000
        self._attr_native_step = 1
        self._attr_mode = "slider"
        self._attr_state_class = STATE_CLASSES["total_increasing"]


# HEALTH SCORES

class PawControlHealthScoreNumber(PawControlNumberBase):
    """Number entity for health score."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "health_score", "health_score")
        self._attr_icon = ICONS["health"]
        self._attr_native_min_value = 0
        self._attr_native_max_value = 10
        self._attr_native_step = 0.1
        self._attr_mode = "slider"
        self._attr_state_class = STATE_CLASSES["measurement"]


class PawControlHappinessScoreNumber(PawControlNumberBase):
    """Number entity for happiness score."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "happiness_score", "happiness_score")
        self._attr_icon = ICONS["mood"]
        self._attr_native_min_value = 0
        self._attr_native_max_value = 10
        self._attr_native_step = 0.1
        self._attr_mode = "slider"
        self._attr_state_class = STATE_CLASSES["measurement"]


class PawControlActivityScoreNumber(PawControlNumberBase):
    """Number entity for activity score."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, dog_name, "activity_score", "activity_score")
        self._attr_icon = ICONS["walk"]
        self._attr_native_min_value = 0
        self._attr_native_max_value = 10
        self._attr_native_step = 0.1
        self._attr_mode = "slider"
        self._attr_state_class = STATE_CLASSES["measurement"]