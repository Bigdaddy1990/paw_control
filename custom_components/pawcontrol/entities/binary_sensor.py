# entities/binary_sensor.py
from homeassistant.components.binary_sensor import BinarySensorEntity

from .base import PawControlBaseEntity
from ..helpers.entity import as_bool


class PawControlBinarySensorEntity(PawControlBaseEntity, BinarySensorEntity):
    """Basisklasse für Binary Sensor-Entities mit Konvertierung."""

    def __init__(
        self,
        coordinator,
        name: str | None = None,
        dog_name: str | None = None,
        unique_suffix: str | None = None,
        *,
        key: str | None = None,
        icon: str | None = None,
        device_class=None,
    ) -> None:
        super().__init__(
            coordinator,
            name,
            dog_name,
            unique_suffix,
            key=key,
            icon=icon,
        )
        if device_class:
            self._attr_device_class = device_class

    def _update_state(self) -> None:
        """Hole und konvertiere den Status aus den Koordinatordaten."""
        self._state = as_bool(self.coordinator.data.get(self._attr_name))

    @property
    def is_on(self) -> bool:
        return self._state
