"""Gemeinsame GPS-Basisklasse für alle Paw Control GPS-Entities."""

from homeassistant.helpers.entity import Entity
from ..helpers.gps import is_valid_gps_coords

class PawControlGpsEntity(Entity):
    """Basisklasse für GPS-Entities."""

    def __init__(self, name, coordinator):
        self._attr_name = name
        self._coordinator = coordinator
        self._state = None

    @property
    def available(self):
        """Entity ist verfügbar, wenn Koordinaten gültig sind."""
        data = self._coordinator.data.get(self._attr_name, {})
        return is_valid_gps_coords(data.get("lat"), data.get("lon"))

    async def async_update(self):
        """Daten beim Coordinator aktualisieren."""
        await self._coordinator.async_request_refresh()
        data = self._coordinator.data.get(self._attr_name, {})
        if is_valid_gps_coords(data.get("lat"), data.get("lon")):
            self._state = (data["lat"], data["lon"])
        else:
            self._state = None
