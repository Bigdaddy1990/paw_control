"""Paw Control integration setup and teardown."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .installation_manager import InstallationManager


# Single instance of the manager used by Home Assistant during setup
manager = InstallationManager()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Paw Control from a config entry."""
    return await manager.setup_entry(hass, entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Paw Control config entry."""
    return await manager.unload_entry(hass, entry)

