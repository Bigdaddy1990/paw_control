"""Dashboard creation for Paw Control."""
from __future__ import annotations

import logging
import os
from typing import Any

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


async def async_create_dashboard(hass: HomeAssistant, dog_name: str) -> None:
    """Create a comprehensive dashboard for the dog system."""
    
    try:
        # Generate main dashboard
        main_dashboard = _generate_main_dashboard(dog_name)
        await _save_dashboard(hass, f"paw_control_{dog_name}", main_dashboard)
        
        # Create mobile dashboard (simplified)
        mobile_dashboard = _generate_mobile_dashboard(dog_name)
        await _save_dashboard(hass, f"paw_control_{dog_name}_mobile", mobile_dashboard)
        
        _LOGGER.info("Dashboards created successfully for %s", dog_name)
        
    except Exception as e:
        _LOGGER.error("Failed to create dashboards for %s: %s", dog_name, e)
        raise


def _generate_main_dashboard(dog_name: str) -> str:
    """Generate the main comprehensive dashboard."""
    
    return f"""# 🐶 Paw Control Dashboard für {dog_name.title()}
# Automatisch generiert von der Paw Control Integration

title: "🐶 {dog_name.title()} - Paw Control"
theme: Backend-selected

views:
  - title: Übersicht
    path: overview
    icon: mdi:dog
    cards:
      # Header Card mit Hundestatus
      - type: custom:mushroom-template-card
        primary: "{dog_name.title()}"
        secondary: "Mein treuer Begleiter"
        icon: mdi:dog
        icon_color: blue
        
      # Fütterungsbereich
      - type: custom:mushroom-title-card
        title: "🍽️ Fütterung"
        
      - type: horizontal-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: sensor.{dog_name}_last_fed
            name: "Letzte Fütterung"
            icon: mdi:food-drumstick
            
          - type: custom:mushroom-entity-card
            entity: sensor.{dog_name}_next_feeding
            name: "Nächste Fütterung"
            icon: mdi:clock-outline
            
      # Aktivitäten
      - type: custom:mushroom-title-card
        title: "🚶 Aktivitäten"
        
      - type: horizontal-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: sensor.{dog_name}_last_walk
            name: "Letzter Spaziergang"
            icon: mdi:walk
            
          - type: custom:mushroom-entity-card
            entity: sensor.{dog_name}_activity_level
            name: "Aktivitätslevel"
            icon: mdi:speedometer
            
      # Gesundheit
      - type: custom:mushroom-title-card
        title: "🏥 Gesundheit"
        
      - type: horizontal-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: sensor.{dog_name}_health_status
            name: "Gesundheitsstatus"
            icon: mdi:heart-pulse
            
          - type: custom:mushroom-entity-card
            entity: sensor.{dog_name}_weight_tracking
            name: "Gewicht"
            icon: mdi:scale-bathroom
            
      # Schnellaktionen
      - type: custom:mushroom-title-card
        title: "⚡ Schnellaktionen"
        
      - type: horizontal-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: button.{dog_name}_feed
            name: "Füttern"
            icon: mdi:food-drumstick
            tap_action:
              action: call-service
              service: button.press
              target:
                entity_id: button.{dog_name}_feed
                
          - type: custom:mushroom-entity-card
            entity: button.{dog_name}_start_walk
            name: "Gassi starten"
            icon: mdi:walk
            tap_action:
              action: call-service
              service: button.press
              target:
                entity_id: button.{dog_name}_start_walk

  - title: Statistiken
    path: statistics
    icon: mdi:chart-line
    cards:
      - type: custom:mushroom-title-card
        title: "📊 Statistiken"
        
      - type: entities
        title: "Heute"
        entities:
          - sensor.{dog_name}_daily_food_amount
          - sensor.{dog_name}_playtime_today
          - sensor.{dog_name}_training_sessions
          - sensor.{dog_name}_feeding_streak
          - sensor.{dog_name}_walk_streak
          
  - title: Gesundheit
    path: health
    icon: mdi:heart-pulse
    cards:
      - type: custom:mushroom-title-card
        title: "❤️ Gesundheit & Wohlbefinden"
        
      - type: entities
        title: "Gesundheitsdaten"
        entities:
          - sensor.{dog_name}_health_status
          - sensor.{dog_name}_weight_tracking
          - sensor.{dog_name}_mood
          - binary_sensor.{dog_name}_is_sick
          - binary_sensor.{dog_name}_is_stressed
"""


def _generate_mobile_dashboard(dog_name: str) -> str:
    """Generate a simplified mobile dashboard."""
    
    return f"""# 📱 Mobile Dashboard für {dog_name.title()}

title: "📱 {dog_name.title()}"
theme: Backend-selected

views:
  - title: Home
    path: mobile_home
    icon: mdi:home
    cards:
      - type: custom:mushroom-template-card
        primary: "{dog_name.title()}"
        secondary: "Schnellzugriff"
        icon: mdi:dog
        icon_color: blue
        
      # Quick Actions Grid
      - type: grid
        columns: 2
        square: true
        cards:
          - type: custom:mushroom-entity-card
            entity: button.{dog_name}_feed
            name: "Füttern"
            icon: mdi:food-drumstick
            
          - type: custom:mushroom-entity-card
            entity: button.{dog_name}_start_walk
            name: "Gassi"
            icon: mdi:walk
            
          - type: custom:mushroom-entity-card
            entity: button.{dog_name}_start_playtime
            name: "Spielen"
            icon: mdi:tennis
            
          - type: custom:mushroom-entity-card
            entity: button.{dog_name}_health_check
            name: "Gesundheit"
            icon: mdi:heart-pulse
"""


async def _save_dashboard(hass: HomeAssistant, filename: str, content: str) -> None:
    """Save dashboard to file."""
    
    def _write_dashboard_file(path: str, content: str) -> None:
        """Write dashboard file synchronously."""
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    
    dashboard_path = hass.config.path("dashboards")
    dashboard_file = os.path.join(dashboard_path, f"{filename}.yaml")
    
    try:
        await hass.async_add_executor_job(_write_dashboard_file, dashboard_file, content)
        _LOGGER.info("Dashboard saved: %s", dashboard_file)
        
    except Exception as e:
        _LOGGER.error("Failed to save dashboard %s: %s", dashboard_file, e)
        raise
