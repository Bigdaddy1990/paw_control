"""Select platform for Paw Control integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN, 
    ICONS, 
    ATTR_DOG_NAME, 
    ATTR_LAST_UPDATED,
    HEALTH_STATUS_OPTIONS,
    MOOD_OPTIONS,
    ENERGY_LEVEL_OPTIONS,
    ACTIVITY_LEVELS,
    SIZE_CATEGORIES,
    EMERGENCY_LEVELS,
    WALK_TYPES,
)
from .coordinator import PawControlCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    dog_name = coordinator.dog_name
    
    entities = [
        # Health status selects
        PawControlHealthStatusSelect(coordinator, dog_name),
        PawControlMoodSelect(coordinator, dog_name),
        PawControlEnergyLevelSelect(coordinator, dog_name),
        PawControlAppetiteLevelSelect(coordinator, dog_name),
        
        # Activity selects
        PawControlActivityLevelSelect(coordinator, dog_name),
        PawControlPreferredWalkTypeSelect(coordinator, dog_name),
        
        # Physical characteristics
        PawControlSizeCategorySelect(coordinator, dog_name),
        
        # System selects
        PawControlEmergencyLevelSelect(coordinator, dog_name),
        PawControlGPSSourceTypeSelect(coordinator, dog_name),
    ]
    
    async_add_entities(entities)


class PawControlSelectBase(CoordinatorEntity, SelectEntity):
    """Base class for Paw Control select entities."""

    def __init__(
        self,
        coordinator: PawControlCoordinator,
        dog_name: str,
        select_type: str,
        entity_suffix: str,
        options: list[str],
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._dog_name = dog_name
        self._select_type = select_type
        self._entity_suffix = entity_suffix
        self._helper_entity_id = f"input_select.{dog_name}_{entity_suffix}"
        self._attr_unique_id = f"{DOMAIN}_{dog_name.lower()}_{select_type}"
        self._attr_name = f"{dog_name.title()} {select_type.replace('_', ' ').title()}"
        self._attr_options = options

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
    def current_option(self) -> str | None:
        """Return the current selected option."""
        helper_state = self.hass.states.get(self._helper_entity_id)
        if helper_state and helper_state.state not in ["unknown", "unavailable"]:
            return helper_state.state
        return None

    async def async_select_option(self, option: str) -> None:
        """Select an option."""
        if option not in self.options:
            _LOGGER.error("Invalid option %s for %s", option, self._helper_entity_id)
            return
        
        try:
            await self.hass.services.async_call(
                "input_select", "select_option",
                {
                    "entity_id": self._helper_entity_id,
                    "option": option
                },
                blocking=True
            )
        except Exception as e:
            _LOGGER.error("Failed to set option for %s: %s", self._helper_entity_id, e)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.hass.states.get(self._helper_entity_id) is not None


# HEALTH STATUS SELECTS

class PawControlHealthStatusSelect(PawControlSelectBase):
    """Select entity for health status."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, dog_name, "health_status", "health_status", HEALTH_STATUS_OPTIONS)
        self._attr_icon = ICONS["health"]


class PawControlMoodSelect(PawControlSelectBase):
    """Select entity for mood."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, dog_name, "mood", "mood", MOOD_OPTIONS)
        self._attr_icon = ICONS["mood"]


class PawControlEnergyLevelSelect(PawControlSelectBase):
    """Select entity for energy level."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, dog_name, "energy_level", "energy_level_category", ENERGY_LEVEL_OPTIONS)
        self._attr_icon = "mdi:battery"


class PawControlAppetiteLevelSelect(PawControlSelectBase):
    """Select entity for appetite level."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, dog_name, "appetite_level", "appetite_level", [
            "Kein Appetit",
            "Wenig Appetit", 
            "Normal",
            "Guter Appetit",
            "Sehr guter Appetit"
        ])
        self._attr_icon = ICONS["food"]


# ACTIVITY SELECTS

class PawControlActivityLevelSelect(PawControlSelectBase):
    """Select entity for activity level."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, dog_name, "activity_level", "activity_level", ACTIVITY_LEVELS)
        self._attr_icon = ICONS["walk"]


class PawControlPreferredWalkTypeSelect(PawControlSelectBase):
    """Select entity for preferred walk type."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, dog_name, "preferred_walk_type", "preferred_walk_type", WALK_TYPES)
        self._attr_icon = ICONS["walk"]


# PHYSICAL CHARACTERISTICS

class PawControlSizeCategorySelect(PawControlSelectBase):
    """Select entity for size category."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, dog_name, "size_category", "size_category", SIZE_CATEGORIES)
        self._attr_icon = ICONS["weight"]


# SYSTEM SELECTS

class PawControlEmergencyLevelSelect(PawControlSelectBase):
    """Select entity for emergency level."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, dog_name, "emergency_level", "emergency_level", EMERGENCY_LEVELS)
        self._attr_icon = ICONS["emergency"]


class PawControlGPSSourceTypeSelect(PawControlSelectBase):
    """Select entity for GPS source type."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, dog_name, "gps_source_type", "gps_source_type", [
            "Manual",
            "Smartphone", 
            "Device Tracker",
            "Person Entity",
            "Tractive",
            "Webhook",
            "MQTT"
        ])
        self._attr_icon = ICONS["gps"]