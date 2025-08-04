# entities/number.py
from homeassistant.components.number import NumberEntity

from .base import PawControlBaseEntity
from ..helpers.entity import clamp_value

class PawControlNumberEntity(PawControlBaseEntity, NumberEntity):
    """Basisklasse für Number-Entities mit Validierung."""

    def __init__(
        self,
        coordinator,
        name: str,
        dog_name: str | None = None,
        unique_suffix: str | None = None,
        min_value: float | None = None,
        max_value: float | None = None,
    ) -> None:
        super().__init__(coordinator, name, dog_name, unique_suffix)
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value

    @property
    def native_value(self):
        return self._state

    async def async_set_native_value(self, value: float) -> None:
        """Setze den numerischen Wert innerhalb der Grenzen."""
        self._state = clamp_value(value, self.native_min_value, self.native_max_value)
