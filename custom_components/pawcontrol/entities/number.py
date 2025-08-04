# entities/number.py
from homeassistant.components.number import NumberEntity
from .base import PawControlBaseEntity

class PawControlNumberEntity(PawControlBaseEntity, NumberEntity):
    """Basisklasse für Number-Entities."""

    @property
    def value(self):
        return self._state

    async def async_set_value(self, value: float):
        # Wert setzen
        pass
