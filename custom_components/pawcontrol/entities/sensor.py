from .base import PawControlBaseEntity

class PawControlSensorEntity(PawControlBaseEntity):
    """Basisklasse für alle Sensoren."""

    def _update_state(self):
        # Holt den State aus den Koordinatordaten
        self._state = self._coordinator.data.get(self._attr_name)

    @property
    def state(self):
        return self._state
