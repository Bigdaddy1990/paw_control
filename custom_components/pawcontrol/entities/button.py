# entities/button.py
from homeassistant.components.button import ButtonEntity
from .base import PawControlBaseEntity

class PawControlButtonEntity(PawControlBaseEntity, ButtonEntity):
    """Basisklasse für Button-Entities."""

    async def async_press(self):
        # Implementiere hier die Button-Logik
        pass
