"""The Paw Control integration - KOMPLETT REPARIERTE VERSION."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.exceptions import ServiceValidationError

from .const import (
    DOMAIN,
    CONF_DOG_NAME,
    CONF_DOG_BREED,
    CONF_DOG_AGE,
    CONF_DOG_WEIGHT,
    DEFAULT_DOG_WEIGHT,
    DEFAULT_DOG_AGE,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)

# Service Schemas - Vereinfacht
FEED_DOG_SCHEMA = vol.Schema({
    vol.Required("dog_name"): cv.string,
    vol.Optional("meal_type", default="morning"): vol.In(["morning", "lunch", "evening", "snack"]),
    vol.Optional("amount", default=100): vol.Range(min=10, max=1000),
})

START_WALK_SCHEMA = vol.Schema({
    vol.Required("dog_name"): cv.string,
    vol.Optional("walk_type", default="normal"): vol.In(["short", "normal", "long"]),
})

END_WALK_SCHEMA = vol.Schema({
    vol.Required("dog_name"): cv.string,
    vol.Optional("duration", default=30): vol.Range(min=1, max=300),
})

UPDATE_GPS_SCHEMA = vol.Schema({
    vol.Required("dog_name"): cv.string,
    vol.Required("latitude"): vol.Range(min=-90, max=90),
    vol.Required("longitude"): vol.Range(min=-180, max=180),
    vol.Optional("accuracy", default=10): vol.Range(min=1, max=1000),
})

HEALTH_CHECK_SCHEMA = vol.Schema({
    vol.Required("dog_name"): cv.string,
    vol.Optional("temperature"): vol.Range(min=35.0, max=42.0),
    vol.Optional("weight"): vol.Range(min=0.5, max=100.0),
    vol.Optional("notes"): cv.string,
})


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Paw Control integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Paw Control from a config entry."""
    _LOGGER.info("Setting up Paw Control for %s", entry.data[CONF_DOG_NAME])
    
    dog_name = entry.data[CONF_DOG_NAME]
    
    # Initialize coordinator
    from .coordinator import PawControlCoordinator
    coordinator = PawControlCoordinator(hass, entry)
    
    # Store coordinator
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "config": entry.data,
        "dog_name": dog_name,
    }
    
    try:
        # Wait for helper domains to be ready
        await _wait_for_helper_domains(hass)
        
        # Create helper entities
        await _create_helper_entities(hass, dog_name)
        
        # Wait for entities to be created
        await asyncio.sleep(2)
        
        # Setup platforms
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
        # Register services (only once)
        if not hass.data[DOMAIN].get("services_registered"):
            await _register_services(hass)
            hass.data[DOMAIN]["services_registered"] = True
        
        _LOGGER.info("✅ Paw Control setup completed for %s", dog_name)
        return True
        
    except Exception as e:
        _LOGGER.error("❌ Setup failed for %s: %s", dog_name, e)
        return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    dog_name = entry.data[CONF_DOG_NAME]
    _LOGGER.info("Unloading Paw Control for %s", dog_name)
    
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        
        # Unregister services if no more instances
        if not any(data for data in hass.data[DOMAIN].values() if isinstance(data, dict)):
            await _unregister_services(hass)
            hass.data[DOMAIN].pop("services_registered", None)
    
    return unload_ok


async def _wait_for_helper_domains(hass: HomeAssistant, timeout: int = 30) -> bool:
    """Wait for helper domains to be available."""
    required_domains = ["input_boolean", "counter", "input_datetime", "input_text", "input_number"]
    
    for _ in range(timeout):
        if all(hass.services.has_service(domain, "create") for domain in required_domains):
            return True
        await asyncio.sleep(1)
    
    _LOGGER.warning("Timeout waiting for helper domains")
    return False


