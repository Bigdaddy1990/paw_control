"""Button platform for Paw Control - COMPLETELY FIXED."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    ICON_FOOD,
    ICON_WALK,
    ICON_HEALTH,
    ICON_PLAY,
    ICON_TRAINING,
    ATTR_DOG_NAME,
    ATTR_DOG_BREED,
    ATTR_DOG_AGE,
    ATTR_DOG_WEIGHT,
    ATTR_LAST_UPDATED,
)
from .helpers import PawControlDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    dog_name = coordinator.dog_name
    
    entities = [
        # Feeding buttons
        PawControlFeedMorningButton(coordinator, dog_name),
        PawControlFeedLunchButton(coordinator, dog_name),
        PawControlFeedEveningButton(coordinator, dog_name),
        PawControlFeedSnackButton(coordinator, dog_name),
        
        # Activity buttons
        PawControlStartWalkButton(coordinator, dog_name),
        PawControlEndWalkButton(coordinator, dog_name),
        PawControlMarkOutsideButton(coordinator, dog_name),
        PawControlMarkPoopDoneButton(coordinator, dog_name),
        
        # Training buttons
        PawControlStartTrainingButton(coordinator, dog_name),
        PawControlEndTrainingButton(coordinator, dog_name),
        
        # Play buttons
        PawControlStartPlaytimeButton(coordinator, dog_name),
        PawControlEndPlaytimeButton(coordinator, dog_name),
        
        # Health buttons
        PawControlHealthCheckButton(coordinator, dog_name),
        PawControlGiveMedicationButton(coordinator, dog_name),
        
        # GPS buttons
        PawControlUpdateGPSButton(coordinator, dog_name),
        PawControlStartWalkTrackingButton(coordinator, dog_name),
        PawControlEndWalkTrackingButton(coordinator, dog_name),
        
        # System buttons
        PawControlResetDailyDataButton(coordinator, dog_name),
        PawControlEmergencyButton(coordinator, dog_name),
        PawControlVisitorModeButton(coordinator, dog_name),
    ]
    
    async_add_entities(entities)


class PawControlButtonBase(CoordinatorEntity, ButtonEntity):
    """Base class for Paw Control buttons."""

    def __init__(
        self,
        coordinator: PawControlDataUpdateCoordinator,
        dog_name: str,
        button_type: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._dog_name = dog_name
        self._button_type = button_type
        self._attr_unique_id = f"{DOMAIN}_{dog_name.lower()}_{button_type}"
        self._attr_name = f"{dog_name} {button_type.replace('_', ' ').title()}"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._dog_name.lower())},
            "name": f"Paw Control - {self._dog_name}",
            "manufacturer": "Paw Control",
            "model": "Dog Management System",
            "sw_version": "1.3.0",
        }

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            ATTR_DOG_NAME: self._dog_name,
            ATTR_LAST_UPDATED: datetime.now().isoformat(),
        }

    async def _safe_service_call(self, domain: str, service: str, data: dict) -> bool:
        """Safely call a service with error handling."""
        try:
            await self.hass.services.async_call(domain, service, data, blocking=True)
            return True
        except Exception as e:
            _LOGGER.error("Service call %s.%s failed for %s: %s", domain, service, self._dog_name, e)
            return False

    async def _set_boolean_state(self, entity_suffix: str, state: bool) -> None:
        """Set boolean entity state."""
        entity_id = f"input_boolean.{self._dog_name}_{entity_suffix}"
        service = "turn_on" if state else "turn_off"
        await self._safe_service_call("input_boolean", service, {"entity_id": entity_id})

    async def _increment_counter(self, entity_suffix: str) -> None:
        """Increment counter entity."""
        entity_id = f"counter.{self._dog_name}_{entity_suffix}"
        await self._safe_service_call("counter", "increment", {"entity_id": entity_id})

    async def _set_datetime_now(self, entity_suffix: str) -> None:
        """Set datetime entity to current time."""
        entity_id = f"input_datetime.{self._dog_name}_{entity_suffix}"
        await self._safe_service_call("input_datetime", "set_datetime", {
            "entity_id": entity_id,
            "datetime": datetime.now().isoformat()
        })

    async def _add_to_number(self, entity_suffix: str, amount: float) -> None:
        """Add amount to number entity."""
        entity_id = f"input_number.{self._dog_name}_{entity_suffix}"
        current_state = self.hass.states.get(entity_id)
        
        if current_state and current_state.state not in ["unknown", "unavailable"]:
            try:
                current_value = float(current_state.state)
                new_value = current_value + amount
                await self._safe_service_call("input_number", "set_value", {
                    "entity_id": entity_id,
                    "value": new_value
                })
            except (ValueError, TypeError) as e:
                _LOGGER.error("Error updating number entity %s: %s", entity_id, e)


# FEEDING BUTTONS

class PawControlFeedMorningButton(PawControlButtonBase):
    """Button to mark morning feeding."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "feed_morning")
        self._attr_icon = "mdi:weather-sunrise"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._set_boolean_state("feeding_morning", True)
            await self._increment_counter("feeding_morning_count")
            await self._set_datetime_now("last_feeding_morning")
            await self._add_to_number("daily_food_amount", 150)  # Default amount
            
            _LOGGER.info("Morning feeding recorded for %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to record morning feeding for %s: %s", self._dog_name, e)


