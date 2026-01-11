"""Modular setup and teardown manager for Paw Control."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

from . import dashboard
from .const import CONF_CREATE_DASHBOARD, CONF_DOG_NAME
from .module_registry import (
    async_ensure_helpers,
    async_setup_modules,
    async_unload_modules,
)
from .setup_helpers import async_remove_helpers_for_dog
from .utils import merge_entry_options

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .types import PawControlConfigData, PawControlOptions

_LOGGER = logging.getLogger(__name__)


class InstallationManager:
    """Handle integration installation and configuration."""

    async def setup_entry(self, hass: HomeAssistant, entry: ConfigEntry) -> bool:
        """Set up the integration and selected modules."""
        opts = merge_entry_options(entry)
        module_opts = cast("PawControlOptions", opts)

        dog_present = CONF_DOG_NAME in opts
        dog_name = opts.setdefault(CONF_DOG_NAME, entry.title)

        try:
            await async_ensure_helpers(hass, module_opts)
            await async_setup_modules(hass, entry, module_opts)
        except Exception:  # pragma: no cover - defensive programming
            _LOGGER.exception("Error setting up modules for entry %s", entry.entry_id)
            return False

        await self._maybe_create_dashboard(hass, dog_name, dog_present, opts)

        return True

    async def unload_entry(self, hass: HomeAssistant, entry: ConfigEntry) -> bool:
        """Unload the integration and clean up modules."""
        try:
            await async_unload_modules(hass, entry)
            dog_id = entry.data.get(CONF_DOG_NAME, entry.title)
            await async_remove_helpers_for_dog(hass, dog_id)
        except Exception:  # pragma: no cover - defensive programming
            _LOGGER.exception("Error unloading modules for entry %s", entry.entry_id)
            return False
        return True

    async def _maybe_create_dashboard(
        self,
        hass: HomeAssistant,
        dog_name: str,
        dog_present: bool,
        opts: PawControlConfigData,
    ) -> None:
        """Create dashboard if requested via options."""
        if not opts.get(CONF_CREATE_DASHBOARD, False):
            return
        if dog_present and dog_name:
            try:
                await dashboard.create_dashboard(hass, dog_name)
            except Exception:  # pragma: no cover - defensive programming
                _LOGGER.exception("Error creating dashboard for %s", dog_name)
        else:
            _LOGGER.warning("Dashboard creation requested but no dog name provided")


__all__ = ["InstallationManager"]
