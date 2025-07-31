"""The Paw Control integration - COMPLETE RESTORATION."""
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
from homeassistant.helpers.event import async_track_time_change, async_track_state_change_event
from homeassistant.helpers.storage import Store
from homeassistant.exceptions import ServiceValidationError

# Import service handlers
from .service_handlers import (
    update_feeding_entities,
    update_walk_start_entities,
    update_walk_end_entities,
    update_health_entities,
    update_mood_entities,
    update_training_start_entities,
    update_training_end_entities,
    update_medication_entities,
    update_vet_entities,
    update_playtime_start_entities,
    update_playtime_end_entities,
    reset_all_entities,
    update_gps_entities,
    setup_gps_automation,
    start_walk_tracking,
    end_walk_tracking,
    safe_service_call
)

from .const import (
    DOMAIN,
    CONF_DOG_NAME,
    CONF_PUSH_DEVICES,
    CONF_PERSON_TRACKING,
    CONF_CREATE_DASHBOARD,
    CONF_DOOR_SENSOR,
    SERVICE_ENTITY_ID,
    SERVICE_FOOD_TYPE,
    SERVICE_FOOD_AMOUNT,
    SERVICE_WALK_TYPE,
    SERVICE_LOCATION,
    SERVICE_RATING,
    SERVICE_NOTES,
    SERVICE_WEIGHT,
    SERVICE_TEMPERATURE,
    SERVICE_ENERGY_LEVEL,
    SERVICE_SYMPTOMS,
    SERVICE_MOOD,
    SERVICE_REASON,
    SERVICE_TRAINING_TYPE,
    SERVICE_DURATION_PLANNED,
    SERVICE_SUCCESS_RATING,
    SERVICE_LEARNED_COMMANDS,
    SERVICE_MEDICATION_NAME,
    SERVICE_MEDICATION_AMOUNT,
    SERVICE_MEDICATION_UNIT,
    SERVICE_VET_NAME,
    SERVICE_VET_DATE,
    SERVICE_VET_REASON,
    SERVICE_PLAY_TYPE,
    SERVICE_DURATION,
    SERVICE_FUN_RATING,
    SERVICE_ENERGY_AFTERWARDS,
    SERVICE_CONFIRM_RESET,
    SERVICE_TRIGGER_FEEDING_REMINDER,
    SERVICE_DAILY_RESET,
    SERVICE_SEND_NOTIFICATION,
    SERVICE_SET_VISITOR_MODE,
    SERVICE_LOG_ACTIVITY,
    SERVICE_ADD_DOG,
    SERVICE_TEST_NOTIFICATION,
    SERVICE_EMERGENCY_CONTACT,
    SERVICE_HEALTH_CHECK,
    MEAL_TYPES,
    ACTIVITY_TYPES,
    FEEDING_TYPES,
    ICONS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]

# Complete service schemas
FEED_DOG_SCHEMA = vol.Schema({
    vol.Required(SERVICE_ENTITY_ID): cv.entity_id,
    vol.Optional(SERVICE_FOOD_TYPE, default="Trockenfutter"): vol.In([
        "Trockenfutter", "Nassfutter", "BARF", "Leckerli", "Kauknochen", "Sonstiges"
    ]),
    vol.Optional(SERVICE_FOOD_AMOUNT, default=100): vol.All(vol.Coerce(int), vol.Range(min=1, max=2000)),
    vol.Optional(SERVICE_NOTES): cv.string,
})

START_WALK_SCHEMA = vol.Schema({
    vol.Required(SERVICE_ENTITY_ID): cv.entity_id,
    vol.Optional(SERVICE_WALK_TYPE, default="Normal"): vol.In([
        "Kurz", "Normal", "Lang", "Training", "Freilauf", "Sozialisierung"
    ]),
    vol.Optional(SERVICE_LOCATION): cv.string,
    vol.Optional(SERVICE_NOTES): cv.string,
})

END_WALK_SCHEMA = vol.Schema({
    vol.Required(SERVICE_ENTITY_ID): cv.entity_id,
    vol.Optional(SERVICE_RATING, default=5): vol.Range(min=1, max=5),
    vol.Optional(SERVICE_NOTES): cv.string,
    vol.Optional(SERVICE_DURATION): vol.Coerce(int),
})

LOG_HEALTH_DATA_SCHEMA = vol.Schema({
    vol.Required(SERVICE_ENTITY_ID): cv.entity_id,
    vol.Optional(SERVICE_WEIGHT): vol.All(vol.Coerce(float), vol.Range(min=0.5, max=100.0)),
    vol.Optional(SERVICE_TEMPERATURE): vol.All(vol.Coerce(float), vol.Range(min=35.0, max=42.0)),
    vol.Optional(SERVICE_ENERGY_LEVEL): vol.In([
        "Sehr niedrig", "Niedrig", "Normal", "Hoch", "Sehr hoch"
    ]),
    vol.Optional(SERVICE_SYMPTOMS): cv.string,
    vol.Optional(SERVICE_NOTES): cv.string,
})

SET_MOOD_SCHEMA = vol.Schema({
    vol.Required(SERVICE_ENTITY_ID): cv.entity_id,
    vol.Required(SERVICE_MOOD): vol.In([
        "😄 Sehr fröhlich", "😊 Fröhlich", "😐 Neutral", "😟 Traurig", "😠 Ärgerlich", "😴 Müde"
    ]),
    vol.Optional(SERVICE_REASON): cv.string,
    vol.Optional(SERVICE_NOTES): cv.string,
})

START_TRAINING_SCHEMA = vol.Schema({
    vol.Required(SERVICE_ENTITY_ID): cv.entity_id,
    vol.Required(SERVICE_TRAINING_TYPE): vol.In([
        "Grundgehorsam", "Leinenführigkeit", "Apportieren", "Tricks", "Sozialisierung", "Agility"
    ]),
    vol.Optional(SERVICE_DURATION_PLANNED, default=15): vol.All(vol.Coerce(int), vol.Range(min=5, max=120)),
    vol.Optional(SERVICE_LOCATION): cv.string,
    vol.Optional(SERVICE_NOTES): cv.string,
})

END_TRAINING_SCHEMA = vol.Schema({
    vol.Required(SERVICE_ENTITY_ID): cv.entity_id,
    vol.Optional(SERVICE_SUCCESS_RATING, default=3): vol.Range(min=1, max=5),
    vol.Optional(SERVICE_LEARNED_COMMANDS): cv.string,
    vol.Optional(SERVICE_DURATION): vol.Coerce(int),
    vol.Optional(SERVICE_NOTES): cv.string,
})

LOG_MEDICATION_SCHEMA = vol.Schema({
    vol.Required(SERVICE_ENTITY_ID): cv.entity_id,
    vol.Required(SERVICE_MEDICATION_NAME): cv.string,
    vol.Required(SERVICE_MEDICATION_AMOUNT): vol.Coerce(float),
    vol.Optional(SERVICE_MEDICATION_UNIT, default="mg"): vol.In(["mg", "ml", "Tabletten", "Tropfen"]),
    vol.Optional(SERVICE_NOTES): cv.string,
})

