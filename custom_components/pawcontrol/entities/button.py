# entities/button.py
"""Gemeinsame Basisklasse für Paw Control Buttons."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity

from .base import PawControlBaseEntity
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
        super().__init__(
            coordinator,
            name,
            dog_name,
            unique_suffix,
            key=key,
            icon=icon,
        )

    async def _safe_service_call(self, domain: str, service: str, data: dict) -> bool:
        """Hilfsfunktion für sichere Serviceaufrufe."""
        return await safe_service_call(self.hass, domain, service, data)

    async def async_press(self) -> None:  # pragma: no cover - muss in Unterklassen implementiert werden
        """Button-Logik in Unterklassen bereitstellen."""
        raise NotImplementedError
