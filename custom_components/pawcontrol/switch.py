"""Switch platform for Paw Control integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ICONS, ATTR_DOG_NAME, ATTR_LAST_UPDATED
from .coordinator import PawControlCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    dog_name = coordinator.dog_name
    
    entities = [
        # System switches
        PawControlEmergencyModeSwitch(coordinator, dog_name),
        PawControlVisitorModeSwitch(coordinator, dog_name),
        PawControlAutoWalkDetectionSwitch(coordinator, dog_name),
        
        # Activity switches
        PawControlWalkInProgressSwitch(coordinator, dog_name),
        PawControlTrainingSessionSwitch(coordinator, dog_name),
        PawControlPlaytimeSessionSwitch(coordinator, dog_name),
        
        # Health switches
        PawControlMedicationReminderSwitch(coordinator, dog_name),
        PawControlHealthMonitoringSwitch(coordinator, dog_name),
    ]
    
    async_add_entities(entities)


class PawControlSwitchBase(CoordinatorEntity, SwitchEntity):
    """Base class for Paw Control switches."""

    def __init__(
        self,
        coordinator: PawControlCoordinator,
        dog_name: str,
        switch_type: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._dog_name = dog_name
        self._switch_type = switch_type
        self._attr_unique_id = f"{DOMAIN}_{dog_name.lower()}_{switch_type}"
        self._attr_name = f"{dog_name.title()} {switch_type.replace('_', ' ').title()}"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._dog_name.lower())},
            "name": f"Paw Control - {self._dog_name}",
            "manufacturer": "Paw Control",
            "model": "Dog Management System",
            "sw_version": "1.0.0",
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


# SYSTEM SWITCHES

class PawControlEmergencyModeSwitch(PawControlSwitchBase):
    """Switch for emergency mode."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, dog_name, "emergency_mode")
        self._attr_icon = ICONS["emergency"]

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        try:
            emergency_state = self.hass.states.get(f"input_boolean.{self._dog_name}_emergency_mode")
            return emergency_state.state == "on" if emergency_state else False
        except Exception:
            return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on emergency mode."""
        try:
            # Activate emergency mode
            await self._safe_service_call("input_boolean", "turn_on", {
                "entity_id": f"input_boolean.{self._dog_name}_emergency_mode"
            })
            
            # Set emergency level to critical
            await self._safe_service_call("input_select", "select_option", {
                "entity_id": f"input_select.{self._dog_name}_emergency_level",
                "option": "Kritisch"
            })
            
            # Add emergency note
            await self._safe_service_call("input_text", "set_value", {
                "entity_id": f"input_text.{self._dog_name}_notes",
                "value": f"🚨 NOTFALL aktiviert um {datetime.now().strftime('%H:%M')}"
            })
            
            # Send notification
            if self.hass.services.has_service("persistent_notification", "create"):
                await self.hass.services.async_call(
                    "persistent_notification", "create",
                    {
                        "title": f"🚨 NOTFALL - {self._dog_name.title()}",
                        "message": "Notfallmodus aktiviert! Sofortige Aufmerksamkeit erforderlich!",
                        "notification_id": f"emergency_{self._dog_name}",
                    }
                )
            
            _LOGGER.warning("EMERGENCY MODE activated for %s", self._dog_name)
            
        except Exception as e:
            _LOGGER.error("Failed to activate emergency mode for %s: %s", self._dog_name, e)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off emergency mode."""
        try:
            # Deactivate emergency mode
            await self._safe_service_call("input_boolean", "turn_off", {
                "entity_id": f"input_boolean.{self._dog_name}_emergency_mode"
            })
            
            # Reset emergency level to normal
            await self._safe_service_call("input_select", "select_option", {
                "entity_id": f"input_select.{self._dog_name}_emergency_level",
                "option": "Normal"
            })
            
            # Add deactivation note
            await self._safe_service_call("input_text", "set_value", {
                "entity_id": f"input_text.{self._dog_name}_notes",
                "value": f"✅ Notfall beendet um {datetime.now().strftime('%H:%M')}"
            })
            
            _LOGGER.info("Emergency mode deactivated for %s", self._dog_name)
            
        except Exception as e:
            _LOGGER.error("Failed to deactivate emergency mode for %s: %s", self._dog_name, e)