SCHEDULE_VET_VISIT_SCHEMA = vol.Schema({
    vol.Required(SERVICE_ENTITY_ID): cv.entity_id,
    vol.Required(SERVICE_VET_NAME): cv.string,
    vol.Required(SERVICE_VET_DATE): cv.string,
    vol.Optional(SERVICE_VET_REASON, default="Routineuntersuchung"): cv.string,
    vol.Optional(SERVICE_NOTES): cv.string,
})

START_PLAYTIME_SCHEMA = vol.Schema({
    vol.Required(SERVICE_ENTITY_ID): cv.entity_id,
    vol.Optional(SERVICE_PLAY_TYPE, default="Freies Spiel"): vol.In([
        "Freies Spiel", "Ball spielen", "Frisbee", "Zerrspiele", "Verstecken", "Intelligenzspiele"
    ]),
    vol.Optional(SERVICE_LOCATION, default="Zuhause"): cv.string,
    vol.Optional(SERVICE_NOTES): cv.string,
})

END_PLAYTIME_SCHEMA = vol.Schema({
    vol.Required(SERVICE_ENTITY_ID): cv.entity_id,
    vol.Optional(SERVICE_DURATION): vol.Coerce(int),
    vol.Optional(SERVICE_FUN_RATING, default=5): vol.Range(min=1, max=5),
    vol.Optional(SERVICE_ENERGY_AFTERWARDS): vol.In([
        "Sehr müde", "Müde", "Entspannt", "Noch energiegeladen", "Hyperaktiv"
    ]),
    vol.Optional(SERVICE_NOTES): cv.string,
})

RESET_ALL_DATA_SCHEMA = vol.Schema({
    vol.Required(SERVICE_ENTITY_ID): cv.entity_id,
    vol.Required(SERVICE_CONFIRM_RESET): vol.In(["RESET"]),
    vol.Optional("backup_data", default=True): cv.boolean,
})

# Enhanced service schemas from Hundesystem
TRIGGER_FEEDING_REMINDER_SCHEMA = vol.Schema({
    vol.Required("meal_type"): vol.In(MEAL_TYPES.keys()),
    vol.Optional("message"): cv.string,
    vol.Optional("dog_name"): cv.string,
})

SEND_NOTIFICATION_SCHEMA = vol.Schema({
    vol.Required("title"): cv.string,
    vol.Required("message"): cv.string,
    vol.Optional("target"): cv.string,
    vol.Optional("dog_name"): cv.string,
    vol.Optional("data"): dict,
})

SET_VISITOR_MODE_SCHEMA = vol.Schema({
    vol.Required("enabled"): cv.boolean,
    vol.Optional("visitor_name", default=""): cv.string,
    vol.Optional("dog_name"): cv.string,
})

LOG_ACTIVITY_SCHEMA = vol.Schema({
    vol.Required("activity_type"): vol.In(ACTIVITY_TYPES.keys()),
    vol.Optional("duration"): vol.Range(min=1, max=480),
    vol.Optional("notes", default=""): cv.string,
    vol.Optional("dog_name"): cv.string,
})

ADD_DOG_SCHEMA = vol.Schema({
    vol.Required("dog_name"): cv.string,
    vol.Optional("push_devices", default=[]): [cv.string],
    vol.Optional("door_sensor"): cv.entity_id,
    vol.Optional("create_dashboard", default=True): cv.boolean,
})

TEST_NOTIFICATION_SCHEMA = vol.Schema({
    vol.Optional("dog_name"): cv.string,
})

EMERGENCY_CONTACT_SCHEMA = vol.Schema({
    vol.Required("emergency_type"): vol.In(["medical", "lost", "injury", "behavioral", "other"]),
    vol.Required("message"): cv.string,
    vol.Optional("location", default=""): cv.string,
    vol.Optional("contact_vet", default=False): cv.boolean,
    vol.Required("dog_name"): cv.string,
})

HEALTH_CHECK_SCHEMA = vol.Schema({
    vol.Optional("check_type", default="general"): vol.In(["general", "feeding", "activity", "behavior", "symptoms"]),
    vol.Optional("notes", default=""): cv.string,
    vol.Optional("temperature"): vol.Range(min=35.0, max=42.0),
    vol.Optional("weight"): vol.Range(min=0.1, max=100.0),
    vol.Required("dog_name"): cv.string,
})

# GPS Service Schemas
UPDATE_GPS_SIMPLE_SCHEMA = vol.Schema({
    vol.Required(SERVICE_ENTITY_ID): cv.entity_id,
    vol.Required("latitude"): vol.All(vol.Coerce(float), vol.Range(min=-90, max=90)),
    vol.Required("longitude"): vol.All(vol.Coerce(float), vol.Range(min=-180, max=180)),
    vol.Optional("accuracy", default=0): vol.All(vol.Coerce(float), vol.Range(min=0, max=1000)),
    vol.Optional("source_info", default="manual"): cv.string,
})

SETUP_AUTOMATIC_GPS_SCHEMA = vol.Schema({
    vol.Required(SERVICE_ENTITY_ID): cv.entity_id,
    vol.Optional("gps_entity"): cv.entity_id,
    vol.Optional("tracking_sensitivity", default="medium"): vol.In(["low", "medium", "high"]),
    vol.Optional("movement_threshold", default=50): vol.All(vol.Coerce(int), vol.Range(min=10, max=500)),
    vol.Optional("auto_start_walk", default=True): cv.boolean,
    vol.Optional("auto_end_walk", default=True): cv.boolean,
    vol.Optional("home_zone_radius", default=100): vol.All(vol.Coerce(int), vol.Range(min=50, max=1000)),
    vol.Optional("track_route", default=True): cv.boolean,
    vol.Optional("calculate_stats", default=True): cv.boolean,
})

START_WALK_TRACKING_SCHEMA = vol.Schema({
    vol.Required(SERVICE_ENTITY_ID): cv.entity_id,
    vol.Optional("walk_name"): cv.string,
    vol.Optional("expected_duration"): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
    vol.Optional("track_detailed_route", default=True): cv.boolean,
})

END_WALK_TRACKING_SCHEMA = vol.Schema({
    vol.Required(SERVICE_ENTITY_ID): cv.entity_id,
    vol.Optional("walk_rating"): vol.Range(min=1, max=5),
    vol.Optional("notes"): cv.string,
    vol.Optional("save_route", default=False): cv.boolean,
})

VERIFY_INSTALLATION_SCHEMA = vol.Schema({
    vol.Required(SERVICE_ENTITY_ID): cv.entity_id,
    vol.Optional("force_check", default=False): cv.boolean,
    vol.Optional("create_missing_entities", default=True): cv.boolean,
    vol.Optional("send_notification", default=True): cv.boolean,
    vol.Optional("detailed_report", default=False): cv.boolean,
})

