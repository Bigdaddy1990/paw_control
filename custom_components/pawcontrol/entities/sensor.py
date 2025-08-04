from .base import PawControlBaseEntity

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
        if unit:
            self._attr_native_unit_of_measurement = unit

    def _update_state(self):
        """Holt den State aus den Koordinatordaten."""
        self._state = self.coordinator.data.get(self._attr_name)

    @property
    def state(self):
        return self._state
