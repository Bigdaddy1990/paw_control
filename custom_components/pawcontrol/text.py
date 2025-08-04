"""Text platform for Paw Control integration."""
from __future__ import annotations

import logging
from homeassistant.components.text import TextMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import PawControlCoordinator
from .entities import PawControlTextEntity
from .helpers.entity import get_icon

_LOGGER = logging.getLogger(__name__)


TEXT_ENTITIES: list[dict] = [
    {"key": "breed", "icon": "mdi:dog", "max_length": 100},
    {"key": "notes", "icon": "mdi:note-text", "max_length": 255, "mode": TextMode.TEXT},
    {"key": "daily_notes", "icon": "mdi:note-text-outline", "max_length": 500, "mode": TextMode.TEXT},
    {"key": "health_notes", "icon": get_icon("health"), "max_length": 255, "mode": TextMode.TEXT},
    {"key": "medication_notes", "icon": get_icon("medication"), "max_length": 255, "mode": TextMode.TEXT},
    {"key": "vet_contact", "icon": get_icon("vet"), "max_length": 255},
    {"key": "current_location", "icon": get_icon("location"), "max_length": 100},
    {"key": "home_coordinates", "icon": get_icon("home"), "max_length": 50},
    {"key": "current_walk_route", "icon": get_icon("walk"), "max_length": 1000, "mode": TextMode.TEXT},
    {"key": "favorite_walk_routes", "icon": get_icon("walk"), "max_length": 1000, "mode": TextMode.TEXT},
    {"key": "gps_tracker_status", "icon": get_icon("gps"), "max_length": 255},
    {"key": "gps_tracker_config", "icon": get_icon("settings"), "max_length": 1000, "mode": TextMode.TEXT},
    {"key": "visitor_name", "icon": get_icon("visitor"), "max_length": 100},
    {"key": "visitor_instructions", "icon": get_icon("visitor"), "max_length": 500, "mode": TextMode.TEXT},
    {"key": "walk_history_today", "icon": get_icon("walk"), "max_length": 500, "mode": TextMode.TEXT},
    {"key": "activity_history", "icon": get_icon("statistics"), "max_length": 1000, "mode": TextMode.TEXT},
    {"key": "last_activity", "icon": get_icon("status"), "max_length": 255},
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the text platform."""
    coordinator: PawControlCoordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    dog_name = coordinator.dog_name

    entities = [
        PawControlTextEntity(coordinator, dog_name=dog_name, **cfg)
        for cfg in TEXT_ENTITIES
    ]

    async_add_entities(entities)

