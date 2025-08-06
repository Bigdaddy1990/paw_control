"""Helper creation utilities for Paw Control."""

from __future__ import annotations

import asyncio
import logging

from homeassistant.core import HomeAssistant
from homeassistant.components.input_datetime import (
    DOMAIN as INPUT_DATETIME_DOMAIN,
)
from homeassistant.components.input_boolean import (
    DOMAIN as INPUT_BOOLEAN_DOMAIN,
)
from homeassistant.components.counter import (
    DOMAIN as COUNTER_DOMAIN,
)
from homeassistant.util.dt import now

from .utils import safe_service_call

_LOGGER = logging.getLogger(__name__)

COUNTERS = ("feeding", "walk", "potty")


async def _call_service(
    hass: HomeAssistant, dog_id: str, domain: str, service: str, data: dict
) -> None:
    """Execute a helper service call and log errors."""
    try:
        await safe_service_call(hass, domain, service, data)
    except Exception:  # pragma: no cover - defensive programming
        _LOGGER.exception(
            "Error creating helper %s for dog %s", data.get("entity_id", "?"), dog_id
        )


async def async_create_helpers_for_dog(hass: HomeAssistant, dog_id: str) -> None:
    """Create helper entities required for core features."""

    helper_calls: list[tuple[str, str, dict]] = [
        (
            INPUT_DATETIME_DOMAIN,
            "set_datetime",
            {
                "entity_id": f"input_datetime.last_walk_{dog_id}",
                "timestamp": now().timestamp(),
            },
        ),
        (
            INPUT_BOOLEAN_DOMAIN,
            "turn_off",
            {"entity_id": f"input_boolean.visitor_mode_{dog_id}"},
        ),
        (
            "input_text",
            "set_value",
            {
                "entity_id": f"input_text.last_activity_{dog_id}",
                "value": "No activity yet",
            },
        ),
    ]

    counter_cfg = {
        "initial": 0,
        "minimum": 0,
        "maximum": 20,
        "step": 1,
        "restore": True,
    }
    for counter in COUNTERS:
        helper_calls.append(
            (
                COUNTER_DOMAIN,
                "configure",
                {"entity_id": f"counter.{counter}_{dog_id}", **counter_cfg},
            )
        )

    await asyncio.gather(
        *(
            _call_service(hass, dog_id, domain, service, data)
            for domain, service, data in helper_calls
        )
    )


__all__ = ["async_create_helpers_for_dog"]