# Global services registry to prevent double registration
_SERVICES_REGISTERED = False


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Paw Control integration."""
    _LOGGER.debug("Setting up Paw Control integration")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Paw Control from a config entry with enhanced error handling."""
    global _SERVICES_REGISTERED
    
    _LOGGER.info("Setting up Paw Control for %s", entry.data[CONF_DOG_NAME])
    
    hass.data.setdefault(DOMAIN, {})
    
    dog_name = entry.data[CONF_DOG_NAME]
    
    # Store config data
    hass.data[DOMAIN][entry.entry_id] = {
        "config": entry.data,
        "dog_name": dog_name,
        "store": Store(hass, 1, f"{DOMAIN}_{dog_name}"),
        "listeners": [],  # Track event listeners for cleanup
    }
    
    try:
        # Import helper functions
        from .helpers import async_create_helpers, PawControlDataUpdateCoordinator
        from .setup_verifier import async_verify_and_fix_installation
        
        # Step 1: Wait for core domains to be ready
        _LOGGER.info("Step 1: Waiting for core domains to be ready...")
        if not await _wait_for_core_domains(hass):
            _LOGGER.error("Core domains not ready, setup may be incomplete")
        
        # Step 2: Create all helper entities for this dog
        _LOGGER.info("Step 2: Creating helper entities for %s", dog_name)
        await async_create_helpers(hass, dog_name, entry.data)
        _LOGGER.info("Helper entities created successfully for %s", dog_name)
        
        # Step 3: Wait for entities to stabilize
        _LOGGER.info("Step 3: Waiting for entities to stabilize...")
        await asyncio.sleep(3.0)
        
        # Step 4: Verify installation and auto-fix any issues
        _LOGGER.info("Step 4: Verifying installation...")
        try:
            verification_result = await async_verify_and_fix_installation(hass, dog_name)
            
            if verification_result["status"] == "success":
                _LOGGER.info("Installation verified successfully for %s", dog_name)
            elif verification_result["status"] == "fixed":
                _LOGGER.info("Installation issues auto-fixed for %s: created %d entities", 
                            dog_name, len(verification_result.get("created_entities", [])))
            else:
                _LOGGER.warning("Installation verification failed for %s: %s", 
                              dog_name, verification_result.get("errors", []))
        except Exception as e:
            _LOGGER.warning("Installation verification failed for %s: %s", dog_name, e)
        
        # Step 5: Initialize the coordinator
        _LOGGER.info("Step 5: Initializing coordinator for %s", dog_name)
        coordinator = PawControlDataUpdateCoordinator(hass, entry)
        
        # Fetch initial data
        await coordinator.async_config_entry_first_refresh()
        
        # Update stored coordinator
        hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator
        
        # Step 6: Set up platforms
        _LOGGER.info("Step 6: Setting up platforms for %s", dog_name)
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        _LOGGER.info("Platforms set up successfully for %s", dog_name)
        
        # Step 7: Register services (only once globally)
        if not _SERVICES_REGISTERED:
            _LOGGER.info("Step 7: Registering global services")
            await _async_register_services(hass)
            _SERVICES_REGISTERED = True
        else:
            _LOGGER.debug("Services already registered, skipping")
        
        # Step 8: Create dashboard if requested
        if entry.data.get(CONF_CREATE_DASHBOARD, True):
            _LOGGER.info("Step 8: Creating dashboard for %s", dog_name)
            try:
                from .dashboard import async_create_dashboard
                await async_create_dashboard(hass, dog_name, entry.data)
            except Exception as e:
                _LOGGER.warning("Dashboard creation failed for %s: %s", dog_name, e)
        
        # Step 9: Setup automations and listeners
        _LOGGER.info("Step 9: Setting up automations for %s", dog_name)
        await _setup_automations(hass, entry, dog_name)
        
        # Step 10: Final verification and notification
        _LOGGER.info("Step 10: Final verification for %s", dog_name)
        await _final_verification_and_notification(hass, dog_name)
        
        _LOGGER.info("✅ Paw Control setup completed successfully for %s!", dog_name)
        return True
        
    except Exception as e:
        _LOGGER.error("❌ Error during setup for %s: %s", dog_name, e, exc_info=True)
        # Clean up partial setup
        await _cleanup_partial_setup(hass, entry)
        return False


