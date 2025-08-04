"""Basisklasse für DateTime-Entities."""

from __future__ import annotations

from homeassistant.components.datetime import DateTimeEntity

from .base import PawControlBaseEntity
from ..helpers.entity import parse_datetime


class PawControlDateTimeEntity(PawControlBaseEntity, DateTimeEntity):
    """Gemeinsame Funktionalität für DateTime-Entities."""

    @property
    def native_value(self):
        return parse_datetime(self._state)
