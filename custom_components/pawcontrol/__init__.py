"""Paw Control integration setup and teardown."""

from __future__ import annotations

from typing import Any, Dict, Optional

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .actionable_push import setup_actionable_notifications
from .const import DOMAIN
from .installation_manager import InstallationManager

DOMAIN = "pawcontrol"

_LOGGER = logging.getLogger(__name__)


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
    """Set up the Paw Control integration (YAML configuration not supported)."""
    _get_domain_data(hass)

    if DOMAIN in config:
        _LOGGER.warning("Configuration via YAML is not supported")

    setup_actionable_notifications(hass)

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


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle reload of a config entry."""
    await async_unload_entry(hass, entry)
    return await async_setup_entry(hass, entry)


__all__ = [
    "DOMAIN",
    "async_setup",
    "async_setup_entry",
    "async_unload_entry",
    "async_reload_entry",
    "get_domain_data",
    "get_manager",
]


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle reloading a config entry by unloading and setting it up again."""
    if not await async_unload_entry(hass, entry):
        return False
    return await async_setup_entry(hass, entry)

