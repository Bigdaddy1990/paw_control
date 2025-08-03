"""Modular setup and teardown manager for Paw Control."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import dashboard
from .const import CONF_CREATE_DASHBOARD, CONF_DOG_NAME
from .module_manager import (
    async_ensure_helpers,
    async_setup_modules,
    async_unload_modules,
)


class InstallationManager:
    """Handle integration installation and configuration."""

    async def setup_entry(self, hass: HomeAssistant, entry: ConfigEntry) -> bool:
        """Set up the integration and selected modules."""
        # Merge config entry data and options, with options taking precedence
        opts = {**entry.data, **entry.options}

        # Ensure helper entities for enabled modules then set them up
        await async_ensure_helpers(hass, opts)
        await async_setup_modules(hass, entry, opts)

        # Create dashboard if requested
        if opts.get(CONF_CREATE_DASHBOARD, False):
            await dashboard.create_dashboard(hass, opts[CONF_DOG_NAME])

        return True

    async def unload_entry(self, hass: HomeAssistant, entry: ConfigEntry) -> bool:
        """Unload the integration and clean up modules."""
        await async_unload_modules(hass, entry)
        return True
