# entities/binary_sensor.py
from homeassistant.components.binary_sensor import BinarySensorEntity

from .base import PawControlBaseEntity
from ..helpers.entity import as_bool


class PawControlBinarySensorEntity(PawControlBaseEntity, BinarySensorEntity):
    """Basisklasse für Binary Sensor-Entities mit Konvertierung."""

    def _update_state(self) -> None:
        """Hole und konvertiere den Status aus den Koordinatordaten."""
        self._state = as_bool(self.coordinator.data.get(self._attr_name))

    @property
    def is_on(self) -> bool:
        return self._state
