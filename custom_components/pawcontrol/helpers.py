"""Helper functions for Paw Control integration."""
from __future__ import annotations

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.util import slugify

from .const import (
    DOMAIN,
    CONF_DOG_NAME,
    ENTITIES,
    FEEDING_TYPES,
    MEAL_TYPES
)
from .utils import safe_service_call, normalize_dog_name

_LOGGER = logging.getLogger(__name__)


class PawControlDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for Paw Control."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )
        self.dog_name = entry.data[CONF_DOG_NAME]
        self.entry = entry
        self.config = entry.data

    @property
    def dog_name_normalized(self) -> str:
        """Get normalized dog name."""
        return normalize_dog_name(self.dog_name)

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from the API."""
        try:
            # Collect current state data
            data = {
                "dog_profile": {
                    "name": self.dog_name,
                    "breed": await self._get_entity_state("breed", ""),
                    "age": await self._get_entity_state("age_years", 0),
                    "weight": await self._get_entity_state("weight", 0),
                },
                "health": {
                    "status": await self._get_entity_state("health_status", "Gut"),
                    "mood": await self._get_entity_state("mood", "😊 Fröhlich"),
                    "temperature": await self._get_entity_state("temperature", 0),
                    "last_vet_visit": await self._get_entity_state("last_vet_visit", None),
                },
                "activity": {
                    "last_walk": await self._get_entity_state("last_walk", None),
                    "last_feeding": await self._get_entity_state("last_feeding_morning", None),
                    "activity_level": await self._get_entity_state("activity_level", "Normal"),
                },
                "status": {
                    "visitor_mode": await self._get_boolean_state("visitor_mode_input"),
                    "emergency_mode": await self._get_boolean_state("emergency_mode"),
                    "walk_in_progress": await self._get_boolean_state("walk_in_progress"),
                },
                "last_updated": datetime.now().isoformat(),
            }
            
            return data
            
        except Exception as e:
            _LOGGER.error("Error updating data for %s: %s", self.dog_name, e)
            return {}

    async def _get_entity_state(self, entity_suffix: str, default: Any = None) -> Any:
        """Get state of an entity."""
        # Try different entity types
        entity_types = ["input_text", "input_number", "input_select", "input_datetime", "sensor"]
        
        for entity_type in entity_types:
            entity_id = f"{entity_type}.{self.dog_name}_{entity_suffix}"
            state = self.hass.states.get(entity_id)
            
            if state and state.state not in ["unknown", "unavailable"]:
                # Convert numeric values
                if entity_type == "input_number":
                    try:
                        return float(state.state)
                    except (ValueError, TypeError):
                        continue
                else:
                    return state.state
        
        return default

    async def _get_boolean_state(self, entity_suffix: str) -> bool:
        """Get boolean state of an entity."""
        entity_id = f"input_boolean.{self.dog_name}_{entity_suffix}"
        state = self.hass.states.get(entity_id)
        return state.state == "on" if state else False

    # ================================================================================
    # SERVICE HANDLERS
    # ================================================================================

    async def async_feed_dog(self, data: Dict[str, Any]) -> None:
        """Handle feed dog service."""
        try:
            food_type = data.get("food_type", "Trockenfutter")
            amount = data.get("food_amount", 150)
            notes = data.get("notes", "")
            
            # Determine meal type based on time
            now = datetime.now()
            if now.hour < 10:
                meal_type = "morning"
            elif now.hour < 16:
                meal_type = "lunch"
            else:
                meal_type = "evening"
            
            # Update feeding boolean
            await safe_service_call(
                self.hass, "input_boolean", "turn_on",
                {"entity_id": f"input_boolean.{self.dog_name}_feeding_{meal_type}"}
            )
            
            # Update last feeding time
            await safe_service_call(
                self.hass, "input_datetime", "set_datetime",
                {
                    "entity_id": f"input_datetime.{self.dog_name}_last_feeding_{meal_type}",
                    "datetime": now.isoformat()
                }
            )
            
            # Update daily food amount
            await self._add_to_daily_amount("daily_food_amount", amount)
            
            _LOGGER.info("Feeding recorded for %s: %s (%dg)", self.dog_name, meal_type, amount)
            
        except Exception as e:
            _LOGGER.error("Error in feed dog service for %s: %s", self.dog_name, e)

    async def async_start_walk(self, data: Dict[str, Any]) -> None:
        """Handle start walk service."""
        try:
            walk_type = data.get("walk_type", "Normal")
            location = data.get("location", "")
            
            # Set walk in progress
            await safe_service_call(
                self.hass, "input_boolean", "turn_on",
                {"entity_id": f"input_boolean.{self.dog_name}_walk_in_progress"}
            )
            
            # Update last walk time
            await safe_service_call(
                self.hass, "input_datetime", "set_datetime",
                {
                    "entity_id": f"input_datetime.{self.dog_name}_last_walk",
                    "datetime": datetime.now().isoformat()
                }
            )
            
            # Mark as outside
            await safe_service_call(
                self.hass, "input_boolean", "turn_on",
                {"entity_id": f"input_boolean.{self.dog_name}_outside"}
            )
            
            _LOGGER.info("Walk started for %s: %s", self.dog_name, walk_type)
            
        except Exception as e:
            _LOGGER.error("Error in start walk service for %s: %s", self.dog_name, e)

    async def async_end_walk(self, data: Dict[str, Any]) -> None:
        """Handle end walk service."""
        try:
            duration = data.get("duration", 30)
            rating = data.get("rating", 5)
            notes = data.get("notes", "")
            
            # End walk in progress
            await safe_service_call(
                self.hass, "input_boolean", "turn_off",
                {"entity_id": f"input_boolean.{self.dog_name}_walk_in_progress"}
            )
            
            # Mark as walked today
            await safe_service_call(
                self.hass, "input_boolean", "turn_on",
                {"entity_id": f"input_boolean.{self.dog_name}_walked_today"}
            )
            
            # Update walk duration
            await self._add_to_daily_amount("daily_walk_duration", duration)
            
            # Increment walk counter
            await safe_service_call(
                self.hass, "counter", "increment",
                {"entity_id": f"counter.{self.dog_name}_walk_count"}
            )
            
            _LOGGER.info("Walk ended for %s: %d minutes", self.dog_name, duration)
            
        except Exception as e:
            _LOGGER.error("Error in end walk service for %s: %s", self.dog_name, e)

    async def async_log_health_data(self, data: Dict[str, Any]) -> None:
        """Handle log health data service."""
        try:
            weight = data.get("weight")
            temperature = data.get("temperature")
            energy_level = data.get("energy_level")
            symptoms = data.get("symptoms", "")
            notes = data.get("notes", "")
            
            # Update weight if provided
            if weight:
                await safe_service_call(
                    self.hass, "input_number", "set_value",
                    {"entity_id": f"input_number.{self.dog_name}_weight", "value": weight}
                )
            
            # Update temperature if provided
            if temperature:
                await safe_service_call(
                    self.hass, "input_number", "set_value",
                    {"entity_id": f"input_number.{self.dog_name}_temperature", "value": temperature}
                )
            
            # Update energy level if provided
            if energy_level:
                await safe_service_call(
                    self.hass, "input_select", "select_option",
                    {"entity_id": f"input_select.{self.dog_name}_energy_level_category", "option": energy_level}
                )
            
            # Update health notes
            health_note = f"{symptoms} {notes}".strip()
            if health_note:
                await safe_service_call(
                    self.hass, "input_text", "set_value",
                    {"entity_id": f"input_text.{self.dog_name}_health_notes", "value": health_note}
                )
            
            _LOGGER.info("Health data logged for %s", self.dog_name)
            
        except Exception as e:
            _LOGGER.error("Error in log health data service for %s: %s", self.dog_name, e)

    async def async_set_mood(self, data: Dict[str, Any]) -> None:
        """Handle set mood service."""
        try:
            mood = data.get("mood")
            reason = data.get("reason", "")
            
            if mood:
                await safe_service_call(
                    self.hass, "input_select", "select_option",
                    {"entity_id": f"input_select.{self.dog_name}_mood", "option": mood}
                )
                
                _LOGGER.info("Mood set for %s: %s", self.dog_name, mood)
            
        except Exception as e:
            _LOGGER.error("Error in set mood service for %s: %s", self.dog_name, e)

    async def async_start_training(self, data: Dict[str, Any]) -> None:
        """Handle start training service."""
        try:
            training_type = data.get("training_type", "Grundgehorsam")
            duration_planned = data.get("duration_planned", 15)
            
            await safe_service_call(
                self.hass, "input_boolean", "turn_on",
                {"entity_id": f"input_boolean.{self.dog_name}_training_session"}
            )
            
            await safe_service_call(
                self.hass, "input_datetime", "set_datetime",
                {
                    "entity_id": f"input_datetime.{self.dog_name}_last_training",
                    "datetime": datetime.now().isoformat()
                }
            )
            
            _LOGGER.info("Training started for %s: %s", self.dog_name, training_type)
            
        except Exception as e:
            _LOGGER.error("Error in start training service for %s: %s", self.dog_name, e)

    async def async_end_training(self, data: Dict[str, Any]) -> None:
        """Handle end training service."""
        try:
            success_rating = data.get("success_rating", 3)
            duration = data.get("duration", 15)
            learned_commands = data.get("learned_commands", "")
            
            await safe_service_call(
                self.hass, "input_boolean", "turn_off",
                {"entity_id": f"input_boolean.{self.dog_name}_training_session"}
            )
            
            await safe_service_call(
                self.hass, "counter", "increment",
                {"entity_id": f"counter.{self.dog_name}_training_count"}
            )
            
            await self._add_to_daily_amount("daily_training_duration", duration)
            
            _LOGGER.info("Training ended for %s: %d minutes", self.dog_name, duration)
            
        except Exception as e:
            _LOGGER.error("Error in end training service for %s: %s", self.dog_name, e)

    async def async_log_medication(self, data: Dict[str, Any]) -> None:
        """Handle log medication service."""
        try:
            medication_name = data.get("medication_name", "")
            medication_amount = data.get("medication_amount", 0)
            medication_unit = data.get("medication_unit", "mg")
            
            await safe_service_call(
                self.hass, "input_boolean", "turn_on",
                {"entity_id": f"input_boolean.{self.dog_name}_medication_given"}
            )
            
            await safe_service_call(
                self.hass, "counter", "increment",
                {"entity_id": f"counter.{self.dog_name}_medication_count"}
            )
            
            await safe_service_call(
                self.hass, "input_datetime", "set_datetime",
                {
                    "entity_id": f"input_datetime.{self.dog_name}_last_medication",
                    "datetime": datetime.now().isoformat()
                }
            )
            
            _LOGGER.info("Medication logged for %s: %s %s%s", 
                        self.dog_name, medication_name, medication_amount, medication_unit)
            
        except Exception as e:
            _LOGGER.error("Error in log medication service for %s: %s", self.dog_name, e)

    async def async_schedule_vet_visit(self, data: Dict[str, Any]) -> None:
        """Handle schedule vet visit service."""
        try:
            vet_name = data.get("vet_name", "")
            vet_date = data.get("vet_date", "")
            vet_reason = data.get("vet_reason", "Routineuntersuchung")
            
            if vet_date:
                await safe_service_call(
                    self.hass, "input_datetime", "set_datetime",
                    {
                        "entity_id": f"input_datetime.{self.dog_name}_next_vet_appointment",
                        "datetime": vet_date
                    }
                )
            
            if vet_name:
                await safe_service_call(
                    self.hass, "input_text", "set_value",
                    {"entity_id": f"input_text.{self.dog_name}_vet_contact", "value": vet_name}
                )
            
            _LOGGER.info("Vet visit scheduled for %s: %s", self.dog_name, vet_date)
            
        except Exception as e:
            _LOGGER.error("Error in schedule vet visit service for %s: %s", self.dog_name, e)

    async def async_start_playtime(self, data: Dict[str, Any]) -> None:
        """Handle start playtime service."""
        try:
            play_type = data.get("play_type", "Freies Spiel")
            location = data.get("location", "Zuhause")
            
            await safe_service_call(
                self.hass, "input_boolean", "turn_on",
                {"entity_id": f"input_boolean.{self.dog_name}_played_today"}
            )
            
            await safe_service_call(
                self.hass, "input_datetime", "set_datetime",
                {
                    "entity_id": f"input_datetime.{self.dog_name}_last_play",
                    "datetime": datetime.now().isoformat()
                }
            )
            
            _LOGGER.info("Playtime started for %s: %s", self.dog_name, play_type)
            
        except Exception as e:
            _LOGGER.error("Error in start playtime service for %s: %s", self.dog_name, e)

    async def async_end_playtime(self, data: Dict[str, Any]) -> None:
        """Handle end playtime service."""
        try:
            duration = data.get("duration", 20)
            fun_rating = data.get("fun_rating", 5)
            energy_afterwards = data.get("energy_afterwards", "Entspannt")
            
            await safe_service_call(
                self.hass, "counter", "increment",
                {"entity_id": f"counter.{self.dog_name}_play_count"}
            )
            
            await self._add_to_daily_amount("daily_play_duration", duration)
            
            _LOGGER.info("Playtime ended for %s: %d minutes", self.dog_name, duration)
            
        except Exception as e:
            _LOGGER.error("Error in end playtime service for %s: %s", self.dog_name, e)

    async def async_reset_all_data(self, data: Dict[str, Any]) -> None:
        """Handle reset all data service."""
        try:
            confirm_reset = data.get("confirm_reset", "")
            
            if confirm_reset != "RESET":
                _LOGGER.warning("Reset not confirmed for %s", self.dog_name)
                return
            
            # Reset boolean entities
            boolean_entities = [
                "feeding_morning", "feeding_lunch", "feeding_evening", "feeding_snack",
                "outside", "walked_today", "played_today", "poop_done", 
                "medication_given", "training_session"
            ]
            
            for entity_suffix in boolean_entities:
                await safe_service_call(
                    self.hass, "input_boolean", "turn_off",
                    {"entity_id": f"input_boolean.{self.dog_name}_{entity_suffix}"}
                )
            
            # Reset counters
            counter_entities = [
                "walk_count", "play_count", "training_count", "poop_count", "medication_count"
            ]
            
            for entity_suffix in counter_entities:
                await safe_service_call(
                    self.hass, "counter", "reset",
                    {"entity_id": f"counter.{self.dog_name}_{entity_suffix}"}
                )
            
            # Reset daily amounts
            number_entities = [
                "daily_food_amount", "daily_walk_duration", "daily_play_duration", "daily_training_duration"
            ]
            
            for entity_suffix in number_entities:
                await safe_service_call(
                    self.hass, "input_number", "set_value",
                    {"entity_id": f"input_number.{self.dog_name}_{entity_suffix}", "value": 0}
                )
            
            _LOGGER.info("All data reset for %s", self.dog_name)
            
        except Exception as e:
            _LOGGER.error("Error in reset all data service for %s: %s", self.dog_name, e)

    # ================================================================================
    # HELPER METHODS
    # ================================================================================

    async def _add_to_daily_amount(self, entity_suffix: str, amount: float) -> None:
        """Add amount to daily tracking entity."""
        try:
            entity_id = f"input_number.{self.dog_name}_{entity_suffix}"
            current_state = self.hass.states.get(entity_id)
            
            if current_state and current_state.state not in ["unknown", "unavailable"]:
                current_value = float(current_state.state)
                new_value = current_value + amount
                
                await safe_service_call(
                    self.hass, "input_number", "set_value",
                    {"entity_id": entity_id, "value": new_value}
                )
                
        except (ValueError, TypeError) as e:
            _LOGGER.error("Error adding to daily amount %s: %s", entity_suffix, e)


# ================================================================================
# ENTITY CREATION FUNCTIONS
# ================================================================================

async def async_create_helpers(hass: HomeAssistant, dog_name: str, config: Dict[str, Any]) -> None:
    """Create all helper entities for a dog."""
    try:
        _LOGGER.info("Creating helper entities for %s", dog_name)
        
        # Create entities by type
        await _create_input_boolean_entities(hass, dog_name)
        await _create_input_number_entities(hass, dog_name)
        await _create_input_text_entities(hass, dog_name)
        await _create_input_datetime_entities(hass, dog_name)
        await _create_counter_entities(hass, dog_name)
        await _create_input_select_entities(hass, dog_name)
        
        _LOGGER.info("Successfully created helper entities for %s", dog_name)
        
    except Exception as e:
        _LOGGER.error("Error creating helper entities for %s: %s", dog_name, e)
        raise


async def _create_input_boolean_entities(hass: HomeAssistant, dog_name: str) -> None:
    """Create input_boolean entities."""
    for entity_suffix, entity_config in ENTITIES.get("input_boolean", {}).items():
        entity_name = f"{dog_name}_{entity_suffix}"
        
        await safe_service_call(
            hass, "input_boolean", "create",
            {
                "name": f"{dog_name.title()} {entity_config['name']}",
                "icon": entity_config.get("icon", "mdi:dog")
            }
        )
        
        await asyncio.sleep(0.1)  # Small delay between creations


async def _create_input_number_entities(hass: HomeAssistant, dog_name: str) -> None:
    """Create input_number entities."""
    for entity_suffix, entity_config in ENTITIES.get("input_number", {}).items():
        entity_name = f"{dog_name}_{entity_suffix}"
        
        service_data = {
            "name": f"{dog_name.title()} {entity_config['name']}",
            "min": entity_config.get("min", 0),
            "max": entity_config.get("max", 100),
            "step": entity_config.get("step", 1),
            "icon": entity_config.get("icon", "mdi:dog"),
            "mode": "slider"
        }
        
        if "initial" in entity_config:
            service_data["initial"] = entity_config["initial"]
        if "unit" in entity_config:
            service_data["unit_of_measurement"] = entity_config["unit"]
        
        await safe_service_call(hass, "input_number", "create", service_data)
        await asyncio.sleep(0.1)


async def _create_input_text_entities(hass: HomeAssistant, dog_name: str) -> None:
    """Create input_text entities."""
    for entity_suffix, entity_config in ENTITIES.get("input_text", {}).items():
        entity_name = f"{dog_name}_{entity_suffix}"
        
        service_data = {
            "name": f"{dog_name.title()} {entity_config['name']}",
            "max": entity_config.get("max", 255),
            "icon": entity_config.get("icon", "mdi:dog"),
            "mode": "text"
        }
        
        await safe_service_call(hass, "input_text", "create", service_data)
        await asyncio.sleep(0.1)


async def _create_input_datetime_entities(hass: HomeAssistant, dog_name: str) -> None:
    """Create input_datetime entities."""
    for entity_suffix, entity_config in ENTITIES.get("input_datetime", {}).items():
        entity_name = f"{dog_name}_{entity_suffix}"
        
        service_data = {
            "name": f"{dog_name.title()} {entity_config['name']}",
            "has_date": entity_config.get("has_date", True),
            "has_time": entity_config.get("has_time", True),
            "icon": entity_config.get("icon", "mdi:dog")
        }
        
        if "initial" in entity_config:
            service_data["initial"] = entity_config["initial"]
        
        await safe_service_call(hass, "input_datetime", "create", service_data)
        await asyncio.sleep(0.1)


async def _create_counter_entities(hass: HomeAssistant, dog_name: str) -> None:
    """Create counter entities."""
    for entity_suffix, entity_config in ENTITIES.get("counter", {}).items():
        entity_name = f"{dog_name}_{entity_suffix}"
        
        service_data = {
            "name": f"{dog_name.title()} {entity_config['name']}",
            "initial": entity_config.get("initial", 0),
            "step": entity_config.get("step", 1),
            "minimum": 0,
            "maximum": 999999,
            "icon": entity_config.get("icon", "mdi:dog"),
            "restore": True
        }
        
        await safe_service_call(hass, "counter", "create", service_data)
        await asyncio.sleep(0.1)


async def _create_input_select_entities(hass: HomeAssistant, dog_name: str) -> None:
    """Create input_select entities."""
    for entity_suffix, entity_config in ENTITIES.get("input_select", {}).items():
        entity_name = f"{dog_name}_{entity_suffix}"
        
        service_data = {
            "name": f"{dog_name.title()} {entity_config['name']}",
            "options": entity_config.get("options", ["Option1", "Option2"]),
            "icon": entity_config.get("icon", "mdi:dog")
        }
        
        if "initial" in entity_config:
            service_data["initial"] = entity_config["initial"]
        
        await safe_service_call(hass, "input_select", "create", service_data)
        await asyncio.sleep(0.1)


# ================================================================================
# UTILITY FUNCTIONS
# ================================================================================

def get_dog_entity_id(dog_name: str, entity_type: str, suffix: str) -> str:
    """Generate entity ID for dog-specific entity."""
    dog_slug = slugify(dog_name)
    return f"{entity_type}.{dog_slug}_{suffix}"


async def check_entity_exists(hass: HomeAssistant, entity_id: str) -> bool:
    """Check if entity exists."""
    return hass.states.get(entity_id) is not None


async def get_dog_status_summary(hass: HomeAssistant, dog_name: str) -> Dict[str, Any]:
    """Get comprehensive status summary for a dog."""
    try:
        # Get feeding status
        feeding_status = {}
        for meal in FEEDING_TYPES:
            entity_id = f"input_boolean.{dog_name}_feeding_{meal}"
            state = hass.states.get(entity_id)
            feeding_status[meal] = state.state == "on" if state else False
        
        # Get activity status
        activity_entities = ["outside", "walked_today", "played_today", "poop_done"]
        activity_status = {}
        for activity in activity_entities:
            entity_id = f"input_boolean.{dog_name}_{activity}"
            state = hass.states.get(entity_id)
            activity_status[activity] = state.state == "on" if state else False
        
        # Get health status
        health_entity = f"input_select.{dog_name}_health_status"
        health_state = hass.states.get(health_entity)
        health_status = health_state.state if health_state else "Unbekannt"
        
        # Get mood
        mood_entity = f"input_select.{dog_name}_mood"
        mood_state = hass.states.get(mood_entity)
        mood = mood_state.state if mood_state else "😐 Neutral"
        
        # Calculate completion percentage
        total_tasks = len(feeding_status) + len(activity_status)
        completed_tasks = sum(feeding_status.values()) + sum(activity_status.values())
        completion_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        return {
            "dog_name": dog_name,
            "feeding_status": feeding_status,
            "activity_status": activity_status,
            "health_status": health_status,
            "mood": mood,
            "completion_percentage": completion_percentage,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        _LOGGER.error("Error getting status summary for %s: %s", dog_name, e)
        return {
            "dog_name": dog_name,
            "error": str(e),
            "last_updated": datetime.now().isoformat()
        }


async def send_dog_notification(hass: HomeAssistant, dog_name: str, title: str, message: str) -> None:
    """Send notification for dog."""
    try:
        if hass.services.has_service("persistent_notification", "create"):
            await hass.services.async_call(
                "persistent_notification", "create",
                {
                    "title": title,
                    "message": message,
                    "notification_id": f"paw_control_{dog_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                },
                blocking=False
            )
    except Exception as e:
        _LOGGER.error("Error sending notification for %s: %s", dog_name, e)


async def cleanup_dog_entities(hass: HomeAssistant, dog_name: str) -> None:
    """Clean up all entities for a dog (used during uninstall)."""
    try:
        _LOGGER.info("Cleaning up entities for %s", dog_name)
        
        # Get all entities with dog name
        all_entities = hass.states.async_all()
        dog_entities = [
            state.entity_id for state in all_entities 
            if dog_name in state.entity_id.lower()
        ]
        
        # Remove entities by domain
        domains_to_clean = ["input_boolean", "input_number", "input_text", "input_datetime", "counter", "input_select"]
        
        for domain in domains_to_clean:
            domain_entities = [entity_id for entity_id in dog_entities if entity_id.startswith(f"{domain}.")]
            
            for entity_id in domain_entities:
                try:
                    await hass.services.async_call(
                        domain, "remove",
                        {"entity_id": entity_id},
                        blocking=True
                    )
                    await asyncio.sleep(0.1)
                except Exception as e:
                    _LOGGER.debug("Could not remove entity %s: %s", entity_id, e)
        
        _LOGGER.info("Entity cleanup completed for %s", dog_name)
        
    except Exception as e:
        _LOGGER.error("Error during entity cleanup for %s: %s", dog_name, e)

def parse_datetime(dt_str: str) -> Optional[datetime.datetime]:
    try:
        return datetime.datetime.fromisoformat(dt_str)
    except Exception as e:
        _LOGGER.error("Failed to parse datetime '%s': %s", dt_str, e)
        return None

def format_datetime(dt: datetime.datetime) -> str:
    if dt is None:
        return ""
    return dt.isoformat()

def safe_get(data: Dict, *keys, default=None):
    for key in keys:
        if not isinstance(data, dict):
            return default
        data = data.get(key, default)
        if data is default:
            return default
    return data

def merge_dicts(a: Dict, b: Dict) -> Dict:
    result = a.copy()
    result.update(b)
    return result

def days_between(date1: datetime.datetime, date2: datetime.datetime) -> int:
    return abs((date2 - date1).days)

def clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, val))

def is_valid_lat_lon(lat: Any, lon: Any) -> bool:
    try:
        lat = float(lat)
        lon = float(lon)
        return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0
    except Exception:
        return False

def pretty_time_delta(seconds: int) -> str:
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    result = []
    if days > 0:
        result.append(f"{days}d")
    if hours > 0:
        result.append(f"{hours}h")
    if minutes > 0:
        result.append(f"{minutes}m")
    if sec > 0 or not result:
        result.append(f"{sec}s")
    return ' '.join(result)

def generate_automation(trigger: dict, action: dict, condition: dict = None) -> dict:
    automation = {
        "trigger": [trigger],
        "action": [action]
    }
    if condition:
        automation["condition"] = [condition]
    return automation

def build_time_trigger(at_time: str) -> dict:
    return {
        "platform": "time",
        "at": at_time
    }

def build_state_trigger(entity_id: str, from_state: str = None, to_state: str = None) -> dict:
    trig = {
        "platform": "state",
        "entity_id": entity_id
    }
    if from_state is not None:
        trig["from"] = from_state
    if to_state is not None:
        trig["to"] = to_state
    return trig

def build_notify_action(message: str, title: str = "PawControl") -> dict:
    return {
        "service": "persistent_notification.create",
        "data": {"title": title, "message": message}
    }

def send_notification(hass, title: str, message: str):
    hass.async_create_task(
        hass.services.async_call(
            "persistent_notification",
            "create",
            {"title": title, "message": message},
        )
    )

def send_mobile_notification(hass, message: str, target_device: str = None):
    service_data = {"message": message}
    if target_device:
        service_data["target"] = target_device
    hass.async_create_task(
        hass.services.async_call(
            "notify",
            "mobile_app",
            service_data,
        )
    )