class PawControlFeedLunchButton(PawControlButtonBase):
    """Button to mark lunch feeding."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "feed_lunch")
        self._attr_icon = "mdi:weather-sunny"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._set_boolean_state("feeding_lunch", True)
            await self._increment_counter("feeding_lunch_count")
            await self._set_datetime_now("last_feeding_lunch")
            await self._add_to_number("daily_food_amount", 100)
            
            _LOGGER.info("Lunch feeding recorded for %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to record lunch feeding for %s: %s", self._dog_name, e)


class PawControlFeedEveningButton(PawControlButtonBase):
    """Button to mark evening feeding."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "feed_evening")
        self._attr_icon = "mdi:weather-sunset"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._set_boolean_state("feeding_evening", True)
            await self._increment_counter("feeding_evening_count")
            await self._set_datetime_now("last_feeding_evening")
            await self._add_to_number("daily_food_amount", 150)
            
            _LOGGER.info("Evening feeding recorded for %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to record evening feeding for %s: %s", self._dog_name, e)


class PawControlFeedSnackButton(PawControlButtonBase):
    """Button to mark snack feeding."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "feed_snack")
        self._attr_icon = "mdi:bone"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._set_boolean_state("feeding_snack", True)
            await self._increment_counter("feeding_snack_count")
            await self._set_datetime_now("last_feeding_snack")
            await self._add_to_number("daily_food_amount", 50)
            
            _LOGGER.info("Snack feeding recorded for %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to record snack feeding for %s: %s", self._dog_name, e)


# ACTIVITY BUTTONS

class PawControlStartWalkButton(PawControlButtonBase):
    """Button to start a walk."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "start_walk")
        self._attr_icon = ICON_WALK

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._set_boolean_state("walk_in_progress", True)
            await self._set_boolean_state("outside", True)
            await self._set_datetime_now("last_walk")
            
            # Reset current walk metrics
            await self._safe_service_call("input_number", "set_value", {
                "entity_id": f"input_number.{self._dog_name}_current_walk_distance",
                "value": 0
            })
            await self._safe_service_call("input_number", "set_value", {
                "entity_id": f"input_number.{self._dog_name}_current_walk_duration",
                "value": 0
            })
            
            _LOGGER.info("Walk started for %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to start walk for %s: %s", self._dog_name, e)


