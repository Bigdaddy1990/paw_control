"""Text platform for Paw Control integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.text import TextEntity, TextMode
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
    """Set up the text platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    dog_name = coordinator.dog_name
    
    entities = [
        # Basic information
        PawControlBreedText(coordinator, dog_name),
        PawControlNotesText(coordinator, dog_name),
        PawControlDailyNotesText(coordinator, dog_name),
        
        # Health notes
        PawControlHealthNotesText(coordinator, dog_name),
        PawControlMedicationNotesText(coordinator, dog_name),
        PawControlVetContactText(coordinator, dog_name),
        
        # Location and GPS
        PawControlCurrentLocationText(coordinator, dog_name),
        PawControlHomeCoordinatesText(coordinator, dog_name),
        PawControlCurrentWalkRouteText(coordinator, dog_name),
        PawControlFavoriteWalkRoutesText(coordinator, dog_name),
        
        # GPS tracker management
        PawControlGPSTrackerStatusText(coordinator, dog_name),
        PawControlGPSTrackerConfigText(coordinator, dog_name),
        
        # Visitor mode
        PawControlVisitorNameText(coordinator, dog_name),
        PawControlVisitorInstructionsText(coordinator, dog_name),
        
        # Activity history
        PawControlWalkHistoryTodayText(coordinator, dog_name),
        PawControlActivityHistoryText(coordinator, dog_name),
        PawControlLastActivityText(coordinator, dog_name),
    ]
    
    async_add_entities(entities)


class PawControlTextBase(CoordinatorEntity, TextEntity):
    """Base class for Paw Control text entities."""

    def __init__(
        self,
        coordinator: PawControlCoordinator,
        dog_name: str,
        text_type: str,
        entity_suffix: str,
        max_length: int = 255,
        mode: TextMode = TextMode.TEXT,
    ) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator)
        self._dog_name = dog_name
        self._text_type = text_type
        self._entity_suffix = entity_suffix
        self._helper_entity_id = f"input_text.{dog_name}_{entity_suffix}"
        self._attr_unique_id = f"{DOMAIN}_{dog_name.lower()}_{text_type}"
        self._attr_name = f"{dog_name.title()} {text_type.replace('_', ' ').title()}"
        self._attr_native_max = max_length
        self._attr_mode = mode

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
    def native_value(self) -> str | None:
        """Return the current value."""
        helper_state = self.hass.states.get(self._helper_entity_id)
        if helper_state and helper_state.state not in ["unknown", "unavailable"]:
            return helper_state.state
        return None

    async def async_set_value(self, value: str) -> None:
        """Set the text value."""
        try:
            # Limit to max length
            if len(value) > self.native_max:
                value = value[:self.native_max]
            
            await self.hass.services.async_call(
                "input_text", "set_value",
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


# BASIC INFORMATION

class PawControlBreedText(PawControlTextBase):
    """Text entity for dog breed."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, dog_name, "breed", "breed", 100)
        self._attr_icon = "mdi:dog"


class PawControlNotesText(PawControlTextBase):
    """Text entity for general notes."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, dog_name, "notes", "notes", 255, TextMode.TEXT)
        self._attr_icon = "mdi:note-text"


class PawControlDailyNotesText(PawControlTextBase):
    """Text entity for daily notes."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, dog_name, "daily_notes", "daily_notes", 500, TextMode.TEXT)
        self._attr_icon = "mdi:note-text-outline"


# HEALTH NOTES

class PawControlHealthNotesText(PawControlTextBase):
    """Text entity for health notes."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, dog_name, "health_notes", "health_notes", 255, TextMode.TEXT)
        self._attr_icon = ICONS["health"]


class PawControlMedicationNotesText(PawControlTextBase):
    """Text entity for medication notes."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, dog_name, "medication_notes", "medication_notes", 255, TextMode.TEXT)
        self._attr_icon = ICONS["medication"]


class PawControlVetContactText(PawControlTextBase):
    """Text entity for veterinarian contact."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, dog_name, "vet_contact", "vet_contact", 255)
        self._attr_icon = ICONS["vet"]


# LOCATION AND GPS

class PawControlCurrentLocationText(PawControlTextBase):
    """Text entity for current location."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, dog_name, "current_location", "current_location", 100)
        self._attr_icon = ICONS["location"]


class PawControlHomeCoordinatesText(PawControlTextBase):
    """Text entity for home coordinates."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, dog_name, "home_coordinates", "home_coordinates", 50)
        self._attr_icon = ICONS["home"]
        self._attr_pattern = r"^-?\d+\.?\d*,-?\d+\.?\d*$"  # Lat,Lon format


class PawControlCurrentWalkRouteText(PawControlTextBase):
    """Text entity for current walk route."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, dog_name, "current_walk_route", "current_walk_route", 1000, TextMode.TEXT)
        self._attr_icon = ICONS["walk"]


class PawControlFavoriteWalkRoutesText(PawControlTextBase):
    """Text entity for favorite walk routes."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, dog_name, "favorite_walk_routes", "favorite_walk_routes", 1000, TextMode.TEXT)
        self._attr_icon = ICONS["walk"]


# GPS TRACKER MANAGEMENT

class PawControlGPSTrackerStatusText(PawControlTextBase):
    """Text entity for GPS tracker status."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, dog_name, "gps_tracker_status", "gps_tracker_status", 500)
        self._attr_icon = ICONS["gps"]


class PawControlGPSTrackerConfigText(PawControlTextBase):
    """Text entity for GPS tracker configuration."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, dog_name, "gps_tracker_config", "gps_tracker_config", 1000, TextMode.TEXT)
        self._attr_icon = ICONS["settings"]


# VISITOR MODE

class PawControlVisitorNameText(PawControlTextBase):
    """Text entity for visitor name."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, dog_name, "visitor_name", "visitor_name", 100)
        self._attr_icon = ICONS["visitor"]


class PawControlVisitorInstructionsText(PawControlTextBase):
    """Text entity for visitor instructions."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, dog_name, "visitor_instructions", "visitor_instructions", 500, TextMode.TEXT)
        self._attr_icon = ICONS["visitor"]


# ACTIVITY HISTORY

class PawControlWalkHistoryTodayText(PawControlTextBase):
    """Text entity for today's walk history."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, dog_name, "walk_history_today", "walk_history_today", 500, TextMode.TEXT)
        self._attr_icon = ICONS["walk"]


class PawControlActivityHistoryText(PawControlTextBase):
    """Text entity for activity history."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, dog_name, "activity_history", "activity_history", 1000, TextMode.TEXT)
        self._attr_icon = ICONS["statistics"]


class PawControlLastActivityText(PawControlTextBase):
    """Text entity for last activity."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator, dog_name, "last_activity", "last_activity", 255)
        self._attr_icon = ICONS["status"]