"""Hilfsfunktionen für Entity-bezogene Aufgaben."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pawcontrol.const import ATTR_DOG_NAME, ATTR_LAST_UPDATED, ICONS

from .json import JSONMutableMapping, ensure_json_mapping


def get_icon_by_status(status: str) -> str:
    """Mappe einen Status auf ein Icon."""
    icons = {
        "online": "mdi:check-circle",
        "offline": "mdi:alert-circle",
        "unknown": "mdi:help-circle",
    }
    return icons.get(status, "mdi:help-circle")


def get_icon(key: str, default: str | None = "mdi:help-circle") -> str:
    """Lese ein Icon aus der zentralen ICONS-Map."""
    return ICONS.get(key, default)


def format_name(dog_name: str, key: str) -> str:
    """Erzeuge einen konsistent formatierten Entity-Namen."""
    return f"{dog_name.title()} {key.replace('_', ' ').title()}"


def build_attributes(dog_name: str | None = None, **extra: Any) -> JSONMutableMapping:
    """Erzeuge ein Attribut-Dictionary mit Standardwerten."""
    attrs: dict[str, Any] = {ATTR_LAST_UPDATED: datetime.now().isoformat()}
    if dog_name:
        attrs[ATTR_DOG_NAME] = dog_name
    attrs.update(extra)
    return ensure_json_mapping(attrs)


def parse_datetime(value: str | None) -> datetime | None:
    """Konvertiere eine ISO-8601-Zeichenkette in ein ``datetime``-Objekt."""
    if not value or value in ("unknown", "unavailable"):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def clamp_string(value: str | None, max_length: int) -> str:
    """Begrenze eine Zeichenkette auf eine bestimmte Länge."""
    if value is None:
        return ""
    return str(value)[:max_length]


def clamp_value(
    value: float, min_value: float | None = None, max_value: float | None = None
) -> float:
    """Begrenze einen numerischen Wert auf einen Bereich."""
    if min_value is not None and value < min_value:
        return min_value
    if max_value is not None and value > max_value:
        return max_value
    return value


def ensure_option(option: str, options: list[str]) -> str:
    """Validiere eine Auswahl gegen eine Optionsliste."""
    if option in options:
        return option
    return options[0] if options else option


def as_bool(value: Any) -> bool:
    """Konvertiere verschiedene Darstellungen zu einem booleschen Wert."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "on", "1", "yes")
    return bool(value)
