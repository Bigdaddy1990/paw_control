"""Gemeinsame Basisklasse für Health-bezogene Entities."""

from homeassistant.helpers.entity import Entity
from ..const import DOMAIN


class PawControlHealthEntity(Entity):
    """Basisklasse für Health-Überwachungs-Entities."""

    def __init__(self, activity_logger, entry_id: str, name: str, suffix: str) -> None:
        self._activity_logger = activity_logger
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{suffix}_{entry_id}"

    @property
    def _latest_health(self):
        """Gibt den letzten Health-Eintrag zurück."""
        return self._activity_logger.get_latest("health")

    @property
    def extra_state_attributes(self):
        """Standard-Attribute enthalten den letzten Health-Eintrag."""
        return self._latest_health or {}