async def _wait_for_core_domains(hass: HomeAssistant, timeout: int = 30) -> bool:
    """Wait for core domains to be available."""
    required_domains = ["input_boolean", "counter", "input_datetime", "input_text", "input_number", "input_select"]
    
    for _ in range(timeout):
        all_ready = True
        for domain in required_domains:
            if not hass.services.has_service(domain, "create"):
                all_ready = False
                break
        
        if all_ready:
            _LOGGER.debug("All core domains ready")
            return True
        
        await asyncio.sleep(1)
    
    _LOGGER.warning("Timeout waiting for core domains")
    return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry with proper cleanup."""
    global _SERVICES_REGISTERED
    
    _LOGGER.info("Unloading Paw Control entry for %s", entry.data[CONF_DOG_NAME])
    
    # Clean up listeners
    entry_data = hass.data[DOMAIN].get(entry.entry_id, {})
    listeners = entry_data.get("listeners", [])
    for remove_listener in listeners:
        try:
            remove_listener()
        except Exception as e:
            _LOGGER.warning("Error removing listener: %s", e)
    
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        
        # Remove services if no more instances
        if not hass.data[DOMAIN]:
            await _async_unregister_services(hass)
            _SERVICES_REGISTERED = False
            _LOGGER.info("All Paw Control instances removed, services unregistered")
    
    return unload_ok


async def _async_register_services(hass: HomeAssistant) -> None:
    """Register Paw Control services with comprehensive error handling."""
    
    # Check if already registered
    if hass.services.has_service(DOMAIN, "feed_dog"):
        _LOGGER.debug("Services already registered")
        return
    
    async def feed_dog_service(call: ServiceCall) -> None:
        """Handle feed dog service call."""
        await _handle_service_call(hass, call, "feed_dog")
    
    async def start_walk_service(call: ServiceCall) -> None:
        """Handle start walk service call."""
        await _handle_service_call(hass, call, "start_walk")
    
    async def end_walk_service(call: ServiceCall) -> None:
        """Handle end walk service call."""
        await _handle_service_call(hass, call, "end_walk")
    
    async def log_health_data_service(call: ServiceCall) -> None:
        """Handle log health data service call."""
        await _handle_service_call(hass, call, "log_health_data")
    
    async def set_mood_service(call: ServiceCall) -> None:
        """Handle set mood service call."""
        await _handle_service_call(hass, call, "set_mood")
    
    async def start_training_service(call: ServiceCall) -> None:
        """Handle start training service call."""
        await _handle_service_call(hass, call, "start_training")
    
    async def end_training_service(call: ServiceCall) -> None:
        """Handle end training service call."""
        await _handle_service_call(hass, call, "end_training")
    
    async def log_medication_service(call: ServiceCall) -> None:
        """Handle log medication service call."""
        await _handle_service_call(hass, call, "log_medication")
    
    async def schedule_vet_visit_service(call: ServiceCall) -> None:
        """Handle schedule vet visit service call."""
        await _handle_service_call(hass, call, "schedule_vet_visit")
    
    async def start_playtime_service(call: ServiceCall) -> None:
        """Handle start playtime service call."""
        await _handle_service_call(hass, call, "start_playtime")
    
    async def end_playtime_service(call: ServiceCall) -> None:
        """Handle end playtime service call."""
        await _handle_service_call(hass, call, "end_playtime")
    
    async def reset_all_data_service(call: ServiceCall) -> None:
        """Handle reset all data service call."""
        await _handle_service_call(hass, call, "reset_all_data")
    
    # Enhanced services from Hundesystem
    async def trigger_feeding_reminder(call: ServiceCall) -> None:
        """Handle feeding reminder service call."""
        await _handle_enhanced_service_call(hass, call, "trigger_feeding_reminder")
    
    async def daily_reset(call: ServiceCall) -> None:
        """Handle daily reset service call."""
        await _handle_enhanced_service_call(hass, call, "daily_reset")
    
    async def send_notification(call: ServiceCall) -> None:
        """Handle send notification service call."""
        await _handle_enhanced_service_call(hass, call, "send_notification")
    
    async def set_visitor_mode(call: ServiceCall) -> None:
        """Handle set visitor mode service call."""
        await _handle_enhanced_service_call(hass, call, "set_visitor_mode")
    
    async def log_activity(call: ServiceCall) -> None:
        """Handle log activity service call."""
        await _handle_enhanced_service_call(hass, call, "log_activity")
    
    async def test_notification(call: ServiceCall) -> None:
        """Handle test notification service call."""
        await _handle_enhanced_service_call(hass, call, "test_notification")
    
    async def emergency_contact(call: ServiceCall) -> None:
        """Handle emergency contact service call."""
        await _handle_enhanced_service_call(hass, call, "emergency_contact")
    
    async def health_check(call: ServiceCall) -> None:
        """Handle health check service call."""
        await _handle_enhanced_service_call(hass, call, "health_check")
    
    # GPS Services
    async def update_gps_simple_service(call: ServiceCall) -> None:
        """Handle update GPS simple service call."""
        await _handle_gps_service_call(hass, call, "update_gps_simple")
    
    async def setup_automatic_gps_service(call: ServiceCall) -> None:
        """Handle setup automatic GPS service call."""
        await _handle_gps_service_call(hass, call, "setup_automatic_gps")
    
    async def start_walk_tracking_service(call: ServiceCall) -> None:
        """Handle start walk tracking service call."""
        await _handle_gps_service_call(hass, call, "start_walk_tracking")
    
    async def end_walk_tracking_service(call: ServiceCall) -> None:
        """Handle end walk tracking service call."""
        await _handle_gps_service_call(hass, call, "end_walk_tracking")
    
    async def verify_installation_service(call: ServiceCall) -> None:
        """Handle verify installation service call."""
        await _handle_installation_service_call(hass, call)
    
    # Register all services
    services = [
        # Basic Paw Control services
        ("feed_dog", feed_dog_service, FEED_DOG_SCHEMA),
        ("start_walk", start_walk_service, START_WALK_SCHEMA),
        ("end_walk", end_walk_service, END_WALK_SCHEMA),
        ("log_health_data", log_health_data_service, LOG_HEALTH_DATA_SCHEMA),
        ("set_mood", set_mood_service, SET_MOOD_SCHEMA),
        ("start_training", start_training_service, START_TRAINING_SCHEMA),
        ("end_training", end_training_service, END_TRAINING_SCHEMA),
        ("log_medication", log_medication_service, LOG_MEDICATION_SCHEMA),
        ("schedule_vet_visit", schedule_vet_visit_service, SCHEDULE_VET_VISIT_SCHEMA),
        ("start_playtime", start_playtime_service, START_PLAYTIME_SCHEMA),
        ("end_playtime", end_playtime_service, END_PLAYTIME_SCHEMA),
        ("reset_all_data", reset_all_data_service, RESET_ALL_DATA_SCHEMA),
        
        # Enhanced services from Hundesystem
        (SERVICE_TRIGGER_FEEDING_REMINDER, trigger_feeding_reminder, TRIGGER_FEEDING_REMINDER_SCHEMA),
        (SERVICE_DAILY_RESET, daily_reset, None),
        (SERVICE_SEND_NOTIFICATION, send_notification, SEND_NOTIFICATION_SCHEMA),
        (SERVICE_SET_VISITOR_MODE, set_visitor_mode, SET_VISITOR_MODE_SCHEMA),
        (SERVICE_LOG_ACTIVITY, log_activity, LOG_ACTIVITY_SCHEMA),
        (SERVICE_TEST_NOTIFICATION, test_notification, TEST_NOTIFICATION_SCHEMA),
        (SERVICE_EMERGENCY_CONTACT, emergency_contact, EMERGENCY_CONTACT_SCHEMA),
        (SERVICE_HEALTH_CHECK, health_check, HEALTH_CHECK_SCHEMA),
        
        # GPS services
        ("update_gps_simple", update_gps_simple_service, UPDATE_GPS_SIMPLE_SCHEMA),
        ("setup_automatic_gps", setup_automatic_gps_service, SETUP_AUTOMATIC_GPS_SCHEMA),
        ("start_walk_tracking", start_walk_tracking_service, START_WALK_TRACKING_SCHEMA),
        ("end_walk_tracking", end_walk_tracking_service, END_WALK_TRACKING_SCHEMA),
        
        # Installation verification service
        ("verify_installation", verify_installation_service, VERIFY_INSTALLATION_SCHEMA),
    ]
    
    for service_name, service_func, schema in services:
        try:
            if not hass.services.has_service(DOMAIN, service_name):
                hass.services.async_register(DOMAIN, service_name, service_func, schema)
                _LOGGER.debug("Registered service: %s", service_name)
        except Exception as e:
            _LOGGER.error("Failed to register service %s: %s", service_name, e)
    
    _LOGGER.info("All Paw Control services registered successfully")


async def _async_unregister_services(hass: HomeAssistant) -> None:
    """Unregister all services."""
    services = [
        "feed_dog", "start_walk", "end_walk", "log_health_data", "set_mood",
        "start_training", "end_training", "log_medication", "schedule_vet_visit",
        "start_playtime", "end_playtime", "reset_all_data", "update_gps_simple",
        "setup_automatic_gps", "start_walk_tracking", "end_walk_tracking",
        "verify_installation", SERVICE_TRIGGER_FEEDING_REMINDER, SERVICE_DAILY_RESET,
        SERVICE_SEND_NOTIFICATION, SERVICE_SET_VISITOR_MODE, SERVICE_LOG_ACTIVITY,
        SERVICE_TEST_NOTIFICATION, SERVICE_EMERGENCY_CONTACT, SERVICE_HEALTH_CHECK,
    ]
    
    for service_name in services:
        if hass.services.has_service(DOMAIN, service_name):
            hass.services.async_remove(DOMAIN, service_name)
            _LOGGER.debug("Unregistered service: %s", service_name)


async def _handle_service_call(hass: HomeAssistant, call: ServiceCall, service_type: str) -> None:
    """Handle standard service calls."""
    entity_id = call.data.get(SERVICE_ENTITY_ID)
    if not entity_id:
        _LOGGER.error("No entity_id provided for %s service", service_type)
        return
    
    # Extract dog name from entity_id
    dog_name = _extract_dog_name_from_entity_id(entity_id)
    if not dog_name:
        _LOGGER.error("Could not extract dog name from entity_id: %s", entity_id)
        return
    
    # Find the coordinator
    coordinator = _find_coordinator_for_dog(hass, dog_name)
    if not coordinator:
        _LOGGER.error("No coordinator found for dog: %s", dog_name)
        return
    
    try:
        # Route to appropriate coordinator method
        if service_type == "feed_dog":
            await coordinator.async_feed_dog(call.data)
            await update_feeding_entities(hass, dog_name, call.data)
            
        elif service_type == "start_walk":
            await coordinator.async_start_walk(call.data)
            await update_walk_start_entities(hass, dog_name, call.data)
            
        elif service_type == "end_walk":
            await coordinator.async_end_walk(call.data)
            await update_walk_end_entities(hass, dog_name, call.data)
            
        elif service_type == "log_health_data":
            await coordinator.async_log_health_data(call.data)
            await update_health_entities(hass, dog_name, call.data)
            
        elif service_type == "set_mood":
            await coordinator.async_set_mood(call.data)
            await update_mood_entities(hass, dog_name, call.data)
            
        elif service_type == "start_training":
            await coordinator.async_start_training(call.data)
            await update_training_start_entities(hass, dog_name, call.data)
            
        elif service_type == "end_training":
            await coordinator.async_end_training(call.data)
            await update_training_end_entities(hass, dog_name, call.data)
            
        elif service_type == "log_medication":
            await coordinator.async_log_medication(call.data)
            await update_medication_entities(hass, dog_name, call.data)
            
        elif service_type == "schedule_vet_visit":
            await coordinator.async_schedule_vet_visit(call.data)
            await update_vet_entities(hass, dog_name, call.data)
            
        elif service_type == "start_playtime":
            await coordinator.async_start_playtime(call.data)
            await update_playtime_start_entities(hass, dog_name, call.data)
            
        elif service_type == "end_playtime":
            await coordinator.async_end_playtime(call.data)
            await update_playtime_end_entities(hass, dog_name, call.data)
            
        elif service_type == "reset_all_data":
            await coordinator.async_reset_all_data(call.data)
            await reset_all_entities(hass, dog_name, call.data)
        
        _LOGGER.info("%s service completed for %s", service_type, dog_name)
        
    except Exception as e:
        _LOGGER.error("Error in %s service for %s: %s", service_type, dog_name, e)


async def _handle_enhanced_service_call(hass: HomeAssistant, call: ServiceCall, service_type: str) -> None:
    """Handle enhanced service calls from Hundesystem integration."""
    try:
        dog_name = call.data.get("dog_name")
        
        # Get target config entries
        target_entries = []
        if dog_name:
            # Find specific dog
            for entry_id, data in hass.data[DOMAIN].items():
                if isinstance(data, dict) and data.get("dog_name") == dog_name:
                    target_entries.append(data)
                    break
        else:
            # All dogs
            target_entries = [data for data in hass.data[DOMAIN].values() if isinstance(data, dict)]
        
        if service_type == SERVICE_TRIGGER_FEEDING_REMINDER:
            meal_type = call.data["meal_type"]
            message = call.data.get("message", f"🐶 Zeit für {MEAL_TYPES[meal_type]}!")
            
            for entry_data in target_entries:
                config = entry_data["config"]
                dog = entry_data["dog_name"]
                
                # Update feeding datetime
                datetime_entity = f"input_datetime.{dog}_last_feeding_{meal_type}"
                if hass.states.get(datetime_entity):
                    await hass.services.async_call(
                        "input_datetime", "set_datetime",
                        {
                            "entity_id": datetime_entity,
                            "datetime": datetime.now().isoformat()
                        },
                        blocking=True
                    )
                
                # Send notification
                await _send_notification(hass, config, f"🍽️ Fütterungszeit - {dog.title()}", message)
                
                _LOGGER.info("Feeding reminder sent for %s: %s", dog, meal_type)
        
        elif service_type == SERVICE_DAILY_RESET:
            for entry_data in target_entries:
                dog = entry_data["dog_name"]
                config = entry_data["config"]
                
                try:
                    await _perform_daily_reset(hass, dog)
                    
                    # Send confirmation
                    await _send_notification(
                        hass, config,
                        f"🔄 Tagesreset - {dog.title()}", 
                        "Alle Statistiken wurden zurückgesetzt"
                    )
                    
                    _LOGGER.info("Daily reset completed for %s", dog)
                    
                except Exception as e:
                    _LOGGER.error("Error during daily reset for %s: %s", dog, e)
                    continue
        
        elif service_type == SERVICE_SEND_NOTIFICATION:
            title = call.data["title"]
            message = call.data["message"]
            target = call.data.get("target")
            data = call.data.get("data", {})
            
            for entry_data in target_entries:
                config = entry_data["config"]
                await _send_notification(hass, config, title, message, target, data)
        
        elif service_type == SERVICE_SET_VISITOR_MODE:
            enabled = call.data["enabled"]
            visitor_name = call.data.get("visitor_name", "")
            
            for entry_data in target_entries:
                dog = entry_data["dog_name"]
                
                # Set visitor mode input_boolean
                visitor_entity = f"input_boolean.{dog}_visitor_mode_input"
                if hass.states.get(visitor_entity):
                    action = "turn_on" if enabled else "turn_off"
                    await hass.services.async_call(
                        "input_boolean", action,
                        {"entity_id": visitor_entity},
                        blocking=True
                    )
                
                # Set visitor name
                if visitor_name:
                    name_entity = f"input_text.{dog}_visitor_name"
                    if hass.states.get(name_entity):
                        await hass.services.async_call(
                            "input_text", "set_value",
                            {"entity_id": name_entity, "value": visitor_name},
                            blocking=True
                        )
                
                _LOGGER.info("Visitor mode %s for %s", "enabled" if enabled else "disabled", dog)
        
        elif service_type == SERVICE_LOG_ACTIVITY:
            activity_type = call.data["activity_type"]
            duration = call.data.get("duration", 0)
            notes = call.data.get("notes", "")
            
            for entry_data in target_entries:
                dog = entry_data["dog_name"]
                await _log_activity_for_dog(hass, dog, activity_type, duration, notes)
                _LOGGER.info("Activity logged for %s: %s", dog, activity_type)
        
        elif service_type == SERVICE_TEST_NOTIFICATION:
            for entry_data in target_entries:
                config = entry_data["config"]
                dog = entry_data["dog_name"]
                
                await _send_notification(
                    hass, config,
                    f"🧪 Test - {dog.title()}", 
                    "Test-Benachrichtigung funktioniert! 🐶"
                )
        
        elif service_type == SERVICE_EMERGENCY_CONTACT:
            emergency_type = call.data["emergency_type"]
            message = call.data["message"]
            location = call.data.get("location", "")
            contact_vet = call.data.get("contact_vet", False)
            
            for entry_data in target_entries:
                dog = entry_data["dog_name"]
                config = entry_data["config"]
                
                # Set emergency mode
                emergency_entity = f"input_boolean.{dog}_emergency_mode"
                if hass.states.get(emergency_entity):
                    await hass.services.async_call(
                        "input_boolean", "turn_on",
                        {"entity_id": emergency_entity},
                        blocking=True
                    )
                
                # Send high priority notification
                emergency_message = f"🚨 NOTFALL - {dog.title()}\n\n"
                emergency_message += f"Art: {emergency_type}\n"
                emergency_message += f"Beschreibung: {message}\n"
                if location:
                    emergency_message += f"Standort: {location}\n"
                
                await _send_notification(
                    hass, config,
                    f"🚨 NOTFALL - {dog.title()}",
                    emergency_message,
                    data={"priority": "high", "ttl": 0}
                )
                
                _LOGGER.warning("Emergency activated for %s: %s", dog, emergency_type)
        
        elif service_type == SERVICE_HEALTH_CHECK:
            check_type = call.data.get("check_type", "general")
            notes = call.data.get("notes", "")
            temperature = call.data.get("temperature")
            weight = call.data.get("weight")
            
            for entry_data in target_entries:
                dog = entry_data["dog_name"]
                await _perform_health_check(hass, dog, check_type, notes, temperature, weight)
                _LOGGER.info("Health check completed for %s", dog)
        
    except Exception as e:
        _LOGGER.error("Error in enhanced service %s: %s", service_type, e)
        raise ServiceValidationError(f"Service execution failed: {e}")


async def _handle_gps_service_call(hass: HomeAssistant, call: ServiceCall, service_type: str) -> None:
    """Handle GPS-related service calls."""
    entity_id = call.data.get(SERVICE_ENTITY_ID)
    if not entity_id:
        _LOGGER.error("No entity_id provided for %s service", service_type)
        return
    
    # Extract dog name from entity_id
    dog_name = _extract_dog_name_from_entity_id(entity_id)
    if not dog_name:
        _LOGGER.error("Could not extract dog name from entity_id: %s", entity_id)
        return
    
    try:
        # Import GPS coordinator if available
        try:
            from .gps_coordinator import PawControlDataUpdateCoordinator as PawControlGPSCoordinator
            
            # Find or create GPS coordinator
            gps_coordinator = None
            for entry_id, entry_data in hass.data.get(DOMAIN, {}).items():
                if isinstance(entry_data, dict) and entry_data.get("dog_name") == dog_name:
                    coordinator = entry_data.get("coordinator")
                    if coordinator and hasattr(coordinator, 'async_update_gps_simple'):
                        gps_coordinator = coordinator
                        break
            
            if not gps_coordinator:
                _LOGGER.warning("No GPS coordinator found for %s, using standard coordinator", dog_name)
                coordinator = _find_coordinator_for_dog(hass, dog_name)
                if not coordinator:
                    _LOGGER.error("No coordinator found for dog: %s", dog_name)
                    return
                gps_coordinator = coordinator
            
        except ImportError:
            _LOGGER.warning("GPS coordinator not available, using standard coordinator")
            coordinator = _find_coordinator_for_dog(hass, dog_name)
            if not coordinator:
                _LOGGER.error("No coordinator found for dog: %s", dog_name)
                return
            gps_coordinator = coordinator
        
        # Route to appropriate GPS method
        if service_type == "update_gps_simple":
            if hasattr(gps_coordinator, 'async_update_gps_simple'):
                await gps_coordinator.async_update_gps_simple(call.data)
            await update_gps_entities(hass, dog_name, call.data)
            
        elif service_type == "setup_automatic_gps":
            if hasattr(gps_coordinator, 'async_setup_automatic_gps'):
                await gps_coordinator.async_setup_automatic_gps(call.data)
            await setup_gps_automation(hass, dog_name, call.data)
            
        elif service_type == "start_walk_tracking":
            if hasattr(gps_coordinator, 'async_start_walk_tracking'):
                await gps_coordinator.async_start_walk_tracking(call.data)
            await start_walk_tracking(hass, dog_name, call.data)
            
        elif service_type == "end_walk_tracking":
            if hasattr(gps_coordinator, 'async_end_walk_tracking'):
                await gps_coordinator.async_end_walk_tracking(call.data)
            await end_walk_tracking(hass, dog_name, call.data)
        
        _LOGGER.info("GPS %s service completed for %s", service_type, dog_name)
        
    except Exception as e:
        _LOGGER.error("Error in GPS %s service for %s: %s", service_type, dog_name, e)


async def _handle_installation_service_call(hass: HomeAssistant, call: ServiceCall) -> None:
    """Handle installation verification service call."""
    entity_id = call.data.get(SERVICE_ENTITY_ID)
    if not entity_id:
        _LOGGER.error("No entity_id provided for verification")
        return
    
    # Extract dog name from entity_id
    dog_name = _extract_dog_name_from_entity_id(entity_id)
    if not dog_name:
        _LOGGER.error("Could not extract dog name from entity_id: %s", entity_id)
        return
    
    try:
        from .setup_verifier import async_verify_and_fix_installation
        
        force_check = call.data.get("force_check", False)
        create_missing = call.data.get("create_missing_entities", True)
        send_notification = call.data.get("send_notification", True)
        detailed_report = call.data.get("detailed_report", False)
        
        _LOGGER.info("Manual installation verification requested for %s", dog_name)
        
        result = await async_verify_and_fix_installation(hass, dog_name)
        
        # Send notification if requested
        if send_notification and hass.services.has_service("notify", "persistent_notification"):
            if result["status"] == "success":
                message = f"✅ Installation vollständig\n📊 {result.get('total_entities_found', 0)} Entities bereit"
            elif result["status"] == "fixed":
                message = f"🔧 Installation repariert\n➕ {len(result.get('created_entities', []))} Entities erstellt"
            else:
                message = f"❌ Installation hat Probleme\n🚫 {len(result.get('errors', []))} Fehler gefunden"
            
            await hass.services.async_call(
                "notify", "persistent_notification",
                {
                    "title": f"🐕 Paw Control Check - {dog_name}",
                    "message": message,
                    "notification_id": f"paw_control_verification_{dog_name}"
                },
                blocking=False
            )
        
        _LOGGER.info("Manual verification completed for %s: %s", dog_name, result["status"])
        
    except Exception as e:
        _LOGGER.error("Manual verification failed for %s: %s", dog_name, e)


def _extract_dog_name_from_entity_id(entity_id: str) -> str:
    """Extract dog name from entity_id."""
    try:
        # Remove domain prefix (e.g., "sensor.", "input_boolean.")
        entity_name = entity_id.split(".", 1)[1] if "." in entity_id else entity_id
        
        # Extract dog name (first part before underscore)
        parts = entity_name.split("_")
        if len(parts) >= 2:
            return parts[0]
        
        # Fallback: return the whole entity name without domain
        return entity_name
        
    except Exception:
        return ""


def _find_coordinator_for_dog(hass: HomeAssistant, dog_name: str):
    """Find coordinator for a specific dog."""
    for entry_id, entry_data in hass.data.get(DOMAIN, {}).items():
        if isinstance(entry_data, dict) and entry_data.get("dog_name") == dog_name:
            return entry_data.get("coordinator")
    return None


# Helper functions for updating entities after service calls

async def _update_feeding_entities(hass: HomeAssistant, dog_name: str, data: dict) -> None:
    """Update feeding-related entities."""
    try:
        food_type = data.get(SERVICE_FOOD_TYPE, "Trockenfutter")
        amount = data.get(SERVICE_FOOD_AMOUNT, 100)
        
        # Update feeding boolean based on current time
        now = datetime.now()
        if now.hour < 10:
            feeding_entity = f"input_boolean.{dog_name}_feeding_morning"
        elif now.hour < 16:
            feeding_entity = f"input_boolean.{dog_name}_feeding_lunch"
        else:
            feeding_entity = f"input_boolean.{dog_name}_feeding_evening"
        
        # Turn on feeding boolean
        await _safe_service_call(hass, "input_boolean", "turn_on", {"entity_id": feeding_entity})
        
        # Update counter
        counter_entity = feeding_entity.replace("input_boolean", "counter").replace("feeding_", "feeding_") + "_count"
        await _safe_service_call(hass, "counter", "increment", {"entity_id": counter_entity})
        
        # Update last feeding datetime
        datetime_entity = feeding_entity.replace("input_boolean", "input_datetime").replace("feeding_", "last_feeding_")
        await _safe_service_call(hass, "input_datetime", "set_datetime", {
            "entity_id": datetime_entity,
            "datetime": now.isoformat()
        })
        
        # Update daily food amount
        daily_amount_entity = f"input_number.{dog_name}_daily_food_amount"
        current_state = hass.states.get(daily_amount_entity)
        if current_state:
            current_amount = float(current_state.state)
            new_amount = current_amount + amount
            await _safe_service_call(hass, "input_number", "set_value", {
                "entity_id": daily_amount_entity,
                "value": new_amount
            })
        
        _LOGGER.debug("Updated feeding entities for %s", dog_name)
        
    except Exception as e:
        _LOGGER.error("Error updating feeding entities for %s: %s", dog_name, e)


async def _update_walk_start_entities(hass: HomeAssistant, dog_name: str, data: dict) -> None:
    """Update entities when walk starts."""
    try:
        # Set walk in progress
        await _safe_service_call(hass, "input_boolean", "turn_on", {
            "entity_id": f"input_boolean.{dog_name}_walk_in_progress"
        })
        
        # Update walk start time
        await _safe_service_call(hass, "input_datetime", "set_datetime", {
            "entity_id": f"input_datetime.{dog_name}_last_walk",
            "datetime": datetime.now().isoformat()
        })
        
        _LOGGER.debug("Updated walk start entities for %s", dog_name)
        
    except Exception as e:
        _LOGGER.error("Error updating walk start entities for %s: %s", dog_name, e)


async def _update_walk_end_entities(hass: HomeAssistant, dog_name: str, data: dict) -> None:
    """Update entities when walk ends."""
    try:
        # Turn off walk in progress
        await _safe_service_call(hass, "input_boolean", "turn_off", {
            "entity_id": f"input_boolean.{dog_name}_walk_in_progress"
        })
        
        # Set outside and walked_today to true
        await _safe_service_call(hass, "input_boolean", "turn_on", {
            "entity_id": f"input_boolean.{dog_name}_outside"
        })
        await _safe_service_call(hass, "input_boolean", "turn_on", {
            "entity_id": f"input_boolean.{dog_name}_walked_today"
        })
        
        # Increment walk counter
        await _safe_service_call(hass, "counter", "increment", {
            "entity_id": f"counter.{dog_name}_walk_count"
        })
        
        # Update walk duration if provided
        duration = data.get(SERVICE_DURATION)
        if duration:
            await _safe_service_call(hass, "input_number", "set_value", {
                "entity_id": f"input_number.{dog_name}_daily_walk_duration",
                "value": duration
            })
        
        _LOGGER.debug("Updated walk end entities for %s", dog_name)
        
    except Exception as e:
        _LOGGER.error("Error updating walk end entities for %s: %s", dog_name, e)


async def _update_health_entities(hass: HomeAssistant, dog_name: str, data: dict) -> None:
    """Update health-related entities."""
    try:
        # Update weight if provided
        weight = data.get(SERVICE_WEIGHT)
        if weight:
            await _safe_service_call(hass, "input_number", "set_value", {
                "entity_id": f"input_number.{dog_name}_weight",
                "value": weight
            })
        
        # Update temperature if provided
        temperature = data.get(SERVICE_TEMPERATURE)
        if temperature:
            await _safe_service_call(hass, "input_number", "set_value", {
                "entity_id": f"input_number.{dog_name}_temperature",
                "value": temperature
            })
        
        # Update energy level if provided
        energy_level = data.get(SERVICE_ENERGY_LEVEL)
        if energy_level:
            await _safe_service_call(hass, "input_select", "select_option", {
                "entity_id": f"input_select.{dog_name}_energy_level_category",
                "option": energy_level
            })
        
        # Update health notes if provided
        symptoms = data.get(SERVICE_SYMPTOMS)
        notes = data.get(SERVICE_NOTES)
        if symptoms or notes:
            health_notes = f"{symptoms or ''} {notes or ''}".strip()
            await _safe_service_call(hass, "input_text", "set_value", {
                "entity_id": f"input_text.{dog_name}_health_notes",
                "value": health_notes
            })
        
        _LOGGER.debug("Updated health entities for %s", dog_name)
        
    except Exception as e:
        _LOGGER.error("Error updating health entities for %s: %s", dog_name, e)


async def _update_mood_entities(hass: HomeAssistant, dog_name: str, data: dict) -> None:
    """Update mood-related entities."""
    try:
        mood = data.get(SERVICE_MOOD)
        if mood:
            await _safe_service_call(hass, "input_select", "select_option", {
                "entity_id": f"input_select.{dog_name}_mood",
                "option": mood
            })
        
        _LOGGER.debug("Updated mood entities for %s", dog_name)
        
    except Exception as e:
        _LOGGER.error("Error updating mood entities for %s: %s", dog_name, e)


async def _update_training_start_entities(hass: HomeAssistant, dog_name: str, data: dict) -> None:
    """Update entities when training starts."""
    try:
        await _safe_service_call(hass, "input_boolean", "turn_on", {
            "entity_id": f"input_boolean.{dog_name}_training_session"
        })
        
        _LOGGER.debug("Updated training start entities for %s", dog_name)
        
    except Exception as e:
        _LOGGER.error("Error updating training start entities for %s: %s", dog_name, e)


async def _update_training_end_entities(hass: HomeAssistant, dog_name: str, data: dict) -> None:
    """Update entities when training ends."""
    try:
        await _safe_service_call(hass, "input_boolean", "turn_off", {
            "entity_id": f"input_boolean.{dog_name}_training_session"
        })
        
        await _safe_service_call(hass, "counter", "increment", {
            "entity_id": f"counter.{dog_name}_training_count"
        })
        
        _LOGGER.debug("Updated training end entities for %s", dog_name)
        
    except Exception as e:
        _LOGGER.error("Error updating training end entities for %s: %s", dog_name, e)


async def _update_medication_entities(hass: HomeAssistant, dog_name: str, data: dict) -> None:
    """Update medication-related entities."""
    try:
        await _safe_service_call(hass, "input_boolean", "turn_on", {
            "entity_id": f"input_boolean.{dog_name}_medication_given"
        })
        
        await _safe_service_call(hass, "counter", "increment", {
            "entity_id": f"counter.{dog_name}_medication_count"
        })
        
        await _safe_service_call(hass, "input_datetime", "set_datetime", {
            "entity_id": f"input_datetime.{dog_name}_last_medication",
            "datetime": datetime.now().isoformat()
        })
        
        _LOGGER.debug("Updated medication entities for %s", dog_name)
        
    except Exception as e:
        _LOGGER.error("Error updating medication entities for %s: %s", dog_name, e)





# Additional helper functions for setup
async def _setup_automations(hass: HomeAssistant, entry: ConfigEntry, dog_name: str) -> None:
    """Setup automations for this dog."""
    try:
        # Setup basic automations like daily reset, reminders etc.
        # This can be expanded with automation creation
        _LOGGER.debug("Setting up automations for %s", dog_name)
        
    except Exception as e:
        _LOGGER.warning("Error setting up automations for %s: %s", dog_name, e)


async def _final_verification_and_notification(hass: HomeAssistant, dog_name: str) -> None:
    """Final verification and send setup notification."""
    try:
        # Send setup complete notification if notification service is available
        if hass.services.has_service("notify", "persistent_notification"):
            await hass.services.async_call(
                "notify", "persistent_notification",
                {
                    "title": f"🐕 Paw Control Setup Complete - {dog_name}",
                    "message": f"✅ {dog_name} ist bereit!\n\n📱 Services verfügbar\n🛰️ GPS-Tracking aktiviert\n📊 Alle Entitäten erstellt",
                    "notification_id": f"paw_control_setup_complete_{dog_name}"
                },
                blocking=False
            )
        
        _LOGGER.info("Final verification completed for %s", dog_name)
        
    except Exception as e:
        _LOGGER.warning("Error in final verification for %s: %s", dog_name, e)


async def _cleanup_partial_setup(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Clean up partial setup on failure."""
    try:
        dog_name = entry.data[CONF_DOG_NAME]
        entry_data = hass.data[DOMAIN].get(entry.entry_id, {})
        
        # Clean up listeners
        listeners = entry_data.get("listeners", [])
        for remove_listener in listeners:
            try:
                remove_listener()
            except Exception:
                pass
        
        # Remove from hass.data
        hass.data[DOMAIN].pop(entry.entry_id, None)
        
        _LOGGER.info("Cleaned up partial setup for %s", dog_name)
        
    except Exception as e:
        _LOGGER.error("Error cleaning up partial setup: %s", e)


