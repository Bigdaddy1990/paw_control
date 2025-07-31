"""Datetime platform for Paw Control integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.datetime import DateTimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.dt import now

from .const import DOMAIN, ICONS, ATTR_DOG_NAME, ATTR_LAST_UPDATED
from .coordinator import PawControlCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the datetime platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    dog_name = coordinator.dog_name
    
    entities = [
        # Feeding times (last)
        PawControlLastFeedingMorningDateTime(coordinator, dog_name),
        PawControlLastFeedingLunchDateTime(coordinator, dog_name),
        PawControlLastFeedingEveningDateTime(coordinator, dog_name),
        PawControlLastFeedingDateTime(coordinator, dog_name),
        
        # Feeding schedule (times)
        PawControlFeedingMorningTimeDateTime(coordinator, dog_name),
        PawControlFeedingLunchTimeDateTime(coordinator, dog_name),
        PawControlFeedingEveningTimeDateTime(coordinator, dog_name),
        
        # Activity times
        PawControlLastWalkDateTime(coordinator, dog_name),
        PawControlLastOutsideDateTime(coordinator, dog_name),
        PawControlLastPlayDateTime(coordinator, dog_name),
        PawControlLastTrainingDateTime(coordinator, dog_name),
        PawControlLastGroomingDateTime(coordinator, dog_name),
        PawControlLastActivityDateTime(coordinator, dog_name),
        
        # Health and vet
        PawControlLastVetVisitDateTime(coordinator, dog_name),
        PawControlNextVetAppointmentDateTime(coordinator, dog_name),
        PawControlLastMedicationDateTime(coordinator, dog_name),
        PawControlLastWeightCheckDateTime(coordinator, dog_name),
        
        # Visitor mode
        PawControlVisitorStartDateTime(coordinator, dog_name),
        PawControlVisitorEndDateTime(coordinator, dog_name),
        
        # Emergency
        PawControlEmergencyContactTimeDateTime(coordinator, dog_name),
    ]
    
    async_add_entities(entities)


class PawControlDateTimeBase(CoordinatorEntity, DateTimeEntity):
    """Base class for Paw Control datetime entities."""

    def __init__(
        self,
        coordinator: PawControlCoordinator,
        dog_name: str,
        datetime_type: str,
        entity_suffix: str,
        has_date: bool = True,
        has_time: bool = True,
    ) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator)
        self._dog_name = dog_name
        self._datetime_type = datetime_type
        self._entity_suffix = entity_suffix
        self._helper_entity_id = f"input_datetime.{dog_name}_{entity_suffix}"
        self._attr_unique_id = f"{DOMAIN}_{dog_name.lower()}_{datetime_type}"
        self._attr_name = f"{dog_name.title()} {datetime_type.replace('_', ' ').title()}"
        self._has_date = has_date
        self._has_time = has_time

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
            "helper_entity": self._helper_entity_id,
            "has_date": self._has_date,
            "has_time": self._has_time,
        }

    @property
    def native_value(self) -> datetime | None:
        """Return the current datetime value."""
        helper_state = self.hass.states.get(self._helper_entity_id)
        if helper_state and helper_state.state not in ["unknown", "unavailable"]:
            try:
                return datetime.fromisoformat(helper_state.state.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass
        return None

    async def async_set_value(self, value: datetime) -> None:
        """Set the datetime value."""
        try:
            await self.hass.services.async_call(
                "input_datetime", "set_datetime",
                {
                    "entity_id": self._helper_entity_id,
                    "datetime": value.isoformat()
                },
                blocking=True
            )
        except Exception as e:
            _LOGGER.error("Failed to set datetime for %s: %s", self._helper_entity_id, e)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.hass.states.get(self._helper_entity_id) is not None


# FEEDING TIMES (LAST)

class PawControlLastFeedingMorningDateTime(PawControlDateTimeBase):
    """DateTime entity for last morning feeding."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "last_feeding_morning", "last_feeding_morning")
        self._attr_icon = ICONS["morning"]


