"""Generate simple dashboard definitions for Paw Control."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .utils import generate_entity_id

_LOGGER = logging.getLogger(__name__)


async def create_dashboard(hass: HomeAssistant, dog_name: str) -> None:
    """Create a Lovelace dashboard definition and store it in a sensor."""

    dog_slug_health = generate_entity_id(dog_name, "sensor", "health")
    dog_slug_last_walk = generate_entity_id(dog_name, "sensor", "last_walk")
    dog_slug_gps_location = generate_entity_id(dog_name, "sensor", "gps_location")
    dog_slug_walks = generate_entity_id(dog_name, "counter", "walks")
    dog_slug_walk_active = generate_entity_id(
        dog_name, "input_boolean", "walk_active"
    )
    dog_slug_gps_active = generate_entity_id(dog_name, "input_boolean", "gps_active")
    dog_slug_push_active = generate_entity_id(dog_name, "input_boolean", "push_active")
    dog_slug_symptoms = generate_entity_id(dog_name, "input_text", "symptoms")
    dog_slug_medication = generate_entity_id(dog_name, "input_text", "medication")
    dog_slug_weight = generate_entity_id(dog_name, "input_number", "weight")

    dashboard_yaml = f"""
title: 🐾 Paw Control: {dog_name}
views:
  - title: Übersicht
    cards:
      - type: custom:mushroom-entity-card
        entity: {dog_slug_health}
        name: Gesundheit
      - type: custom:mushroom-entity-card
        entity: {dog_slug_last_walk}
        name: Letztes Gassi
      - type: custom:mushroom-entity-card
        entity: {dog_slug_gps_location}
        name: GPS-Position
      - type: custom:mushroom-entity-card
        entity: {dog_slug_walks}
        name: Spaziergänge gesamt
      - type: custom:mushroom-entity-card
        entity: {dog_slug_walk_active}
        name: Gerade Gassi?
      - type: custom:mushroom-entity-card
        entity: {dog_slug_gps_active}
        name: GPS aktiv?
      - type: custom:mushroom-entity-card
        entity: {dog_slug_push_active}
        name: Push aktiviert?
      - type: custom:mushroom-entity-card
        entity: {dog_slug_symptoms}
        name: Symptome
      - type: custom:mushroom-entity-card
        entity: {dog_slug_medication}
        name: Medikamente
      - type: custom:mushroom-entity-card
        entity: {dog_slug_weight}
        name: Gewicht (kg)
    """

    # Store the YAML definition in a sensor for the user to copy into Lovelace
    dashboard_sensor_id = generate_entity_id(dog_name, "sensor", "dashboard_yaml")
    hass.states.async_set(
        dashboard_sensor_id,
        dashboard_yaml,
        {"friendly_name": f"{dog_name} Dashboard-Vorlage (Kopieren für Lovelace)"},
    )

DEFAULT_DASHBOARD_NAME = "PawControl"

MODULE_CARDS = {
    "gps": {
        "type": "map",
        "entities": ["device_tracker.paw_control_gps"],
        "title": "GPS-Tracking"
    },
    "health": {
        "type": "entities",
        "entities": [
            "sensor.paw_control_health_status",
            "sensor.paw_control_last_checkup"
        ],
        "title": "Gesundheit"
    },
    "walk": {
        "type": "history-graph",
        "entities": [
            "sensor.paw_control_last_walk",
            "sensor.paw_control_walk_count"
        ],
        "title": "Gassi"
    }
}

async def async_create_dashboard(hass: HomeAssistant, entry: ConfigEntry):
    modules = entry.options.get("modules", ["gps"])
    cards = []
    for module in modules:
        card = MODULE_CARDS.get(module)
        if card:
            cards.append(card)
    if not cards:
        _LOGGER.warning("No module cards selected for dashboard generation.")
        return
    view = {
        "title": DEFAULT_DASHBOARD_NAME,
        "path": "pawcontrol",
        "icon": "mdi:paw",
        "cards": cards
    }
    _LOGGER.info(f"Generated PawControl dashboard: {view}")
    return view

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    await async_create_dashboard(hass, entry)
    return True
