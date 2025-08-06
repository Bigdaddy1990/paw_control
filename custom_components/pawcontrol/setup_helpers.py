"""Helper creation utilities for Paw Control."""

from __future__ import annotations

import asyncio

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


async def async_create_helpers_for_dog(hass: HomeAssistant, dog_id: str) -> None:
    """Create helper entities required for core features."""

    async def _svc(domain: str, service: str, data: dict) -> None:
        await safe_service_call(hass, domain, service, data)

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
    for counter in ["feeding", "walk", "potty"]:
        helper_calls.append(
            (
                COUNTER_DOMAIN,
                "configure",
                {"entity_id": f"counter.{counter}_{dog_id}", **counter_cfg},
            )
        )

    await asyncio.gather(
        *(_svc(domain, service, data) for domain, service, data in helper_calls)
    )
