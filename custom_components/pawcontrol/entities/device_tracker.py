# entities/device_tracker.py
from homeassistant.components.device_tracker import TrackerEntity
from .base import PawControlBaseEntity

class PawControlDeviceTrackerEntity(PawControlBaseEntity, TrackerEntity):
    """Basisklasse für Device Tracker-Entities."""

    @property
    def latitude(self):
        return self._state.get("lat") if self._state else None

    @property
    def longitude(self):
        return self._state.get("lon") if self._state else None

    @property
    def source_type(self):
        return "gps"
