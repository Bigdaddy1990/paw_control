# entities/switch.py
from homeassistant.components.switch import SwitchEntity
from .base import PawControlBaseEntity

class PawControlSwitchEntity(PawControlBaseEntity, SwitchEntity):
    """Basisklasse für Switch-Entities."""

    @property
    def is_on(self):
        return bool(self._state)

    async def async_turn_on(self, **kwargs):
        # Geräte einschalten
        pass

    async def async_turn_off(self, **kwargs):
        # Geräte ausschalten
        pass
