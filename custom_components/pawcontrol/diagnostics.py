"""Diagnostics support for Paw Control."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util.json import JsonValueType

from .const import DOMAIN
from .helpers.json import _normalise_json


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict[str, JsonValueType]:
    """Return diagnostics for a config entry."""
    domain_data = hass.data.get(DOMAIN, {}).get(config_entry.entry_id, {})
    coordinator = domain_data.get("coordinator")
    gps_handler = domain_data.get("gps_handler")

    return {
        "entry": {
            "entry_id": config_entry.entry_id,
            "title": config_entry.title,
            "data": _normalise_json(dict(config_entry.data)),
            "options": _normalise_json(dict(config_entry.options)),
        },
        "coordinator": {
            "data": _normalise_json(getattr(coordinator, "data", None)),
            "last_update_success": _normalise_json(
                getattr(coordinator, "last_update_success", None)
            ),
        },
        "gps_handler": _normalise_json(getattr(gps_handler, "__dict__", None)),
    }
