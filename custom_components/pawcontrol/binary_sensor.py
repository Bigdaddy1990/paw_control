"""Binary sensor platform for Paw Control - REPARIERT UND VEREINFACHT."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
    """Set up the binary sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    dog_name = coordinator.dog_name
    
    entities = [
        # Status binary sensors
        PawControlIsHungryBinarySensor(coordinator, dog_name),
        PawControlNeedsWalkBinarySensor(coordinator, dog_name),
        PawControlIsOutsideBinarySensor(coordinator, dog_name),
        PawControlEmergencyModeBinarySensor(coordinator, dog_name),
        PawControlVisitorModeBinarySensor(coordinator, dog_name),
        PawControlNeedsAttentionBinarySensor(coordinator, dog_name),
        PawControlGPSTrackingBinarySensor(coordinator, dog_name),
    ]
    
    async_add_entities(entities)


class PawControlBinarySensorBase(CoordinatorEntity, BinarySensorEntity):
    """Base class for Paw Control binary sensors."""

    def __init__(
        self,
        coordinator: PawControlCoordinator,
        dog_name: str,
        sensor_type: str,
    ) -> None:
        """Initialize the binary sensor."""
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


class PawControlIsHungryBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for hunger status."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "is_hungry")
        self._attr_icon = ICONS["food"]

    @property
    def is_on(self) -> bool | None:
        """Return true if the dog is hungry."""
        if not self.coordinator.data:
            return None
        
        feeding = self.coordinator.data.get("feeding_status", {})
        return feeding.get("needs_feeding", True)


class PawControlNeedsWalkBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for walk need status."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "needs_walk")
        self._attr_icon = ICONS["walk"]

    @property
    def is_on(self) -> bool | None:
        """Return true if the dog needs a walk."""
        if not self.coordinator.data:
            return None
        
        activity = self.coordinator.data.get("activity_status", {})
        return activity.get("needs_walk", True)


class PawControlIsOutsideBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for outside status."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "is_outside")
        self._attr_icon = ICONS["outside"]
        self._attr_device_class = BinarySensorDeviceClass.PRESENCE

    @property
    def is_on(self) -> bool | None:
        """Return true if the dog is outside."""
        if not self.coordinator.data:
            return None
        
        activity = self.coordinator.data.get("activity_status", {})
        return activity.get("was_outside", False)


class PawControlEmergencyModeBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for emergency mode."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "emergency_mode")
        self._attr_icon = ICONS["emergency"]
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        """Return true if emergency mode is active."""
        try:
            emergency_state = self.hass.states.get(f"input_boolean.{self._dog_name}_emergency_mode")
            return emergency_state.state == "on" if emergency_state else False
        except Exception as e:
            _LOGGER.error("Error checking emergency mode: %s", e)
            return False


class PawControlVisitorModeBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for visitor mode."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "visitor_mode")
        self._attr_icon = ICONS["visitor"]

    @property
    def is_on(self) -> bool | None:
        """Return true if visitor mode is active."""
        try:
            visitor_state = self.hass.states.get(f"input_boolean.{self._dog_name}_visitor_mode")
            return visitor_state.state == "on" if visitor_state else False
        except Exception as e:
            _LOGGER.error("Error checking visitor mode: %s", e)
            return False


class PawControlNeedsAttentionBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for needs attention status."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "needs_attention")
        self._attr_icon = "mdi:bell-alert"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        """Return true if dog needs attention."""
        if not self.coordinator.data:
            return None
        
        try:
            feeding = self.coordinator.data.get("feeding_status", {})
            activity = self.coordinator.data.get("activity_status", {})
            
            # Check if not fed for too long
            last_feeding = feeding.get("last_feeding")
            if last_feeding:
                try:
                    last_fed_time = datetime.fromisoformat(last_feeding.replace("Z", "+00:00"))
                    if datetime.now() - last_fed_time > timedelta(hours=12):
                        return True
                except ValueError:
                    pass
            
            # Check if not walked for too long
            last_walk = activity.get("last_walk")
            if last_walk:
                try:
                    last_walk_time = datetime.fromisoformat(last_walk.replace("Z", "+00:00"))
                    if datetime.now() - last_walk_time > timedelta(hours=8):
                        return True
                except ValueError:
                    pass
            
            # Check if emergency mode is active
            emergency_state = self.hass.states.get(f"input_boolean.{self._dog_name}_emergency_mode")
            if emergency_state and emergency_state.state == "on":
                return True
            
            return False
            
        except Exception as e:
            _LOGGER.error("Error calculating attention need: %s", e)
            return None


class PawControlGPSTrackingBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for GPS tracking status."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "gps_tracking")
        self._attr_icon = ICONS["gps"]

    @property
    def is_on(self) -> bool | None:
        """Return true if GPS tracking is active."""
        if not self.coordinator.data:
            return None
        
        location = self.coordinator.data.get("location_status", {})
        return location.get("gps_available", False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = super().extra_state_attributes
        
        if self.coordinator.data:
            location = self.coordinator.data.get("location_status", {})
            attrs.update({
                "gps_signal": location.get("gps_signal", 0),
                "current_location": location.get("current_location", "Unknown"),
            })
        
        return attrs
