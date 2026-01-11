"""JSON helper types and normalization for Paw Control."""

from __future__ import annotations

import base64
import logging
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any

from homeassistant.util.json import JsonValueType

_LOGGER = logging.getLogger(__name__)


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
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            encoded = base64.b64encode(value).decode("ascii")
            _LOGGER.debug(
                "Encoding non-UTF8 bytes as base64 for JSON normalization."
            )
            return f"base64:{encoded}"
    _LOGGER.debug(
        "Converting unexpected type %s to string: %r", type(value).__name__, value
    )
    return str(value)


type JSONMutableMapping = dict[str, JsonValueType]


def ensure_json_mapping(data: Mapping[str, Any] | None) -> JSONMutableMapping:
    """Convert ``data`` into a JSON-serialisable mutable mapping."""
    if not data:
        return {}
    normalised = _normalise_json(data)
    if not isinstance(normalised, dict):
        msg = (
            "Data must normalize to a dict, got "
            f"{type(normalised).__name__}: {normalised!r}"
        )
        raise TypeError(msg)
    return normalised
