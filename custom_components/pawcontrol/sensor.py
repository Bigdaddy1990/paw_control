"""Sensor platform for Paw Control - REPARIERT UND VEREINFACHT."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ICONS, ATTR_DOG_NAME, ATTR_LAST_UPDATED
from .coordinator import PawControlCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    dog_name = coordinator.dog_name
    
    entities = [
        # Status sensors
        PawControlStatusSensor(coordinator, dog_name),
        PawControlDailySummarySensor(coordinator, dog_name),
        
        # Activity sensors
        PawControlLastWalkSensor(coordinator, dog_name),
        PawControlWalkCountSensor(coordinator, dog_name),
        
        # Health sensors
        PawControlWeightSensor(coordinator, dog_name),
        PawControlHealthStatusSensor(coordinator, dog_name),
        
        # Location sensors
        PawControlLocationSensor(coordinator, dog_name),
        PawControlGPSSignalSensor(coordinator, dog_name),
    ]
    
    async_add_entities(entities)


class PawControlSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Paw Control sensors."""

    def __init__(
        self,
        coordinator: PawControlCoordinator,
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
            "sw_version": "1.0.0",
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

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "status")
        self._attr_icon = ICONS["status"]

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.get_status_summary()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = super().extra_state_attributes
        
        if self.coordinator.data:
            feeding = self.coordinator.data.get("feeding_status", {})
            activity = self.coordinator.data.get("activity_status", {})
            
            attrs.update({
                "morning_fed": feeding.get("morning_fed", False),
                "evening_fed": feeding.get("evening_fed", False),
                "was_outside": activity.get("was_outside", False),
                "walked_today": activity.get("walked_today", False),
                "poop_done": activity.get("poop_done", False),
                "walk_count": activity.get("walk_count", 0),
            })
        
        return attrs


class PawControlDailySummarySensor(PawControlSensorBase):
    """Sensor for daily summary."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "daily_summary")
        self._attr_icon = "mdi:calendar-today"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return "Keine Daten verfügbar"
        
        try:
            activity = self.coordinator.data.get("activity_status", {})
            feeding = self.coordinator.data.get("feeding_status", {})
            
            walk_count = activity.get("walk_count", 0)
            fed_count = sum([
                feeding.get("morning_fed", False),
                feeding.get("evening_fed", False)
            ])
            
            return f"🚶 {walk_count} Spaziergänge, 🍽️ {fed_count} Mahlzeiten"
            
        except Exception as e:
            _LOGGER.error("Error getting daily summary: %s", e)
            return "Fehler beim Laden"


class PawControlLastWalkSensor(PawControlSensorBase):
    """Sensor for last walk time."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "last_walk")
        self._attr_icon = ICONS["walk"]
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        try:
            activity = self.coordinator.data.get("activity_status", {})
            last_walk = activity.get("last_walk")
            
            if last_walk and last_walk not in ["unknown", "unavailable"]:
                return datetime.fromisoformat(last_walk.replace("Z", "+00:00"))
            
            return None
            
        except (ValueError, TypeError) as e:
            _LOGGER.error("Error parsing last walk time: %s", e)
            return None


class PawControlWalkCountSensor(PawControlSensorBase):
    """Sensor for walk count."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "walk_count")
        self._attr_icon = ICONS["walk"]

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return 0
        
        activity = self.coordinator.data.get("activity_status", {})
        return activity.get("walk_count", 0)


class PawControlWeightSensor(PawControlSensorBase):
    """Sensor for weight."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "weight")
        self._attr_icon = ICONS["weight"]
        self._attr_native_unit_of_measurement = "kg"
        self._attr_device_class = SensorDeviceClass.WEIGHT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        health = self.coordinator.data.get("health_status", {})
        return health.get("weight")


class PawControlHealthStatusSensor(PawControlSensorBase):
    """Sensor for health status."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "health_status")
        self._attr_icon = ICONS["health"]

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return "Unbekannt"
        
        health = self.coordinator.data.get("health_status", {})
        return health.get("status", "Gut")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = super().extra_state_attributes
        
        if self.coordinator.data:
            health = self.coordinator.data.get("health_status", {})
            attrs.update({
                "weight": health.get("weight"),
                "health_notes": health.get("health_notes", ""),
            })
        
        return attrs


class PawControlLocationSensor(PawControlSensorBase):
    """Sensor for current location."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "location")
        self._attr_icon = ICONS["location"]

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return "Unbekannt"
        
        location = self.coordinator.data.get("location_status", {})
        return location.get("current_location", "Unbekannt")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = super().extra_state_attributes
        
        if self.coordinator.data:
            location = self.coordinator.data.get("location_status", {})
            current_loc = location.get("current_location", "")
            
            # Try to parse coordinates
            if current_loc and "," in current_loc:
                try:
                    lat_str, lon_str = current_loc.split(",")
                    attrs.update({
                        "latitude": float(lat_str.strip()),
                        "longitude": float(lon_str.strip()),
                    })
                except (ValueError, IndexError):
                    pass
            
            attrs.update({
                "gps_signal": location.get("gps_signal", 0),
                "gps_available": location.get("gps_available", False),
            })
        
        return attrs


class PawControlGPSSignalSensor(PawControlSensorBase):
    """Sensor for GPS signal strength."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, dog_name, "gps_signal")
        self._attr_icon = ICONS["signal"]
        self._attr_native_unit_of_measurement = "%"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return 0
        
        location = self.coordinator.data.get("location_status", {})
        return location.get("gps_signal", 0)
