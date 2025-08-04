# entities/text.py
from homeassistant.components.text import TextEntity
from .base import PawControlBaseEntity

class PawControlTextEntity(PawControlBaseEntity, TextEntity):
    """Basisklasse für Text-Entities."""

    @property
    def native_value(self):
        return self._state

    async def async_set_value(self, value: str):
        # Textwert setzen
        pass
