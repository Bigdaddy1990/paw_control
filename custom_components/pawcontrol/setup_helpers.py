"""Helper creation utilities for Paw Control."""

from __future__ import annotations

import asyncio
import logging

from dataclasses import dataclass
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.components.input_datetime import DOMAIN as INPUT_DATETIME_DOMAIN
from homeassistant.components.input_boolean import DOMAIN as INPUT_BOOLEAN_DOMAIN
from homeassistant.components.counter import DOMAIN as COUNTER_DOMAIN
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


@dataclass(frozen=True)
class HelperCall:
    """Container describing a helper service call."""

    domain: str
    service: str
    data: dict[str, Any]


COUNTER_HELPERS = ("feeding", "walk", "potty")
COUNTER_CFG: dict[str, Any] = {
    "initial": 0,
    "minimum": 0,
    "maximum": 20,
    "step": 1,
    "restore": True,
}


async def async_create_helpers_for_dog(hass: HomeAssistant, dog_id: str) -> None:
    """Create helper entities required for core features."""

    async def _svc(call: HelperCall) -> None:
        try:
            await safe_service_call(hass, call.domain, call.service, call.data)
        except Exception:  # pragma: no cover - defensive programming
            _LOGGER.exception(
                "Error creating helper %s for dog %s",
                call.data.get("entity_id", "?"),
                dog_id,
            )

    helper_calls: list[HelperCall] = [
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
        helper_calls.append(
            HelperCall(
                COUNTER_DOMAIN,
                "configure",
                {"entity_id": f"counter.{counter}_{dog_id}", **COUNTER_CFG},
            )
        )

    await asyncio.gather(*(_svc(call) for call in helper_calls))


async def async_remove_helpers_for_dog(hass: HomeAssistant, dog_id: str) -> None:
    """Remove helper entities created for core features."""

    async def _svc(domain: str, service: str, data: dict) -> None:
        try:
            await safe_service_call(hass, domain, service, data)
        except Exception:  # pragma: no cover - defensive programming
            _LOGGER.exception(
                "Error removing helper %s for dog %s", data.get("entity_id", "?"), dog_id
            )

    helper_calls: list[tuple[str, str, dict]] = [
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

    for counter in ["feeding", "walk", "potty"]:
        helper_calls.append(
            (
                COUNTER_DOMAIN,
                "remove",
                {"entity_id": f"counter.{counter}_{dog_id}"},
            )
        )

    await asyncio.gather(
        *(
            _call_service(hass, dog_id, domain, service, data)
            for domain, service, data in helper_calls
        )
    )


__all__ = ["async_create_helpers_for_dog", "async_remove_helpers_for_dog"]
