"""Basisklasse für DateTime-Entities."""

from __future__ import annotations

from homeassistant.components.datetime import DateTimeEntity

from .base import PawControlBaseEntity
from ..helpers.entity import parse_datetime, format_name, get_icon


class PawControlDateTimeEntity(PawControlBaseEntity, DateTimeEntity):
    """Gemeinsame Funktionalität für DateTime-Entities."""

    def __init__(
        self,
        coordinator,
        name: str | None = None,
        dog_name: str | None = None,
        unique_suffix: str | None = None,
        *,
        key: str | None = None,
        icon: str | None = None,
        has_date: bool = True,
        has_time: bool = True,
    ) -> None:
        if dog_name and key and not name:
            name = format_name(dog_name, key)
        if key and not unique_suffix:
            unique_suffix = key
        super().__init__(coordinator, name, dog_name, unique_suffix)
        if icon or key:
            self._attr_icon = icon or get_icon(key)
        self._attr_has_date = has_date
        self._attr_has_time = has_time

    @property
    def native_value(self):
        return parse_datetime(self._state)
