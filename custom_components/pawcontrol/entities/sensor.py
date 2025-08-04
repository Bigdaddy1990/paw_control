from .base import PawControlBaseEntity
from ..helpers.entity import get_icon, format_name

class PawControlSensorEntity(PawControlBaseEntity):
    """Basisklasse für alle Sensoren mit gemeinsamer Initialisierung."""

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
        unit: str | None = None,
    ) -> None:
        if dog_name and key and not name:
            name = format_name(dog_name, key)
        if key and not unique_suffix:
            unique_suffix = key
        super().__init__(coordinator, name, dog_name, unique_suffix)
        self._attr_icon = icon or (key and get_icon(key))
        if device_class:
            self._attr_device_class = device_class
        if unit:
            self._attr_native_unit_of_measurement = unit

    def _update_state(self):
        """Holt den State aus den Koordinatordaten."""
        self._state = self.coordinator.data.get(self._attr_name)

    @property
    def state(self):
        return self._state
