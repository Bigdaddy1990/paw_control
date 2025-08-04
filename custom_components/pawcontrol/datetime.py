"""Datetime platform for Paw Control integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import PawControlCoordinator
from .entities import PawControlDateTimeEntity
from .helpers.entity import get_icon

_LOGGER = logging.getLogger(__name__)


DATETIME_ENTITIES: list[dict] = [
    {"key": "last_feeding_morning"},
    {"key": "last_feeding_lunch"},
    {"key": "last_feeding_evening"},
    {"key": "last_feeding"},
    {"key": "feeding_morning_time", "has_date": False},
    {"key": "feeding_lunch_time", "has_date": False},
    {"key": "feeding_evening_time", "has_date": False},
    {"key": "last_walk", "icon": get_icon("walk")},
    {"key": "last_outside"},
    {"key": "last_play"},
    {"key": "last_training", "icon": get_icon("training")},
    {"key": "last_grooming", "icon": get_icon("grooming")},
    {"key": "last_activity"},
    {"key": "last_vet_visit", "icon": get_icon("vet")},
    {"key": "next_vet_appointment", "icon": get_icon("vet")},
    {"key": "last_medication", "icon": get_icon("medication")},
    {"key": "last_weight_check", "icon": get_icon("weight")},
    {"key": "visitor_start"},
    {"key": "visitor_end"},
    {"key": "emergency_contact_time", "icon": get_icon("emergency")},
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the datetime platform."""
    coordinator: PawControlCoordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    dog_name = coordinator.dog_name

    entities = [
        PawControlDateTimeEntity(coordinator, dog_name=dog_name, **cfg)
        for cfg in DATETIME_ENTITIES
    ]

    async_add_entities(entities)

