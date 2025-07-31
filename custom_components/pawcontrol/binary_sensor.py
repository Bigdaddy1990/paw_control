"""Binary sensor platform for Paw Control integration - FIXED VERSION."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.event import Event

from .const import (
    DOMAIN,
    ICON_FOOD,
    ICON_WALK,
    ICON_SLEEP,
    ICON_PLAY,
    ICON_TRAINING,
    ICON_HEALTH,
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
    """Set up the binary sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    dog_name = coordinator.dog_name
    
    entities = [
        PawControlIsHungryBinarySensor(coordinator, dog_name),
        PawControlNeedsWalkBinarySensor(coordinator, dog_name),
        PawControlIsSleepingBinarySensor(coordinator, dog_name),
        PawControlIsPlayingBinarySensor(coordinator, dog_name),
        PawControlNeedsTrainingBinarySensor(coordinator, dog_name),
        PawControlIsSickBinarySensor(coordinator, dog_name),
        PawControlIsStressedBinarySensor(coordinator, dog_name),
        PawControlNeedsGroomingBinarySensor(coordinator, dog_name),
        PawControlIsOutsideBinarySensor(coordinator, dog_name),
        PawControlHasEatenBinarySensor(coordinator, dog_name),
        PawControlDailyTasksCompleteBinarySensor(coordinator, dog_name),
        PawControlVisitorModeBinarySensor(coordinator, dog_name),
        PawControlEmergencyModeBinarySensor(coordinator, dog_name),
        PawControlNeedsAttentionBinarySensor(coordinator, dog_name),
        PawControlGPSTrackingBinarySensor(coordinator, dog_name),
    ]
    
    async_add_entities(entities)


class PawControlBinarySensorBase(CoordinatorEntity, BinarySensorEntity):
    """Base class for Paw Control binary sensors."""

    def __init__(
        self,
        coordinator: PawControlDataUpdateCoordinator,
        dog_name: str,
        sensor_type: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._dog_name = dog_name
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{DOMAIN}_{dog_name.lower()}_{sensor_type}"
        self._attr_name = f"{dog_name} {sensor_type.replace('_', ' ').title()}"

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
        if not self.coordinator.data:
            return {}
        
        dog_profile = self.coordinator.data.get("dog_profile", {})
        return {
            ATTR_DOG_NAME: dog_profile.get("name", self._dog_name),
            ATTR_DOG_BREED: dog_profile.get("breed", ""),
            ATTR_DOG_AGE: dog_profile.get("age", 0),
            ATTR_DOG_WEIGHT: dog_profile.get("weight", 0),
            ATTR_LAST_UPDATED: datetime.now().isoformat(),
        }


class PawControlIsHungryBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for hunger status."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "is_hungry")
        self._attr_icon = ICON_FOOD
        self._attr_device_class = None
        
        # Set up state tracking for real-time updates
        self._feeding_entities = [
            f"input_boolean.{dog_name}_feeding_morning",
            f"input_boolean.{dog_name}_feeding_lunch",
            f"input_boolean.{dog_name}_feeding_evening",
        ]
        
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, self._feeding_entities, self._handle_feeding_change
            )
        )

    @callback
    def _handle_feeding_change(self, event: Event) -> None:
        """Handle feeding state changes."""
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        try:
            # Check if any feeding happened in last 4 hours
            current_time = datetime.now()
            
            for meal_type in ["morning", "lunch", "evening"]:
                entity_id = f"input_datetime.{self._dog_name}_last_feeding_{meal_type}"
                state = self.hass.states.get(entity_id)
                
                if state and state.state not in ["unknown", "unavailable"]:
                    try:
                        last_feeding = datetime.fromisoformat(state.state.replace("Z", "+00:00"))
                        time_since_feeding = current_time - last_feeding
                        
                        # If fed within last 4 hours, not hungry
                        if time_since_feeding < timedelta(hours=4):
                            return False
                    except ValueError:
                        continue
            
            # Check if any feeding boolean is currently on
            for entity_id in self._feeding_entities:
                state = self.hass.states.get(entity_id)
                if state and state.state == "on":
                    return False
            
            return True  # Hungry if no recent feeding
            
        except Exception as e:
            _LOGGER.error("Error calculating hunger status for %s: %s", self._dog_name, e)
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = super().extra_state_attributes
        
        try:
            # Add feeding information
            last_feeding_times = {}
            for meal_type in ["morning", "lunch", "evening"]:
                entity_id = f"input_datetime.{self._dog_name}_last_feeding_{meal_type}"
                state = self.hass.states.get(entity_id)
                if state and state.state not in ["unknown", "unavailable"]:
                    last_feeding_times[meal_type] = state.state
            
            attrs.update({
                "last_feeding_times": last_feeding_times,
                "daily_food_amount": self._get_number_value(f"input_number.{self._dog_name}_daily_food_amount"),
                "feeding_streak": self._get_number_value(f"input_number.{self._dog_name}_feeding_streak"),
            })
            
        except Exception as e:
            _LOGGER.error("Error getting hunger attributes for %s: %s", self._dog_name, e)
        
        return attrs

    def _get_number_value(self, entity_id: str) -> float:
        """Get number value from entity."""
        state = self.hass.states.get(entity_id)
        try:
            return float(state.state) if state and state.state not in ["unknown", "unavailable"] else 0.0
        except (ValueError, TypeError):
            return 0.0


class PawControlNeedsWalkBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for walk need status."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "needs_walk")
        self._attr_icon = ICON_WALK
        self._attr_device_class = None

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        try:
            # Check if walked today
            walked_today_entity = f"input_boolean.{self._dog_name}_walked_today"
            walked_state = self.hass.states.get(walked_today_entity)
            
            if walked_state and walked_state.state == "on":
                return False  # Already walked today
            
            # Check last walk time
            last_walk_entity = f"input_datetime.{self._dog_name}_last_walk"
            last_walk_state = self.hass.states.get(last_walk_entity)
            
            if last_walk_state and last_walk_state.state not in ["unknown", "unavailable"]:
                try:
                    last_walk = datetime.fromisoformat(last_walk_state.state.replace("Z", "+00:00"))
                    time_since_walk = datetime.now() - last_walk
                    
                    # Needs walk if more than 6 hours since last walk
                    return time_since_walk > timedelta(hours=6)
                except ValueError:
                    pass
            
            return True  # Needs walk if no recent walk recorded
            
        except Exception as e:
            _LOGGER.error("Error calculating walk need for %s: %s", self._dog_name, e)
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = super().extra_state_attributes
        
        try:
            attrs.update({
                "walk_count_today": self._get_counter_value(f"counter.{self._dog_name}_walk_count"),
                "daily_walk_duration": self._get_number_value(f"input_number.{self._dog_name}_daily_walk_duration"),
                "last_walk": self._get_datetime_value(f"input_datetime.{self._dog_name}_last_walk"),
                "walk_in_progress": self._get_boolean_value(f"input_boolean.{self._dog_name}_walk_in_progress"),
            })
            
        except Exception as e:
            _LOGGER.error("Error getting walk attributes for %s: %s", self._dog_name, e)
        
        return attrs

    def _get_counter_value(self, entity_id: str) -> int:
        """Get counter value."""
        state = self.hass.states.get(entity_id)
        try:
            return int(state.state) if state and state.state not in ["unknown", "unavailable"] else 0
        except (ValueError, TypeError):
            return 0

    def _get_number_value(self, entity_id: str) -> float:
        """Get number value."""
        state = self.hass.states.get(entity_id)
        try:
            return float(state.state) if state and state.state not in ["unknown", "unavailable"] else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _get_datetime_value(self, entity_id: str) -> str | None:
        """Get datetime value."""
        state = self.hass.states.get(entity_id)
        return state.state if state and state.state not in ["unknown", "unavailable"] else None

    def _get_boolean_value(self, entity_id: str) -> bool:
        """Get boolean value."""
        state = self.hass.states.get(entity_id)
        return state.state == "on" if state else False


class PawControlIsSleepingBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for sleeping status."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "is_sleeping")
        self._attr_icon = ICON_SLEEP
        self._attr_device_class = None

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        try:
            # Simple logic: sleeping between 22:00 and 06:00
            current_time = datetime.now().time()
            
            # Check if it's sleep time (22:00 - 06:00)
            if current_time.hour >= 22 or current_time.hour <= 6:
                # Check if dog is not currently active
                outside_state = self.hass.states.get(f"input_boolean.{self._dog_name}_outside")
                play_state = self.hass.states.get(f"input_boolean.{self._dog_name}_played_today")
                
                if outside_state and outside_state.state == "on":
                    return False  # Not sleeping if outside
                
                return True  # Likely sleeping
            
            return False  # Not sleep time
            
        except Exception as e:
            _LOGGER.error("Error calculating sleep status for %s: %s", self._dog_name, e)
            return None


class PawControlIsPlayingBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for playing status."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "is_playing")
        self._attr_icon = ICON_PLAY
        self._attr_device_class = None

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        try:
            # Check if played recently (within last hour)
            last_play_entity = f"input_datetime.{self._dog_name}_last_play"
            last_play_state = self.hass.states.get(last_play_entity)
            
            if last_play_state and last_play_state.state not in ["unknown", "unavailable"]:
                try:
                    last_play = datetime.fromisoformat(last_play_state.state.replace("Z", "+00:00"))
                    time_since_play = datetime.now() - last_play
                    
                    return time_since_play < timedelta(hours=1)
                except ValueError:
                    pass
            
            # Check if played today boolean is on
            played_today_state = self.hass.states.get(f"input_boolean.{self._dog_name}_played_today")
            return played_today_state.state == "on" if played_today_state else False
            
        except Exception as e:
            _LOGGER.error("Error calculating play status for %s: %s", self._dog_name, e)
            return None


class PawControlNeedsTrainingBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for training need status."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "needs_training")
        self._attr_icon = ICON_TRAINING
        self._attr_device_class = None

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        try:
            # Check if trained today
            training_session_state = self.hass.states.get(f"input_boolean.{self._dog_name}_training_session")
            if training_session_state and training_session_state.state == "on":
                return False  # Currently in training or trained today
            
            # Check training count today
            training_count_state = self.hass.states.get(f"counter.{self._dog_name}_training_count")
            if training_count_state and training_count_state.state not in ["unknown", "unavailable"]:
                try:
                    training_count = int(training_count_state.state)
                    return training_count == 0  # Needs training if count is 0
                except ValueError:
                    pass
            
            return True  # Default to needs training
            
        except Exception as e:
            _LOGGER.error("Error calculating training need for %s: %s", self._dog_name, e)
            return None


class PawControlIsSickBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for sick status."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "is_sick")
        self._attr_icon = ICON_HEALTH
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        try:
            # Check health status
            health_status_state = self.hass.states.get(f"input_select.{self._dog_name}_health_status")
            if health_status_state and health_status_state.state not in ["unknown", "unavailable"]:
                # Consider sick if health status is bad
                sick_statuses = ["Schlecht", "Krank", "Sehr schlecht"]
                return health_status_state.state in sick_statuses
            
            # Check if feeling well boolean is off
            feeling_well_state = self.hass.states.get(f"input_boolean.{self._dog_name}_feeling_well")
            if feeling_well_state:
                return feeling_well_state.state == "off"
            
            return False  # Default to not sick
            
        except Exception as e:
            _LOGGER.error("Error calculating sick status for %s: %s", self._dog_name, e)
            return None


class PawControlIsStressedBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for stressed status."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "is_stressed")
        self._attr_icon = "mdi:emoticon-sad"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        try:
            # Check mood
            mood_state = self.hass.states.get(f"input_select.{self._dog_name}_mood")
            if mood_state and mood_state.state not in ["unknown", "unavailable"]:
                stressed_moods = ["😟 Traurig", "😠 Ärgerlich", "😰 Ängstlich"]
                return mood_state.state in stressed_moods
            
            return False  # Default to not stressed
            
        except Exception as e:
            _LOGGER.error("Error calculating stress status for %s: %s", self._dog_name, e)
            return None


class PawControlNeedsGroomingBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for grooming need status."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "needs_grooming")
        self._attr_icon = "mdi:shower"
        self._attr_device_class = None

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        try:
            # Check needs grooming boolean
            needs_grooming_state = self.hass.states.get(f"input_boolean.{self._dog_name}_needs_grooming")
            if needs_grooming_state:
                return needs_grooming_state.state == "on"
            
            # Check last grooming date
            last_grooming_state = self.hass.states.get(f"input_datetime.{self._dog_name}_last_grooming")
            if last_grooming_state and last_grooming_state.state not in ["unknown", "unavailable"]:
                try:
                    last_grooming = datetime.fromisoformat(last_grooming_state.state.replace("Z", "+00:00"))
                    time_since_grooming = datetime.now() - last_grooming
                    
                    # Needs grooming if more than 4 weeks
                    return time_since_grooming > timedelta(weeks=4)
                except ValueError:
                    pass
            
            return False  # Default to not needing grooming
            
        except Exception as e:
            _LOGGER.error("Error calculating grooming need for %s: %s", self._dog_name, e)
            return None


class PawControlIsOutsideBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for outside status."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "is_outside")
        self._attr_icon = "mdi:home-export-outline"
        self._attr_device_class = BinarySensorDeviceClass.PRESENCE

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        try:
            # Check outside boolean
            outside_state = self.hass.states.get(f"input_boolean.{self._dog_name}_outside")
            if outside_state:
                return outside_state.state == "on"
            
            # Check walk in progress
            walk_progress_state = self.hass.states.get(f"input_boolean.{self._dog_name}_walk_in_progress")
            if walk_progress_state:
                return walk_progress_state.state == "on"
            
            return False
            
        except Exception as e:
            _LOGGER.error("Error calculating outside status for %s: %s", self._dog_name, e)
            return None


class PawControlHasEatenBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for eaten status."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "has_eaten")
        self._attr_icon = ICON_FOOD
        self._attr_device_class = None

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        try:
            # Check if any feeding boolean is on
            feeding_entities = [
                f"input_boolean.{self._dog_name}_feeding_morning",
                f"input_boolean.{self._dog_name}_feeding_lunch",
                f"input_boolean.{self._dog_name}_feeding_evening",
            ]
            
            for entity_id in feeding_entities:
                state = self.hass.states.get(entity_id)
                if state and state.state == "on":
                    return True
            
            return False
            
        except Exception as e:
            _LOGGER.error("Error calculating eaten status for %s: %s", self._dog_name, e)
            return None


class PawControlDailyTasksCompleteBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for daily tasks completion."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "daily_tasks_complete")
        self._attr_icon = "mdi:check-circle"
        self._attr_device_class = None

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        try:
            # Check if main tasks are done
            fed_state = self.hass.states.get(f"input_boolean.{self._dog_name}_feeding_morning")
            outside_state = self.hass.states.get(f"input_boolean.{self._dog_name}_outside")
            poop_state = self.hass.states.get(f"input_boolean.{self._dog_name}_poop_done")
            
            fed = fed_state.state == "on" if fed_state else False
            outside = outside_state.state == "on" if outside_state else False
            poop = poop_state.state == "on" if poop_state else False
            
            # All main tasks complete
            return fed and outside and poop
            
        except Exception as e:
            _LOGGER.error("Error calculating task completion for %s: %s", self._dog_name, e)
            return None


class PawControlVisitorModeBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for visitor mode."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "visitor_mode")
        self._attr_icon = "mdi:account-group"
        self._attr_device_class = None

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        try:
            visitor_state = self.hass.states.get(f"input_boolean.{self._dog_name}_visitor_mode_input")
            return visitor_state.state == "on" if visitor_state else False
            
        except Exception as e:
            _LOGGER.error("Error calculating visitor mode for %s: %s", self._dog_name, e)
            return None


class PawControlEmergencyModeBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for emergency mode."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "emergency_mode")
        self._attr_icon = "mdi:alert"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        try:
            emergency_state = self.hass.states.get(f"input_boolean.{self._dog_name}_emergency_mode")
            return emergency_state.state == "on" if emergency_state else False
            
        except Exception as e:
            _LOGGER.error("Error calculating emergency mode for %s: %s", self._dog_name, e)
            return None


class PawControlNeedsAttentionBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for needs attention status."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "needs_attention")
        self._attr_icon = "mdi:bell-alert"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        try:
            # Check multiple conditions that require attention
            
            # 1. Not fed for too long
            last_fed_entity = f"input_datetime.{self._dog_name}_last_feeding_morning"
            last_fed_state = self.hass.states.get(last_fed_entity)
            if last_fed_state and last_fed_state.state not in ["unknown", "unavailable"]:
                try:
                    last_fed = datetime.fromisoformat(last_fed_state.state.replace("Z", "+00:00"))
                    if datetime.now() - last_fed > timedelta(hours=12):
                        return True
                except ValueError:
                    pass
            
            # 2. Not outside for too long
            last_outside_entity = f"input_datetime.{self._dog_name}_last_outside"
            last_outside_state = self.hass.states.get(last_outside_entity)
            if last_outside_state and last_outside_state.state not in ["unknown", "unavailable"]:
                try:
                    last_outside = datetime.fromisoformat(last_outside_state.state.replace("Z", "+00:00"))
                    if datetime.now() - last_outside > timedelta(hours=8):
                        return True
                except ValueError:
                    pass
            
            # 3. Health issues
            sick_state = self.hass.states.get(f"binary_sensor.{self._dog_name}_is_sick")
            if sick_state and sick_state.state == "on":
                return True
            
            # 4. Emergency mode
            emergency_state = self.hass.states.get(f"input_boolean.{self._dog_name}_emergency_mode")
            if emergency_state and emergency_state.state == "on":
                return True
            
            return False
            
        except Exception as e:
            _LOGGER.error("Error calculating attention need for %s: %s", self._dog_name, e)
            return None


class PawControlGPSTrackingBinarySensor(PawControlBinarySensorBase):
    """Binary sensor for GPS tracking status."""

    def __init__(self, coordinator: PawControlDataUpdateCoordinator, dog_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, dog_name, "gps_tracking")
        self._attr_icon = "mdi:crosshairs-gps"
        self._attr_device_class = None

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        try:
            # Check if GPS tracking is enabled
            gps_enabled_state = self.hass.states.get(f"input_boolean.{self._dog_name}_gps_tracking_enabled")
            if not gps_enabled_state or gps_enabled_state.state != "on":
                return False
            
            # Check GPS signal strength
            signal_state = self.hass.states.get(f"input_number.{self._dog_name}_gps_signal_strength")
            if signal_state and signal_state.state not in ["unknown", "unavailable"]:
                try:
                    signal_strength = float(signal_state.state)
                    return signal_strength > 20  # GPS active if signal > 20%
                except ValueError:
                    pass
            
            return False
            
        except Exception as e:
            _LOGGER.error("Error calculating GPS tracking status for %s: %s", self._dog_name, e)
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = super().extra_state_attributes
        
        try:
            attrs.update({
                "gps_signal_strength": self._get_number_value(f"input_number.{self._dog_name}_gps_signal_strength"),
                "gps_battery_level": self._get_number_value(f"input_number.{self._dog_name}_gps_battery_level"),
                "walk_in_progress": self._get_boolean_value(f"input_boolean.{self._dog_name}_walk_in_progress"),
                "current_location": self._get_text_value(f"input_text.{self._dog_name}_current_location"),
            })
            
        except Exception as e:
            _LOGGER.error("Error getting GPS tracking attributes for %s: %s", self._dog_name, e)
        
        return attrs

    def _get_number_value(self, entity_id: str) -> float:
        """Get number value."""
        state = self.hass.states.get(entity_id)
        try:
            return float(state.state) if state and state.state not in ["unknown", "unavailable"] else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _get_boolean_value(self, entity_id: str) -> bool:
        """Get boolean value."""
        state = self.hass.states.get(entity_id)
        return state.state == "on" if state else False

    def _get_text_value(self, entity_id: str) -> str:
        """Get text value."""
        state = self.hass.states.get(entity_id)
        return state.state if state and state.state not in ["unknown", "unavailable"] else ""
