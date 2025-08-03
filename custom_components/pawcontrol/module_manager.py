"""Helper functions to manage optional Paw Control modules.

This module centralizes logic for setting up, unloading and ensuring
helper entities for the optional modules defined in ``module_registry``.
"""
from __future__ import annotations

from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .module_registry import MODULES


async def async_setup_modules(
    hass: HomeAssistant, entry: ConfigEntry, opts: Dict[str, Any]
) -> None:
    """Set up all enabled modules based on provided options."""
    for key, module in MODULES.items():
        if opts.get(key, module.default):
            await module.setup(hass, entry)
        elif module.teardown:
            await module.teardown(hass, entry)


async def async_unload_modules(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Unload all modules that define a teardown handler."""
    for module in MODULES.values():
        if module.teardown:
            await module.teardown(hass, entry)


async def async_ensure_helpers(hass: HomeAssistant, opts: Dict[str, Any]) -> None:
    """Ensure helper entities for all enabled modules."""
    for key, module in MODULES.items():
        if opts.get(key, module.default) and module.ensure_helpers:
            await module.ensure_helpers(hass, opts)

