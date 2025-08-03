"""Dashboard-Generator für Paw Control – erstellt eine Dashboard-Vorlage als YAML im System."""
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import *
import logging

_LOGGER = logging.getLogger(__name__)

async def create_dashboard(hass, dog_name):
    """Erstellt ein Lovelace-Dashboard als YAML (Sensor), das alle aktiven Module abbildet."""

    dashboard_yaml = f"""
title: 🐾 Paw Control: {dog_name}
views:
  - title: Übersicht
    cards:
      - type: custom:mushroom-entity-card
        entity: sensor.{dog_name}_health
        name: Gesundheit
      - type: custom:mushroom-entity-card
        entity: sensor.{dog_name}_last_walk
        name: Letztes Gassi
      - type: custom:mushroom-entity-card
        entity: sensor.{dog_name}_gps_location
        name: GPS-Position
      - type: custom:mushroom-entity-card
        entity: counter.{dog_name}_walks
        name: Spaziergänge gesamt
      - type: custom:mushroom-entity-card
        entity: input_boolean.{dog_name}_walk_active
        name: Gerade Gassi?
      - type: custom:mushroom-entity-card
        entity: input_boolean.{dog_name}_gps_active
        name: GPS aktiv?
      - type: custom:mushroom-entity-card
        entity: input_boolean.{dog_name}_push_active
        name: Push aktiviert?
      - type: custom:mushroom-entity-card
        entity: input_text.{dog_name}_symptoms
        name: Symptome
      - type: custom:mushroom-entity-card
        entity: input_text.{dog_name}_medication
        name: Medikamente
      - type: custom:mushroom-entity-card
        entity: input_number.{dog_name}_weight
        name: Gewicht (kg)
    """

    # Speichert das YAML als "Sensor", damit der User es auslesen/kopieren kann
    dashboard_sensor_id = f"sensor.{dog_name}_dashboard_yaml"
    hass.states.async_set(
        dashboard_sensor_id,
        dashboard_yaml,
        {"friendly_name": f"{dog_name} Dashboard-Vorlage (Kopieren für Lovelace)"}
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
