"""Paw Control integration setup and teardown."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .installation_manager import InstallationManager

# Integration domain
DOMAIN = "pawcontrol"


def _get_domain_data(hass: HomeAssistant) -> dict[str, Any]:
    """Return the storage dictionary for this domain."""
    data = getattr(hass, "data", None)
    if data is None:
        data = hass.data = {}
    return data.setdefault(DOMAIN, {})


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Paw Control integration (YAML not supported)."""
    _get_domain_data(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Paw Control from a config entry."""
    manager = InstallationManager()
    _get_domain_data(hass)[entry.entry_id] = manager
    return await manager.setup_entry(hass, entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Paw Control config entry."""
    manager: InstallationManager | None = _get_domain_data(hass).pop(
        entry.entry_id, None
    )
    if manager is None:
        return False
    return await manager.unload_entry(hass, entry)