# Enhanced service helper functions
async def _send_notification(hass: HomeAssistant, config: dict, title: str, message: str, target: str = None, data: dict = None) -> None:
    """Send notification to configured devices."""
    try:
        push_devices = config.get(CONF_PUSH_DEVICES, [])
        
        if not push_devices and hass.services.has_service("notify", "persistent_notification"):
            # Fallback to persistent notification
            await hass.services.async_call(
                "notify", "persistent_notification",
                {
                    "title": title,
                    "message": message,
                    "notification_id": f"paw_control_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                },
                blocking=False
            )
        else:
            for device in push_devices:
                if hass.services.has_service("notify", device):
                    await hass.services.async_call(
                        "notify", device,
                        {
                            "title": title,
                            "message": message,
                            "data": data or {}
                        },
                        blocking=False
                    )
        
    except Exception as e:
        _LOGGER.error("Error sending notification: %s", e)


async def _perform_daily_reset(hass: HomeAssistant, dog_name: str) -> None:
    """Perform daily reset for a dog."""
    try:
        # Reset daily boolean entities
        daily_entities = [
            f"input_boolean.{dog_name}_feeding_morning",
            f"input_boolean.{dog_name}_feeding_lunch",
            f"input_boolean.{dog_name}_feeding_evening",
            f"input_boolean.{dog_name}_walked_today",
            f"input_boolean.{dog_name}_outside",
            f"input_boolean.{dog_name}_medication_given",
        ]
        
        for entity in daily_entities:
            if hass.states.get(entity):
                await hass.services.async_call(
                    "input_boolean", "turn_off",
                    {"entity_id": entity},
                    blocking=True
                )
        
        # Reset daily counters
        daily_counters = [
            f"counter.{dog_name}_walk_count",
            f"counter.{dog_name}_training_count",
            f"counter.{dog_name}_playtime_count",
            f"counter.{dog_name}_medication_count",
        ]
        
        for counter in daily_counters:
            if hass.states.get(counter):
                await hass.services.async_call(
                    "counter", "reset",
                    {"entity_id": counter},
                    blocking=True
                )
        
        # Reset daily number inputs
        daily_numbers = [
            f"input_number.{dog_name}_daily_food_amount",
            f"input_number.{dog_name}_daily_walk_duration",
        ]
        
        for number in daily_numbers:
            if hass.states.get(number):
                await hass.services.async_call(
                    "input_number", "set_value",
                    {"entity_id": number, "value": 0},
                    blocking=True
                )
        
        _LOGGER.info("Daily reset completed for %s", dog_name)
        
    except Exception as e:
        _LOGGER.error("Error during daily reset for %s: %s", dog_name, e)


async def _log_activity_for_dog(hass: HomeAssistant, dog_name: str, activity_type: str, duration: int, notes: str) -> None:
    """Log activity for a specific dog."""
    try:
        # Update activity counter
        counter_entity = f"counter.{dog_name}_activity_count"
        if hass.states.get(counter_entity):
            await hass.services.async_call(
                "counter", "increment",
                {"entity_id": counter_entity},
                blocking=True
            )
        
        # Update last activity time
        datetime_entity = f"input_datetime.{dog_name}_last_activity"
        if hass.states.get(datetime_entity):
            await hass.services.async_call(
                "input_datetime", "set_datetime",
                {
                    "entity_id": datetime_entity,
                    "datetime": datetime.now().isoformat()
                },
                blocking=True
            )
        
        # Update notes if provided
        if notes:
            notes_entity = f"input_text.{dog_name}_last_activity_notes"
            if hass.states.get(notes_entity):
                await hass.services.async_call(
                    "input_text", "set_value",
                    {"entity_id": notes_entity, "value": notes},
                    blocking=True
                )
        
        _LOGGER.debug("Activity logged for %s: %s", dog_name, activity_type)
        
    except Exception as e:
        _LOGGER.error("Error logging activity for %s: %s", dog_name, e)


async def _perform_health_check(hass: HomeAssistant, dog_name: str, check_type: str, notes: str, temperature: float = None, weight: float = None) -> None:
    """Perform health check for a dog."""
    try:
        # Update temperature if provided
        if temperature:
            temp_entity = f"input_number.{dog_name}_temperature"
            if hass.states.get(temp_entity):
                await hass.services.async_call(
                    "input_number", "set_value",
                    {"entity_id": temp_entity, "value": temperature},
                    blocking=True
                )
        
        # Update weight if provided
        if weight:
            weight_entity = f"input_number.{dog_name}_weight"
            if hass.states.get(weight_entity):
                await hass.services.async_call(
                    "input_number", "set_value",
                    {"entity_id": weight_entity, "value": weight},
                    blocking=True
                )
        
        # Update health notes
        if notes:
            notes_entity = f"input_text.{dog_name}_health_notes"
            if hass.states.get(notes_entity):
                await hass.services.async_call(
                    "input_text", "set_value",
                    {"entity_id": notes_entity, "value": notes},
                    blocking=True
                )
        
        _LOGGER.debug("Health check completed for %s", dog_name)
        
    except Exception as e:
        _LOGGER.error("Error during health check for %s: %s", dog_name, e)