class PawControlVisitorModeSwitch(PawControlSwitchBase):
    """Switch for visitor mode."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, dog_name, "visitor_mode")
        self._attr_icon = ICONS["visitor"]

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        try:
            visitor_state = self.hass.states.get(f"input_boolean.{self._dog_name}_visitor_mode_input")
            return visitor_state.state == "on" if visitor_state else False
        except Exception:
            return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on visitor mode."""
        try:
            # Activate visitor mode
            await self._safe_service_call("input_boolean", "turn_on", {
                "entity_id": f"input_boolean.{self._dog_name}_visitor_mode_input"
            })
            
            # Set visitor start time
            await self._safe_service_call("input_datetime", "set_datetime", {
                "entity_id": f"input_datetime.{self._dog_name}_visitor_start",
                "datetime": datetime.now().isoformat()
            })
            
            # Add visitor note
            await self._safe_service_call("input_text", "set_value", {
                "entity_id": f"input_text.{self._dog_name}_notes",
                "value": f"👥 Besuchsmodus aktiviert um {datetime.now().strftime('%H:%M')}"
            })
            
            _LOGGER.info("Visitor mode activated for %s", self._dog_name)
            
        except Exception as e:
            _LOGGER.error("Failed to activate visitor mode for %s: %s", self._dog_name, e)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off visitor mode."""
        try:
            # Deactivate visitor mode
            await self._safe_service_call("input_boolean", "turn_off", {
                "entity_id": f"input_boolean.{self._dog_name}_visitor_mode_input"
            })
            
            # Set visitor end time
            await self._safe_service_call("input_datetime", "set_datetime", {
                "entity_id": f"input_datetime.{self._dog_name}_visitor_end",
                "datetime": datetime.now().isoformat()
            })
            
            # Add deactivation note
            await self._safe_service_call("input_text", "set_value", {
                "entity_id": f"input_text.{self._dog_name}_notes",
                "value": f"👥 Besuchsmodus beendet um {datetime.now().strftime('%H:%M')}"
            })
            
            _LOGGER.info("Visitor mode deactivated for %s", self._dog_name)
            
        except Exception as e:
            _LOGGER.error("Failed to deactivate visitor mode for %s: %s", self._dog_name, e)


class PawControlAutoWalkDetectionSwitch(PawControlSwitchBase):
    """Switch for automatic walk detection."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, dog_name, "auto_walk_detection")
        self._attr_icon = ICONS["automation"]

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        try:
            auto_walk_state = self.hass.states.get(f"input_boolean.{self._dog_name}_auto_walk_detection")
            return auto_walk_state.state == "on" if auto_walk_state else False
        except Exception:
            return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on auto walk detection."""
        try:
            await self._safe_service_call("input_boolean", "turn_on", {
                "entity_id": f"input_boolean.{self._dog_name}_auto_walk_detection"
            })
            
            # Get GPS handler and enable auto detection
            gps_handler = self.hass.data[DOMAIN].get("gps_handler")
            if gps_handler:
                gps_handler._auto_walk_detection = True
            
            _LOGGER.info("Auto walk detection enabled for %s", self._dog_name)
            
        except Exception as e:
            _LOGGER.error("Failed to enable auto walk detection for %s: %s", self._dog_name, e)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off auto walk detection."""
        try:
            await self._safe_service_call("input_boolean", "turn_off", {
                "entity_id": f"input_boolean.{self._dog_name}_auto_walk_detection"
            })
            
            # Get GPS handler and disable auto detection
            gps_handler = self.hass.data[DOMAIN].get("gps_handler")
            if gps_handler:
                gps_handler._auto_walk_detection = False
            
            _LOGGER.info("Auto walk detection disabled for %s", self._dog_name)
            
        except Exception as e:
            _LOGGER.error("Failed to disable auto walk detection for %s: %s", self._dog_name, e)


