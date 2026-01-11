"""JSON helper types and normalization for Paw Control."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any

from homeassistant.util.json import JsonValueType


def _normalise_json(value: Any) -> JsonValueType:
    """Normalise values into JSON-compatible types."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, timedelta):
        return value.total_seconds()
    if isinstance(value, Enum):
        return _normalise_json(value.value)
    if is_dataclass(value):
        return _normalise_json(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _normalise_json(val) for key, val in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_normalise_json(item) for item in value]
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return str(value)


type JSONMutableMapping = dict[str, JsonValueType]


def ensure_json_mapping(data: Mapping[str, Any] | None) -> JSONMutableMapping:
    """Convert ``data`` into a JSON-serialisable mutable mapping."""
    if not data:
        return {}
    normalised = _normalise_json(data)
    if isinstance(normalised, dict):
        return normalised
    return {}
