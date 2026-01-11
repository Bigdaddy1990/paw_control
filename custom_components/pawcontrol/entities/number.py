# entities/number.py
from homeassistant.components.number import NumberEntity

from pawcontrol.helpers.entity import clamp_value

from .base import PawControlBaseEntity


class PawControlNumberEntity(PawControlBaseEntity, NumberEntity):
    """Basisklasse für Number-Entities mit Validierung."""

    def __init__(
        self,
        coordinator,
        name: str | None = None,
        dog_name: str | None = None,
        unique_suffix: str | None = None,
        *,
        key: str | None = None,
        icon: str | None = None,
        min_value: float | None = None,
        max_value: float | None = None,
        unit: str | None = None,
        device_class=None,
        step: float | None = None,
        mode: str | None = None,
        state_class: str | None = None,
    ) -> None:
        super().__init__(
            coordinator,
            name,
            dog_name,
            unique_suffix,
            key=key,
            icon=icon,
        )
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        if unit:
            self._attr_native_unit_of_measurement = unit
        if device_class:
            self._attr_device_class = device_class
        if step is not None:
            self._attr_native_step = step
        if mode:
            self._attr_mode = mode
        if state_class:
            self._attr_state_class = state_class

    @property
    def native_value(self):
        return self._state

    async def async_set_native_value(self, value: float) -> None:
        """Setze den numerischen Wert innerhalb der Grenzen."""
        self._state = clamp_value(value, self.native_min_value, self.native_max_value)