# ACTIVITY SWITCHES

class PawControlWalkInProgressSwitch(PawControlSwitchBase):
    """Switch for walk in progress."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, dog_name, "walk_in_progress")
        self._attr_icon = ICONS["walk"]

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        try:
            walk_state = self.hass.states.get(f"input_boolean.{self._dog_name}_walk_in_progress")
            return walk_state.state == "on" if walk_state else False
        except Exception:
            return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Start walk tracking."""
        try:
            # Get GPS handler and start walk
            if "gps_handler" in self.hass.data[DOMAIN]:
                gps_handler = self.hass.data[DOMAIN]["gps_handler"]
                await gps_handler.async_start_walk("manual")
            else:
                # Fallback to basic entity update
                await self._safe_service_call("input_boolean", "turn_on", {
                    "entity_id": f"input_boolean.{self._dog_name}_walk_in_progress"
                })
                
                await self._safe_service_call("input_datetime", "set_datetime", {
                    "entity_id": f"input_datetime.{self._dog_name}_last_walk",
                    "datetime": datetime.now().isoformat()
                })
            
            _LOGGER.info("Walk started for %s", self._dog_name)
            
        except Exception as e:
            _LOGGER.error("Failed to start walk for %s: %s", self._dog_name, e)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """End walk tracking."""
        try:
            # Get GPS handler and end walk
            if "gps_handler" in self.hass.data[DOMAIN]:
                gps_handler = self.hass.data[DOMAIN]["gps_handler"]
                await gps_handler.async_end_walk()
            else:
                # Fallback to basic entity update
                await self._safe_service_call("input_boolean", "turn_off", {
                    "entity_id": f"input_boolean.{self._dog_name}_walk_in_progress"
                })
                
                await self._safe_service_call("input_boolean", "turn_on", {
                    "entity_id": f"input_boolean.{self._dog_name}_walked_today"
                })
                
                await self._safe_service_call("counter", "increment", {
                    "entity_id": f"counter.{self._dog_name}_walk_count"
                })
            
            _LOGGER.info("Walk ended for %s", self._dog_name)
            
        except Exception as e:
            _LOGGER.error("Failed to end walk for %s: %s", self._dog_name, e)


class PawControlTrainingSessionSwitch(PawControlSwitchBase):
    """Switch for training session."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, dog_name, "training_session")
        self._attr_icon = ICONS["training"]

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        try:
            training_state = self.hass.states.get(f"input_boolean.{self._dog_name}_training_session")
            return training_state.state == "on" if training_state else False
        except Exception:
            return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Start training session."""
        try:
            await self._safe_service_call("input_boolean", "turn_on", {
                "entity_id": f"input_boolean.{self._dog_name}_training_session"
            })
            
            await self._safe_service_call("input_datetime", "set_datetime", {
                "entity_id": f"input_datetime.{self._dog_name}_last_training",
                "datetime": datetime.now().isoformat()
            })
            
            _LOGGER.info("Training session started for %s", self._dog_name)
            
        except Exception as e:
            _LOGGER.error("Failed to start training session for %s: %s", self._dog_name, e)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """End training session."""
        try:
            await self._safe_service_call("input_boolean", "turn_off", {
                "entity_id": f"input_boolean.{self._dog_name}_training_session"
            })
            
            await self._safe_service_call("counter", "increment", {
                "entity_id": f"counter.{self._dog_name}_training_count"
            })
            
            _LOGGER.info("Training session ended for %s", self._dog_name)
            
        except Exception as e:
            _LOGGER.error("Failed to end training session for %s: %s", self._dog_name, e)


