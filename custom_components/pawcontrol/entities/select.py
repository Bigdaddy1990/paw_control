# entities/select.py
from homeassistant.components.select import SelectEntity
from .base import PawControlBaseEntity

class PawControlSelectEntity(PawControlBaseEntity, SelectEntity):
    """Basisklasse für Select-Entities."""

    @property
    def current_option(self):
        return self._state

    async def async_select_option(self, option: str):
        # Option setzen
        pass

    @property
    def options(self):
        # Rückgabe der verfügbaren Optionen
        return []
