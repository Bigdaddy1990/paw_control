"""Paw Control integration setup and teardown."""

from __future__ import annotations

from typing import Any, Dict, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .installation_manager import InstallationManager

# Integration domain
DOMAIN = "pawcontrol"


def get_domain_data(hass: HomeAssistant) -> Dict[str, InstallationManager]:
    """Return the storage dictionary for this domain.

    The dictionary is created on demand and stored in ``hass.data``.
    """
    data = getattr(hass, "data", None)
    if data is None:
        data = hass.data = {}
    return data.setdefault(DOMAIN, {})


def get_manager(hass: HomeAssistant, entry_id: str) -> Optional[InstallationManager]:
    """Return the :class:`InstallationManager` for a config entry.

    Returns ``None`` if the entry has not been set up yet.
    """
    return get_domain_data(hass).get(entry_id)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Paw Control integration (YAML not supported)."""
    get_domain_data(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Paw Control from a config entry."""
    manager = InstallationManager()
    get_domain_data(hass)[entry.entry_id] = manager
    return await manager.setup_entry(hass, entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Paw Control config entry."""
    manager = get_manager(hass, entry.entry_id)
    if manager is None:
        return False
    get_domain_data(hass).pop(entry.entry_id, None)
    return await manager.unload_entry(hass, entry)


__all__ = [
    "DOMAIN",
    "async_setup",
    "async_setup_entry",
    "async_unload_entry",
    "get_domain_data",
    "get_manager",
]

