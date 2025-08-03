"""Modular setup and teardown manager for Paw Control."""
from __future__ import annotations

from typing import Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import dashboard
from .const import CONF_CREATE_DASHBOARD, CONF_DOG_NAME
from .module_registry import MODULES


class InstallationManager:
    """Handle integration installation and configuration."""

    async def setup_entry(self, hass: HomeAssistant, entry: ConfigEntry) -> bool:
        """Set up the integration and selected modules."""
        opts = entry.options if entry.options else entry.data

        # Ensure helper entities for all enabled modules
        await self.ensure_helpers(hass, opts)

        # Run setup or teardown for each module based on options
        for key, module in MODULES.items():
            if opts.get(key, module.default):
                await module.setup(hass, entry)
            elif module.teardown:
                await module.teardown(hass, entry)

        # Create dashboard if requested
        if opts.get(CONF_CREATE_DASHBOARD, False):
            await dashboard.create_dashboard(hass, opts[CONF_DOG_NAME])

        return True

    async def unload_entry(self, hass: HomeAssistant, entry: ConfigEntry) -> bool:
        """Unload the integration and clean up modules."""
        for module in MODULES.values():
            if module.teardown:
                await module.teardown(hass, entry)
        return True

    async def ensure_helpers(self, hass: HomeAssistant, opts: Dict) -> None:
        """Create helper entities for all enabled modules."""
        for key, module in MODULES.items():
            if opts.get(key, module.default) and module.ensure_helpers:
                await module.ensure_helpers(hass, opts)