async def _create_helper_entities(hass: HomeAssistant, dog_name: str) -> None:
    """Create helper entities for the dog."""
    _LOGGER.info("Creating helper entities for %s", dog_name)
    
    # Create essential input_boolean entities
    boolean_entities = [
        ("feeding_morning", "Frühstück", "mdi:weather-sunrise"),
        ("feeding_evening", "Abendessen", "mdi:weather-sunset"),
        ("outside", "War draußen", "mdi:door-open"),
        ("walked_today", "Heute spaziert", "mdi:walk"),
        ("poop_done", "Geschäft gemacht", "mdi:toilet"),
        ("emergency_mode", "Notfallmodus", "mdi:alert"),
        ("visitor_mode", "Besuchsmodus", "mdi:account-group"),
    ]
    
    for suffix, name, icon in boolean_entities:
        await _safe_create_entity(hass, "input_boolean", {
            "name": f"{dog_name.title()} {name}",
            "icon": icon,
        })
    
    # Create essential counter entities
    counter_entities = [
        ("walk_count", "Spaziergänge", "mdi:walk"),
        ("outside_count", "Draußen Anzahl", "mdi:door-open"),
        ("feeding_count", "Fütterungen", "mdi:food"),
    ]
    
    for suffix, name, icon in counter_entities:
        await _safe_create_entity(hass, "counter", {
            "name": f"{dog_name.title()} {name}",
            "initial": 0,
            "step": 1,
            "icon": icon,
        })
    
    # Create essential datetime entities
    datetime_entities = [
        ("last_walk", "Letzter Spaziergang", "mdi:walk"),
        ("last_outside", "Letztes Mal draußen", "mdi:door-open"),
        ("last_feeding", "Letzte Fütterung", "mdi:food"),
    ]
    
    for suffix, name, icon in datetime_entities:
        await _safe_create_entity(hass, "input_datetime", {
            "name": f"{dog_name.title()} {name}",
            "has_date": True,
            "has_time": True,
            "icon": icon,
        })
    
    # Create essential text entities
    text_entities = [
        ("notes", "Notizen", "mdi:note-text"),
        ("current_location", "Aktueller Standort", "mdi:map-marker"),
        ("health_notes", "Gesundheitsnotizen", "mdi:heart-pulse"),
    ]
    
    for suffix, name, icon in text_entities:
        await _safe_create_entity(hass, "input_text", {
            "name": f"{dog_name.title()} {name}",
            "max": 255,
            "icon": icon,
        })
    
    # Create essential number entities
    number_entities = [
        ("weight", "Gewicht", 0.5, 100.0, 0.1, "kg", "mdi:weight-kilogram"),
        ("daily_walk_duration", "Tägliche Spaziergang Dauer", 0, 300, 1, "min", "mdi:walk"),
        ("gps_signal_strength", "GPS Signalstärke", 0, 100, 1, "%", "mdi:signal"),
    ]
    
    for suffix, name, min_val, max_val, step, unit, icon in number_entities:
        await _safe_create_entity(hass, "input_number", {
            "name": f"{dog_name.title()} {name}",
            "min": min_val,
            "max": max_val,
            "step": step,
            "unit_of_measurement": unit,
            "icon": icon,
        })
    
    _LOGGER.info("✅ Helper entities created for %s", dog_name)


async def _safe_create_entity(hass: HomeAssistant, domain: str, data: dict) -> bool:
    """Safely create an entity."""
    try:
        await hass.services.async_call(domain, "create", data, blocking=True)
        await asyncio.sleep(0.1)  # Small delay
        return True
    except Exception as e:
        _LOGGER.debug("Entity creation failed: %s", e)
        return False


