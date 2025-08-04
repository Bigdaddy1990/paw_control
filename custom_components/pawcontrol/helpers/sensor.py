from .base import PawControlBaseEntity
from .entities.sensor import PawControlSensorEntity

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["pawcontrol"]["coordinator"]
    entity_names = coordinator.data.keys()
    entities = [PawControlSensor(coordinator, name) for name in entity_names]
    async_add_entities(entities)

class PawControlSensor(PawControlSensorEntity):
    """Konkrete Sensor Entity."""

    @property
    def name(self):
        return f"{self._attr_name} Sensor"


class PawControlSensorEntity(PawControlBaseEntity):
    """Basisklasse für Sensor-Entities."""

    @property
    def state(self):
        return self._state