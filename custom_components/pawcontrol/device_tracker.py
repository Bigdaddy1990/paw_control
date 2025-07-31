"""Device tracker platform for Paw Control - GPS TRACKING."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ICONS, ATTR_DOG_NAME, ATTR_GPS_ACCURACY, ATTR_WALK_STATS
from .coordinator import PawControlCoordinator
from .gps_handler import PawControlGPSHandler

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the device tracker platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    dog_name = coordinator.dog_name
    
    # Create GPS handler if not exists
    if "gps_handler" not in hass.data[DOMAIN][config_entry.entry_id]:
        gps_handler = PawControlGPSHandler(hass, dog_name, config_entry.data)
        await gps_handler.async_setup()
        hass.data[DOMAIN][config_entry.entry_id]["gps_handler"] = gps_handler
    else:
        gps_handler = hass.data[DOMAIN][config_entry.entry_id]["gps_handler"]
    
    entities = [
        PawControlDeviceTracker(coordinator, dog_name, gps_handler),
    ]
    
    async_add_entities(entities)


class PawControlDeviceTracker(CoordinatorEntity, TrackerEntity):
    """GPS device tracker for the dog."""

    def __init__(
        self,
        coordinator: PawControlCoordinator,
        dog_name: str,
        gps_handler: PawControlGPSHandler,
    ) -> None:
        """Initialize the device tracker."""
        super().__init__(coordinator)
        self._dog_name = dog_name
        self._gps_handler = gps_handler
        self._attr_unique_id = f"{DOMAIN}_{dog_name.lower()}_device_tracker"
        self._attr_name = f"{dog_name.title()} GPS Tracker"
        self._attr_icon = ICONS["gps"]

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._dog_name.lower())},
            "name": f"Paw Control - {self._dog_name}",
            "manufacturer": "Paw Control",
            "model": "Dog GPS Tracker",
            "sw_version": "1.0.0",
        }

    @property
    def source_type(self) -> SourceType:
        """Return the source type of the device tracker."""
        return SourceType.GPS

    @property
    def latitude(self) -> Optional[float]:
        """Return latitude value of the device."""
        location = self._gps_handler.get_current_location()
        return location[0] if location else None

    @property
    def longitude(self) -> Optional[float]:
        """Return longitude value of the device."""
        location = self._gps_handler.get_current_location()
        return location[1] if location else None

    @property
    def location_accuracy(self) -> int:
        """Return the GPS accuracy of the device."""
        gps_status = self._gps_handler.get_gps_status()
        return int(gps_status.get("accuracy", 50))

    @property
    def location_name(self) -> Optional[str]:
        """Return a location name for the current location of the device."""
        location = self._gps_handler.get_current_location()
        home_location = self._gps_handler.get_home_location()
        
        if not location or not home_location:
            return None
        
        # Calculate distance from home
        from .utils import calculate_distance
        distance = calculate_distance(home_location, location)
        
        if distance <= 100:  # Within 100m of home
            return "Zuhause"
        elif distance <= 500:  # Within 500m of home
            return "In der Nähe von Zuhause"
        elif self._gps_handler.is_walk_active():
            return "Beim Spaziergang"
        else:
            return "Unterwegs"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return extra state attributes."""
        gps_status = self._gps_handler.get_gps_status()
        walk_stats = self._gps_handler.get_walk_stats()
        
        attrs = {
            ATTR_DOG_NAME: self._dog_name,
            ATTR_GPS_ACCURACY: gps_status.get("accuracy", 0),
            "gps_source": gps_status.get("source_type", "unknown"),
            "last_gps_update": gps_status.get("last_update"),
            "is_moving": gps_status.get("is_moving", False),
            "current_speed_kmh": round(gps_status.get("current_speed", 0), 1),
            "auto_walk_detection": gps_status.get("auto_walk_detection", False),
        }
        
        # Add walk stats if active
        if walk_stats:
            attrs[ATTR_WALK_STATS] = walk_stats
        
        # Add home distance if available
        location = self._gps_handler.get_current_location()
        home_location = self._gps_handler.get_home_location()
        if location and home_location:
            from .utils import calculate_distance
            home_distance = calculate_distance(home_location, location)
            attrs["home_distance_m"] = int(home_distance)
        
        return attrs

    @property
    def battery_level(self) -> Optional[int]:
        """Return the battery level of the device tracker."""
        # Try to get battery level from GPS battery entity
        battery_entity = f"input_number.{self._dog_name}_gps_battery_level"
        battery_state = self.hass.states.get(battery_entity)
        
        if battery_state and battery_state.state not in ["unknown", "unavailable"]:
            try:
                return int(float(battery_state.state))
            except (ValueError, TypeError):
                pass
        
        return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        gps_status = self._gps_handler.get_gps_status()
        last_update = gps_status.get("last_update")
        
        if not last_update:
            return False
        
        try:
            last_update_dt = datetime.fromisoformat(last_update.replace("Z", "+00:00"))
            time_since_update = (datetime.now() - last_update_dt).total_seconds()
            
            # Consider available if updated within last 30 minutes
            return time_since_update <= 1800
        except (ValueError, TypeError):
            return False