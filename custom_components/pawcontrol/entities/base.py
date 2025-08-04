# entities/base.py
from homeassistant.helpers.entity import Entity

class PawControlBaseEntity(Entity):
    """Basisklasse für alle Paw Control-Entities."""

    def __init__(self, coordinator, name):
        self._attr_name = name
        self._coordinator = coordinator
        self._state = None

    @property
    def available(self):
        """Verfügbarkeit, standardmäßig via Coordinator."""
        return getattr(self._coordinator, "last_update_success", True)

    async def async_update(self):
        """Standard-Update via Coordinator."""
        await self._coordinator.async_request_refresh()
        self._update_state()

    def _update_state(self):
        """Setzt self._state, kann überschrieben werden."""
        self._state = self._coordinator.data.get(self._attr_name)
