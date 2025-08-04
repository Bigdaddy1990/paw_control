# entities/binary_sensor.py
from homeassistant.components.binary_sensor import BinarySensorEntity
from .base import PawControlBaseEntity

class PawControlBinarySensorEntity(PawControlBaseEntity, BinarySensorEntity):
    """Basisklasse für Binary Sensor-Entities."""

    @property
    def is_on(self):
        return bool(self._state)
