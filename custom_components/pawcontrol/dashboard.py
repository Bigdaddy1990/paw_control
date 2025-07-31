"""Dashboard-Generator für Paw Control – erstellt eine Dashboard-Vorlage als YAML im System."""

from .const import *

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