class PawControlLastFeedingLunchDateTime(PawControlDateTimeBase):
    """DateTime entity for last lunch feeding."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "last_feeding_lunch", "last_feeding_lunch")
        self._attr_icon = ICONS["lunch"]


class PawControlLastFeedingEveningDateTime(PawControlDateTimeBase):
    """DateTime entity for last evening feeding."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "last_feeding_evening", "last_feeding_evening")
        self._attr_icon = ICONS["evening"]


class PawControlLastFeedingDateTime(PawControlDateTimeBase):
    """DateTime entity for last feeding (any)."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "last_feeding", "last_feeding")
        self._attr_icon = ICONS["food"]


# FEEDING SCHEDULE (TIMES)

class PawControlFeedingMorningTimeDateTime(PawControlDateTimeBase):
    """DateTime entity for morning feeding time."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "feeding_morning_time", "feeding_morning_time", has_date=False, has_time=True)
        self._attr_icon = ICONS["morning"]


class PawControlFeedingLunchTimeDateTime(PawControlDateTimeBase):
    """DateTime entity for lunch feeding time."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "feeding_lunch_time", "feeding_lunch_time", has_date=False, has_time=True)
        self._attr_icon = ICONS["lunch"]


class PawControlFeedingEveningTimeDateTime(PawControlDateTimeBase):
    """DateTime entity for evening feeding time."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "feeding_evening_time", "feeding_evening_time", has_date=False, has_time=True)
        self._attr_icon = ICONS["evening"]


# ACTIVITY TIMES

class PawControlLastWalkDateTime(PawControlDateTimeBase):
    """DateTime entity for last walk."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "last_walk", "last_walk")
        self._attr_icon = ICONS["walk"]


class PawControlLastOutsideDateTime(PawControlDateTimeBase):
    """DateTime entity for last time outside."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "last_outside", "last_outside")
        self._attr_icon = ICONS["outside"]


class PawControlLastPlayDateTime(PawControlDateTimeBase):
    """DateTime entity for last play time."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "last_play", "last_play")
        self._attr_icon = ICONS["play"]


class PawControlLastTrainingDateTime(PawControlDateTimeBase):
    """DateTime entity for last training."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "last_training", "last_training")
        self._attr_icon = ICONS["training"]


class PawControlLastGroomingDateTime(PawControlDateTimeBase):
    """DateTime entity for last grooming."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "last_grooming", "last_grooming")
        self._attr_icon = ICONS["grooming"]


class PawControlLastActivityDateTime(PawControlDateTimeBase):
    """DateTime entity for last activity."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "last_activity", "last_activity")
        self._attr_icon = ICONS["status"]


# HEALTH AND VET

class PawControlLastVetVisitDateTime(PawControlDateTimeBase):
    """DateTime entity for last vet visit."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "last_vet_visit", "last_vet_visit")
        self._attr_icon = ICONS["vet"]


class PawControlNextVetAppointmentDateTime(PawControlDateTimeBase):
    """DateTime entity for next vet appointment."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "next_vet_appointment", "next_vet_appointment")
        self._attr_icon = ICONS["vet"]


class PawControlLastMedicationDateTime(PawControlDateTimeBase):
    """DateTime entity for last medication."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "last_medication", "last_medication")
        self._attr_icon = ICONS["medication"]


class PawControlLastWeightCheckDateTime(PawControlDateTimeBase):
    """DateTime entity for last weight check."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "last_weight_check", "last_weight_check")
        self._attr_icon = ICONS["weight"]


# VISITOR MODE

class PawControlVisitorStartDateTime(PawControlDateTimeBase):
    """DateTime entity for visitor start time."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "visitor_start", "visitor_start")
        self._attr_icon = ICONS["visitor"]


class PawControlVisitorEndDateTime(PawControlDateTimeBase):
    """DateTime entity for visitor end time."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "visitor_end", "visitor_end")
        self._attr_icon = ICONS["visitor"]


# EMERGENCY

class PawControlEmergencyContactTimeDateTime(PawControlDateTimeBase):
    """DateTime entity for emergency contact time."""

    def __init__(self, coordinator: PawControlCoordinator, dog_name: str) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator, dog_name, "emergency_contact_time", "emergency_contact_time")
        self._attr_icon = ICONS["emergency"]