async def _register_services(hass: HomeAssistant) -> None:
    """Register Paw Control services."""
    _LOGGER.info("Registering Paw Control services")
    
    async def feed_dog_service(call: ServiceCall) -> None:
        """Handle feed dog service."""
        dog_name = call.data.get("dog_name")
        meal_type = call.data.get("meal_type", "morning")
        amount = call.data.get("amount", 100)
        
        try:
            # Set feeding boolean
            entity_id = f"input_boolean.{dog_name}_feeding_{meal_type}"
            await hass.services.async_call("input_boolean", "turn_on", {"entity_id": entity_id})
            
            # Update counter
            counter_id = f"counter.{dog_name}_feeding_count"
            await hass.services.async_call("counter", "increment", {"entity_id": counter_id})
            
            # Update last feeding
            datetime_id = f"input_datetime.{dog_name}_last_feeding"
            await hass.services.async_call("input_datetime", "set_datetime", {
                "entity_id": datetime_id,
                "datetime": datetime.now().isoformat()
            })
            
            _LOGGER.info("Fed %s: %s (%dg)", dog_name, meal_type, amount)
            
        except Exception as e:
            _LOGGER.error("Feed dog service failed: %s", e)
    
    async def start_walk_service(call: ServiceCall) -> None:
        """Handle start walk service."""
        dog_name = call.data.get("dog_name")
        walk_type = call.data.get("walk_type", "normal")
        
        try:
            # Set outside
            await hass.services.async_call("input_boolean", "turn_on", {
                "entity_id": f"input_boolean.{dog_name}_outside"
            })
            
            # Update last walk
            await hass.services.async_call("input_datetime", "set_datetime", {
                "entity_id": f"input_datetime.{dog_name}_last_walk",
                "datetime": datetime.now().isoformat()
            })
            
            _LOGGER.info("Started walk for %s: %s", dog_name, walk_type)
            
        except Exception as e:
            _LOGGER.error("Start walk service failed: %s", e)
    
    async def end_walk_service(call: ServiceCall) -> None:
        """Handle end walk service."""
        dog_name = call.data.get("dog_name")
        duration = call.data.get("duration", 30)
        
        try:
            # Set walked today
            await hass.services.async_call("input_boolean", "turn_on", {
                "entity_id": f"input_boolean.{dog_name}_walked_today"
            })
            
            # Increment walk counter
            await hass.services.async_call("counter", "increment", {
                "entity_id": f"counter.{dog_name}_walk_count"
            })
            
            # Update duration
            await hass.services.async_call("input_number", "set_value", {
                "entity_id": f"input_number.{dog_name}_daily_walk_duration",
                "value": duration
            })
            
            _LOGGER.info("Ended walk for %s: %d minutes", dog_name, duration)
            
        except Exception as e:
            _LOGGER.error("End walk service failed: %s", e)
    
    async def update_gps_service(call: ServiceCall) -> None:
        """Handle GPS update service."""
        dog_name = call.data.get("dog_name")
        latitude = call.data.get("latitude")
        longitude = call.data.get("longitude")
        accuracy = call.data.get("accuracy", 10)
        
        try:
            # Update location
            location_str = f"{latitude:.6f},{longitude:.6f}"
            await hass.services.async_call("input_text", "set_value", {
                "entity_id": f"input_text.{dog_name}_current_location",
                "value": location_str
            })
            
            # Update signal strength
            signal_strength = max(0, min(100, 100 - accuracy))
            await hass.services.async_call("input_number", "set_value", {
                "entity_id": f"input_number.{dog_name}_gps_signal_strength",
                "value": signal_strength
            })
            
            _LOGGER.info("Updated GPS for %s: %s,%s", dog_name, latitude, longitude)
            
        except Exception as e:
            _LOGGER.error("GPS update service failed: %s", e)
    
    async def health_check_service(call: ServiceCall) -> None:
        """Handle health check service."""
        dog_name = call.data.get("dog_name")
        temperature = call.data.get("temperature")
        weight = call.data.get("weight")
        notes = call.data.get("notes", "")
        
        try:
            # Update weight if provided
            if weight:
                await hass.services.async_call("input_number", "set_value", {
                    "entity_id": f"input_number.{dog_name}_weight",
                    "value": weight
                })
            
            # Update health notes
            if notes:
                timestamp = datetime.now().strftime("%H:%M")
                health_note = f"[{timestamp}] {notes}"
                await hass.services.async_call("input_text", "set_value", {
                    "entity_id": f"input_text.{dog_name}_health_notes",
                    "value": health_note
                })
            
            _LOGGER.info("Health check completed for %s", dog_name)
            
        except Exception as e:
            _LOGGER.error("Health check service failed: %s", e)
    
    async def daily_reset_service(call: ServiceCall) -> None:
        """Handle daily reset service."""
        dog_name = call.data.get("dog_name")
        
        try:
            # Reset boolean entities
            boolean_entities = [
                f"input_boolean.{dog_name}_feeding_morning",
                f"input_boolean.{dog_name}_feeding_evening",
                f"input_boolean.{dog_name}_outside",
                f"input_boolean.{dog_name}_walked_today",
                f"input_boolean.{dog_name}_poop_done",
            ]
            
            for entity_id in boolean_entities:
                if hass.states.get(entity_id):
                    await hass.services.async_call("input_boolean", "turn_off", {"entity_id": entity_id})
            
            # Reset counters
            counter_entities = [
                f"counter.{dog_name}_walk_count",
                f"counter.{dog_name}_outside_count",
                f"counter.{dog_name}_feeding_count",
            ]
            
            for entity_id in counter_entities:
                if hass.states.get(entity_id):
                    await hass.services.async_call("counter", "reset", {"entity_id": entity_id})
            
            _LOGGER.info("Daily reset completed for %s", dog_name)
            
        except Exception as e:
            _LOGGER.error("Daily reset service failed: %s", e)
    
    # Register services
    services = [
        ("feed_dog", feed_dog_service, FEED_DOG_SCHEMA),
        ("start_walk", start_walk_service, START_WALK_SCHEMA),
        ("end_walk", end_walk_service, END_WALK_SCHEMA),
        ("update_gps", update_gps_service, UPDATE_GPS_SCHEMA),
        ("health_check", health_check_service, HEALTH_CHECK_SCHEMA),
        ("daily_reset", daily_reset_service, vol.Schema({
            vol.Required("dog_name"): cv.string,
        })),
    ]
    
    for service_name, service_func, schema in services:
        hass.services.async_register(DOMAIN, service_name, service_func, schema)
        _LOGGER.debug("Registered service: %s", service_name)
    
    _LOGGER.info("✅ All services registered")


async def _unregister_services(hass: HomeAssistant) -> None:
    """Unregister all services."""
    services = ["feed_dog", "start_walk", "end_walk", "update_gps", "health_check", "daily_reset"]
    
    for service_name in services:
        if hass.services.has_service(DOMAIN, service_name):
            hass.services.async_remove(DOMAIN, service_name)
    
    _LOGGER.info("Services unregistered")
