# entities/button.py
"""Gemeinsame Basisklasse für Paw Control Buttons."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity

from .base import PawControlBaseEntity
from ..helpers.entity import format_name, get_icon
from ..utils import safe_service_call


class PawControlButtonEntity(PawControlBaseEntity, ButtonEntity):
    """Basisklasse für Button-Entities mit Namens- und Icon-Handling."""

    def __init__(
        self,
        coordinator,
        name: str | None = None,
        dog_name: str | None = None,
        unique_suffix: str | None = None,
        *,
        key: str | None = None,
        icon: str | None = None,
    ) -> None:
        if dog_name and key and not name:
            name = format_name(dog_name, key)
        if key and not unique_suffix:
            unique_suffix = key
        super().__init__(coordinator, name, dog_name, unique_suffix)
        self._attr_icon = icon or (key and get_icon(key))

    async def _safe_service_call(self, domain: str, service: str, data: dict) -> bool:
        """Hilfsfunktion für sichere Serviceaufrufe."""
        return await safe_service_call(self.hass, domain, service, data)

    async def async_press(self) -> None:  # pragma: no cover - muss in Unterklassen implementiert werden
        """Button-Logik in Unterklassen bereitstellen."""
        raise NotImplementedError