class PawControlEndWalkButton(PawControlButtonBase):
    """Button to end a walk."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "end_walk")
        self._attr_icon = ICON_WALK

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._set_boolean_state("walk_in_progress", False)
            await self._set_boolean_state("walked_today", True)
            await self._increment_counter("walk_count")
            await self._add_to_number("daily_walk_duration", 30)  # Default 30 minutes
            
            _LOGGER.info("Walk ended for %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to end walk for %s: %s", self._dog_name, e)


class PawControlMarkOutsideButton(PawControlButtonBase):
    """Button to mark dog as outside."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "mark_outside")
        self._attr_icon = "mdi:door-open"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._set_boolean_state("outside", True)
            await self._increment_counter("outside_count")
            await self._set_datetime_now("last_outside")
            
            _LOGGER.info("Marked %s as outside", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to mark %s as outside: %s", self._dog_name, e)


class PawControlMarkPoopDoneButton(PawControlButtonBase):
    """Button to mark poop as done."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "mark_poop_done")
        self._attr_icon = "mdi:toilet"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._set_boolean_state("poop_done", True)
            await self._increment_counter("poop_count")
            await self._set_datetime_now("last_poop")
            
            _LOGGER.info("Poop marked as done for %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to mark poop done for %s: %s", self._dog_name, e)


# TRAINING BUTTONS

class PawControlStartTrainingButton(PawControlButtonBase):
    """Button to start training."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "start_training")
        self._attr_icon = ICON_TRAINING

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._set_boolean_state("training_session", True)
            await self._set_datetime_now("last_training")
            
            _LOGGER.info("Training started for %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to start training for %s: %s", self._dog_name, e)


class PawControlEndTrainingButton(PawControlButtonBase):
    """Button to end training."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "end_training")
        self._attr_icon = ICON_TRAINING

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._set_boolean_state("training_session", False)
            await self._increment_counter("training_count")
            await self._add_to_number("daily_training_duration", 15)  # Default 15 minutes
            
            _LOGGER.info("Training ended for %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to end training for %s: %s", self._dog_name, e)


# PLAY BUTTONS

class PawControlStartPlaytimeButton(PawControlButtonBase):
    """Button to start playtime."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "start_playtime")
        self._attr_icon = ICON_PLAY

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._set_boolean_state("played_today", True)
            await self._set_datetime_now("last_play")
            
            _LOGGER.info("Playtime started for %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to start playtime for %s: %s", self._dog_name, e)


class PawControlEndPlaytimeButton(PawControlButtonBase):
    """Button to end playtime."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "end_playtime")
        self._attr_icon = ICON_PLAY

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._increment_counter("play_count")
            await self._add_to_number("daily_play_duration", 20)  # Default 20 minutes
            
            _LOGGER.info("Playtime ended for %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to end playtime for %s: %s", self._dog_name, e)


# HEALTH BUTTONS

class PawControlHealthCheckButton(PawControlButtonBase):
    """Button for health check."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "health_check")
        self._attr_icon = ICON_HEALTH

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            # Set feeling well to true (assuming good health check)
            await self._set_boolean_state("feeling_well", True)
            
            # Update health notes
            await self._safe_service_call("input_text", "set_value", {
                "entity_id": f"input_text.{self._dog_name}_health_notes",
                "value": f"Gesundheitscheck durchgeführt am {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            })
            
            _LOGGER.info("Health check performed for %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to perform health check for %s: %s", self._dog_name, e)


class PawControlGiveMedicationButton(PawControlButtonBase):
    """Button to give medication."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "give_medication")
        self._attr_icon = "mdi:pill"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._set_boolean_state("medication_given", True)
            await self._increment_counter("medication_count")
            await self._set_datetime_now("last_medication")
            
            _LOGGER.info("Medication given to %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to record medication for %s: %s", self._dog_name, e)


# GPS BUTTONS

class PawControlUpdateGPSButton(PawControlButtonBase):
    """Button to update GPS location."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "update_gps")
        self._attr_icon = "mdi:crosshairs-gps"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            # Set GPS signal to 100% (simulated manual update)
            await self._safe_service_call("input_number", "set_value", {
                "entity_id": f"input_number.{self._dog_name}_gps_signal_strength",
                "value": 100
            })
            
            # Update GPS status
            await self._safe_service_call("input_text", "set_value", {
                "entity_id": f"input_text.{self._dog_name}_gps_tracker_status",
                "value": f"Manuell aktualisiert um {datetime.now().strftime('%H:%M')}"
            })
            
            _LOGGER.info("GPS updated for %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to update GPS for %s: %s", self._dog_name, e)


class PawControlStartWalkTrackingButton(PawControlButtonBase):
    """Button to start walk tracking."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "start_walk_tracking")
        self._attr_icon = "mdi:map-marker-path"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._set_boolean_state("walk_in_progress", True)
            await self._set_boolean_state("gps_tracking_enabled", True)
            
            # Reset walk metrics
            await self._safe_service_call("input_number", "set_value", {
                "entity_id": f"input_number.{self._dog_name}_current_walk_distance",
                "value": 0
            })
            
            _LOGGER.info("Walk tracking started for %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to start walk tracking for %s: %s", self._dog_name, e)


class PawControlEndWalkTrackingButton(PawControlButtonBase):
    """Button to end walk tracking."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "end_walk_tracking")
        self._attr_icon = "mdi:map-marker-path"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._set_boolean_state("walk_in_progress", False)
            
            # Update today's total from current walk
            current_distance_state = self.hass.states.get(f"input_number.{self._dog_name}_current_walk_distance")
            if current_distance_state and current_distance_state.state not in ["unknown", "unavailable"]:
                try:
                    current_distance = float(current_distance_state.state)
                    await self._add_to_number("walk_distance_today", current_distance)
                except (ValueError, TypeError):
                    pass
            
            await self._increment_counter("walk_count")
            
            _LOGGER.info("Walk tracking ended for %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to end walk tracking for %s: %s", self._dog_name, e)


# SYSTEM BUTTONS

class PawControlResetDailyDataButton(PawControlButtonBase):
    """Button to reset daily data."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "reset_daily_data")
        self._attr_icon = "mdi:refresh"
        self._attr_device_class = ButtonDeviceClass.RESTART

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            # Reset all boolean entities
            boolean_entities = [
                "feeding_morning", "feeding_lunch", "feeding_evening", "feeding_snack",
                "outside", "walked_today", "played_today", "poop_done", "training_session"
            ]
            
            for entity_suffix in boolean_entities:
                await self._set_boolean_state(entity_suffix, False)
            
            # Reset daily amounts
            number_entities = [
                ("daily_food_amount", 0),
                ("daily_walk_duration", 0),
                ("daily_play_duration", 0),
                ("daily_training_duration", 0),
                ("walk_distance_today", 0),
                ("current_walk_distance", 0),
                ("current_walk_duration", 0),
            ]
            
            for entity_suffix, value in number_entities:
                await self._safe_service_call("input_number", "set_value", {
                    "entity_id": f"input_number.{self._dog_name}_{entity_suffix}",
                    "value": value
                })
            
            # Reset counters
            counter_entities = [
                "walk_count", "play_count", "training_count", "poop_count"
            ]
            
            for entity_suffix in counter_entities:
                await self._safe_service_call("counter", "reset", {
                    "entity_id": f"counter.{self._dog_name}_{entity_suffix}"
                })
            
            _LOGGER.info("Daily data reset for %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to reset daily data for %s: %s", self._dog_name, e)


class PawControlEmergencyButton(PawControlButtonBase):
    """Button for emergency situations."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "emergency")
        self._attr_icon = "mdi:alert"
        self._attr_device_class = ButtonDeviceClass.RESTART

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._set_boolean_state("emergency_mode", True)
            await self._increment_counter("emergency_calls")
            
            # Set emergency contact time
            await self._set_datetime_now("emergency_contact_time")
            
            # Add emergency note
            await self._safe_service_call("input_text", "set_value", {
                "entity_id": f"input_text.{self._dog_name}_emergency_contact",
                "value": f"NOTFALL aktiviert um {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            })
            
            _LOGGER.warning("EMERGENCY activated for %s", self._dog_name)
        except Exception as e:
            _LOGGER.error("Failed to activate emergency for %s: %s", self._dog_name, e)


class PawControlVisitorModeButton(PawControlButtonBase):
    """Button to toggle visitor mode."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, dog_name, "visitor_mode")
        self._attr_icon = "mdi:account-group"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            # Toggle visitor mode
            visitor_state = self.hass.states.get(f"input_boolean.{self._dog_name}_visitor_mode_input")
            current_state = visitor_state.state == "on" if visitor_state else False
            
            await self._set_boolean_state("visitor_mode_input", not current_state)
            
            if not current_state:  # Turning on
                await self._set_datetime_now("visitor_start")
                await self._safe_service_call("input_text", "set_value", {
                    "entity_id": f"input_text.{self._dog_name}_visitor_name",
                    "value": f"Besucher ab {datetime.now().strftime('%H:%M')}"
                })
                _LOGGER.info("Visitor mode activated for %s", self._dog_name)
            else:  # Turning off
                await self._set_datetime_now("visitor_end")
                await self._safe_service_call("input_text", "set_value", {
                    "entity_id": f"input_text.{self._dog_name}_visitor_name",
                    "value": ""
                })
                _LOGGER.info("Visitor mode deactivated for %s", self._dog_name)
                
        except Exception as e:
            _LOGGER.error("Failed to toggle visitor mode for %s: %s", self._dog_name, e)
