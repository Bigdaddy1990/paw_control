# entities/datetime.py
from homeassistant.components.datetime import DateTimeEntity
from .base import PawControlBaseEntity

class PawControlDateTimeEntity(PawControlBaseEntity, DateTimeEntity):
    """Basisklasse für DateTime-Entities."""

    @property
    def native_value(self):
        return self._state
