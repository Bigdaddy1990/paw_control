"""Helper creation utilities for Paw Control.

This module creates and removes the helper entities used by the integration.
The helpers are created via service calls which are wrapped in
``safe_service_call`` to ensure failures are logged but do not raise.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.counter import DOMAIN as COUNTER_DOMAIN
from homeassistant.components.input_boolean import DOMAIN as INPUT_BOOLEAN_DOMAIN
from homeassistant.components.input_datetime import DOMAIN as INPUT_DATETIME_DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.util.dt import now

from .utils import safe_service_call

_LOGGER = logging.getLogger(__name__)

# Counters used by the integration
COUNTER_HELPERS = ("feeding", "walk", "potty")

# Default configuration for newly created counters
COUNTER_CONFIG: dict[str, Any] = {
    "initial": 0,
    "minimum": 0,
    "maximum": 20,
    "step": 1,
    "restore": True,
}


async def _call_service(
    hass: HomeAssistant, dog_id: str, domain: str, service: str, data: dict
) -> None:
    """Call a Home Assistant service and log any failure."""
    try:
        await safe_service_call(hass, domain, service, data)
    except Exception:  # pragma: no cover - defensive programming
        _LOGGER.exception(
            "Error executing %s.%s for dog %s", domain, service, dog_id
        )


@dataclass(frozen=True)
class HelperCall:
    """Description of a helper service call."""

    domain: str
    service: str
    data: dict[str, Any]


async def async_create_helpers_for_dog(hass: HomeAssistant, dog_id: str) -> None:
    """Create helper entities required for core features."""

    calls: list[HelperCall] = [
        HelperCall(
            INPUT_DATETIME_DOMAIN,
            "set_datetime",
            {
                "entity_id": f"input_datetime.last_walk_{dog_id}",
                "timestamp": now().timestamp(),
            },
        ),
        HelperCall(
            INPUT_BOOLEAN_DOMAIN,
            "turn_off",
            {"entity_id": f"input_boolean.visitor_mode_{dog_id}"},
        ),
        HelperCall(
            "input_text",
            "set_value",
            {
                "entity_id": f"input_text.last_activity_{dog_id}",
                "value": "No activity yet",
            },
        ),
    ]

    for counter in COUNTER_HELPERS:
        calls.append(
            HelperCall(
                COUNTER_DOMAIN,
                "configure",
                {"entity_id": f"counter.{counter}_{dog_id}", **COUNTER_CONFIG},
            )
        )

    await asyncio.gather(
        *(_call_service(hass, dog_id, c.domain, c.service, c.data) for c in calls)
    )


async def async_remove_helpers_for_dog(hass: HomeAssistant, dog_id: str) -> None:
    """Remove helper entities created for core features."""

    calls: list[tuple[str, str, dict[str, Any]]] = [
        (
            INPUT_DATETIME_DOMAIN,
            "remove",
            {"entity_id": f"input_datetime.last_walk_{dog_id}"},
        ),
        (
            INPUT_BOOLEAN_DOMAIN,
            "remove",
            {"entity_id": f"input_boolean.visitor_mode_{dog_id}"},
        ),
        (
            "input_text",
            "remove",
            {"entity_id": f"input_text.last_activity_{dog_id}"},
        ),
    ]

    for counter in COUNTER_HELPERS:
        calls.append(
            (
                COUNTER_DOMAIN,
                "remove",
                {"entity_id": f"counter.{counter}_{dog_id}"},
            )
        )

    await asyncio.gather(
        *(
            _call_service(hass, dog_id, domain, service, data)
            for domain, service, data in calls
        )
    )


__all__ = ["async_create_helpers_for_dog", "async_remove_helpers_for_dog"]

