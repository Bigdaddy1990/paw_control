"""Paw Control integration setup and teardown."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .installation_manager import InstallationManager

# Integration domain
DOMAIN = "pawcontrol"

# Single instance of the manager used by Home Assistant during setup
manager = InstallationManager()


def _get_domain_data(hass: HomeAssistant) -> dict:
    """Return the storage dictionary for this domain on the hass object."""
    if not hasattr(hass, "data"):
        hass.data = {}
    return hass.data.setdefault(DOMAIN, {})


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Paw Control integration (YAML not supported)."""
    _get_domain_data(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Paw Control from a config entry."""
    _get_domain_data(hass)[entry.entry_id] = manager
    return await manager.setup_entry(hass, entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Paw Control config entry."""
    unload_ok = await manager.unload_entry(hass, entry)
    if unload_ok:
        _get_domain_data(hass).pop(entry.entry_id, None)
    return unload_ok