class PawControlPlaytimeSessionSwitch(PawControlSwitchBase):
    """Switch for playtime session."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, dog_name, "playtime_session")
        self._attr_icon = ICONS["play"]

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        try:
            playtime_state = self.hass.states.get(f"input_boolean.{self._dog_name}_playtime_session")
            return playtime_state.state == "on" if playtime_state else False
        except Exception:
            return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Start playtime session."""
        try:
            await self._safe_service_call("input_boolean", "turn_on", {
                "entity_id": f"input_boolean.{self._dog_name}_playtime_session"
            })
            
            await self._safe_service_call("input_datetime", "set_datetime", {
                "entity_id": f"input_datetime.{self._dog_name}_last_play",
                "datetime": datetime.now().isoformat()
            })
            
            _LOGGER.info("Playtime session started for %s", self._dog_name)
            
        except Exception as e:
            _LOGGER.error("Failed to start playtime session for %s: %s", self._dog_name, e)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """End playtime session."""
        try:
            await self._safe_service_call("input_boolean", "turn_off", {
                "entity_id": f"input_boolean.{self._dog_name}_playtime_session"
            })
            
            await self._safe_service_call("input_boolean", "turn_on", {
                "entity_id": f"input_boolean.{self._dog_name}_played_today"
            })
            
            await self._safe_service_call("counter", "increment", {
                "entity_id": f"counter.{self._dog_name}_play_count"
            })
            
            _LOGGER.info("Playtime session ended for %s", self._dog_name)
            
        except Exception as e:
            _LOGGER.error("Failed to end playtime session for %s: %s", self._dog_name, e)


# HEALTH SWITCHES

class PawControlMedicationReminderSwitch(PawControlSwitchBase):
    """Switch for medication reminders."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, dog_name, "medication_reminder")
        self._attr_icon = ICONS["medication"]

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        # This is a virtual switch - check if medication is due
        try:
            medication_state = self.hass.states.get(f"input_boolean.{self._dog_name}_medication_given")
            return medication_state.state == "off" if medication_state else True
        except Exception:
            return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Mark medication as needed (turn off given status)."""
        try:
            await self._safe_service_call("input_boolean", "turn_off", {
                "entity_id": f"input_boolean.{self._dog_name}_medication_given"
            })
            
            _LOGGER.info("Medication reminder enabled for %s", self._dog_name)
            
        except Exception as e:
            _LOGGER.error("Failed to enable medication reminder for %s: %s", self._dog_name, e)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Mark medication as given."""
        try:
            await self._safe_service_call("input_boolean", "turn_on", {
                "entity_id": f"input_boolean.{self._dog_name}_medication_given"
            })
            
            await self._safe_service_call("input_datetime", "set_datetime", {
                "entity_id": f"input_datetime.{self._dog_name}_last_medication",
                "datetime": datetime.now().isoformat()
            })
            
            await self._safe_service_call("counter", "increment", {
                "entity_id": f"counter.{self._dog_name}_medication_count"
            })
            
            _LOGGER.info("Medication given for %s", self._dog_name)
            
        except Exception as e:
            _LOGGER.error("Failed to mark medication as given for %s: %s", self._dog_name, e)


class PawControlHealthMonitoringSwitch(PawControlSwitchBase):
    """Switch for health monitoring."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, dog_name, "health_monitoring")
        self._attr_icon = ICONS["health"]

    @property
    def is_on(self) -> bool | None:
        """Return true if health monitoring is active."""
        # Always return True for now - health monitoring is always active
        return True

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable health monitoring."""
        # Health monitoring is always on, but we can update health score
        try:
            # Update health score to good value when enabled
            await self._safe_service_call("input_number", "set_value", {
                "entity_id": f"input_number.{self._dog_name}_health_score",
                "value": 8.0
            })
            
            _LOGGER.info("Health monitoring activated for %s", self._dog_name)
            
        except Exception as e:
            _LOGGER.error("Failed to activate health monitoring for %s: %s", self._dog_name, e)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable health monitoring."""
        # Health monitoring can't really be disabled, but we can lower the health score
        try:
            await self._safe_service_call("input_number", "set_value", {
                "entity_id": f"input_number.{self._dog_name}_health_score",
                "value": 5.0
            })
            
            _LOGGER.info("Health monitoring status updated for %s", self._dog_name)
            
        except Exception as e:
            _LOGGER.error("Failed to update health monitoring for %s: %s", self._dog_name, e)