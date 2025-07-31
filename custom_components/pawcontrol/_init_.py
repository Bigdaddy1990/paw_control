"""The Paw Control integration - SIMPLIFIED WORKING VERSION."""
from __future__ import annotations

import logging
from datetime import datetime
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_DOG_NAME

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Paw Control from a config entry."""
    _LOGGER.info("Setting up Paw Control for %s", entry.data[CONF_DOG_NAME])
    
    dog_name = entry.data[CONF_DOG_NAME]
    
    # Store entry data
    hass.data.setdefault(DOMAIN, {})
    
    # Create coordinator
    from .coordinator import PawControlCoordinator
    coordinator = PawControlCoordinator(hass, entry)
    
    # Store coordinator  
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "config": entry.data,
        "dog_name": dog_name,
    }
    
    # Create helper entities first
    await _create_helper_entities(hass, dog_name)
    
    # Wait a bit for entities to be created
    await asyncio.sleep(2)
    
    # Do initial coordinator update
    await coordinator.async_config_entry_first_refresh()
    
    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    _LOGGER.info("Paw Control setup completed for %s", dog_name)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading Paw Control for %s", entry.data[CONF_DOG_NAME])
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def _create_helper_entities(hass: HomeAssistant, dog_name: str) -> None:
    """Create the minimum required helper entities."""
    _LOGGER.info("Creating helper entities for %s", dog_name)
    
    # Essential input_boolean entities
    boolean_entities = [
        ("feeding_morning", "Frühstück gegeben", "mdi:food"),
        ("feeding_evening", "Abendessen gegeben", "mdi:food"),
        ("outside", "War draußen", "mdi:door-open"),
        ("walked_today", "Heute spaziert", "mdi:walk"),
        ("poop_done", "Geschäft gemacht", "mdi:toilet"),
        ("emergency_mode", "Notfallmodus", "mdi:alert"),
        ("visitor_mode", "Besuchsmodus", "mdi:account-group"),
    ]
    
    for suffix, friendly_name, icon in boolean_entities:
        entity_id = f"input_boolean.{dog_name}_{suffix}"
        if not hass.states.get(entity_id):
            try:
                await hass.services.async_call(
                    "input_boolean", "create",
                    {
                        "name": f"{dog_name} {friendly_name}",
                        "icon": icon,
                    },
                    blocking=True
                )
                await asyncio.sleep(0.1)
            except Exception as e:
                _LOGGER.debug("Could not create %s: %s", entity_id, e)
    
    # Essential counter entities
    counter_entities = [
        ("walk_count", "Spaziergänge", "mdi:walk"),
        ("outside_count", "Draußen Anzahl", "mdi:door-open"),
        ("feeding_count", "Fütterungen", "mdi:food"),
    ]
    
    for suffix, friendly_name, icon in counter_entities:
        entity_id = f"counter.{dog_name}_{suffix}"
        if not hass.states.get(entity_id):
            try:
                await hass.services.async_call(
                    "counter", "create",
                    {
                        "name": f"{dog_name} {friendly_name}",
                        "initial": 0,
                        "step": 1,
                        "icon": icon,
                    },
                    blocking=True
                )
                await asyncio.sleep(0.1)
            except Exception as e:
                _LOGGER.debug("Could not create %s: %s", entity_id, e)
    
    # Essential datetime entities
    datetime_entities = [
        ("last_walk", "Letzter Spaziergang", "mdi:walk"),
        ("last_outside", "Letztes Mal draußen", "mdi:door-open"),
        ("last_feeding", "Letzte Fütterung", "mdi:food"),
    ]
    
    for suffix, friendly_name, icon in datetime_entities:
        entity_id = f"input_datetime.{dog_name}_{suffix}"
        if not hass.states.get(entity_id):
            try:
                await hass.services.async_call(
                    "input_datetime", "create",
                    {
                        "name": f"{dog_name} {friendly_name}",
                        "has_date": True,
                        "has_time": True,
                        "icon": icon,
                    },
                    blocking=True
                )
                await asyncio.sleep(0.1)
            except Exception as e:
                _LOGGER.debug("Could not create %s: %s", entity_id, e)
    
    # Essential text entities
    text_entities = [
        ("notes", "Notizen", "mdi:note-text"),
        ("current_location", "Aktueller Standort", "mdi:map-marker"),
        ("health_notes", "Gesundheitsnotizen", "mdi:heart-pulse"),
    ]
    
    for suffix, friendly_name, icon in text_entities:
        entity_id = f"input_text.{dog_name}_{suffix}"
        if not hass.states.get(entity_id):
            try:
                await hass.services.async_call(
                    "input_text", "create",
                    {
                        "name": f"{dog_name} {friendly_name}",
                        "max": 255,
                        "icon": icon,
                    },
                    blocking=True
                )
                await asyncio.sleep(0.1)
            except Exception as e:
                _LOGGER.debug("Could not create %s: %s", entity_id, e)
    
    # Essential number entities
    number_entities = [
        ("weight", "Gewicht", 0.5, 100.0, 0.1, "kg", "mdi:weight-kilogram"),
        ("daily_walk_duration", "Tägliche Spaziergang Dauer", 0, 300, 1, "min", "mdi:walk"),
        ("gps_signal_strength", "GPS Signalstärke", 0, 100, 1, "%", "mdi:signal"),
    ]
    
    for suffix, friendly_name, min_val, max_val, step, unit, icon in number_entities:
        entity_id = f"input_number.{dog_name}_{suffix}"
        if not hass.states.get(entity_id):
            try:
                await hass.services.async_call(
                    "input_number", "create",
                    {
                        "name": f"{dog_name} {friendly_name}",
                        "min": min_val,
                        "max": max_val,
                        "step": step,
                        "unit_of_measurement": unit,
                        "icon": icon,
                    },
                    blocking=True
                )
                await asyncio.sleep(0.1)
            except Exception as e:
                _LOGGER.debug("Could not create %s: %s", entity_id, e)