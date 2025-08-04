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

    tasks = [
        _svc(
            INPUT_DATETIME_DOMAIN,
            "set_datetime",
            {
                "entity_id": f"input_datetime.last_walk_{dog_id}",
                "timestamp": now().timestamp(),
            },
        ),
        _svc(
            INPUT_BOOLEAN_DOMAIN,
            "turn_off",
            {"entity_id": f"input_boolean.visitor_mode_{dog_id}"},
        ),
        _svc(
            "input_text",
            "set_value",
            {
                "entity_id": f"input_text.last_activity_{dog_id}",
                "value": "No activity yet",
            },
        ),
    ]

    for counter in ["feeding", "walk", "potty"]:
        tasks.append(
            _svc(
                COUNTER_DOMAIN,
                "configure",
                {
                    "entity_id": f"counter.{counter}_{dog_id}",
                    "initial": 0,
                    "minimum": 0,
                    "maximum": 20,
                    "step": 1,
                    "restore": True,
                },
            )
        )

    await asyncio.gather(*tasks)
