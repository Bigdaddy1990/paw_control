"""Registry and helpers for optional Paw Control modules.

This module coordinates setup, teardown, and helper creation for each optional
module. Errors raised during these steps by individual modules are logged and
do not prevent subsequent modules from running, keeping setup and teardown
resilient.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Awaitable, Callable, Dict, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_GPS_ENABLE,
    CONF_NOTIFICATIONS_ENABLED,
    CONF_HEALTH_MODULE,
    CONF_WALK_MODULE,
)

from . import gps, push, health, walk

ModuleFunc = Callable[..., Awaitable[None]]


@dataclass
class Module:
    """Container for module handlers."""

    setup: ModuleFunc
    teardown: Optional[ModuleFunc] = None
    ensure_helpers: Optional[ModuleFunc] = None
    default: bool = True


MODULES: Dict[str, Module] = {
    CONF_GPS_ENABLE: Module(
        setup=gps.setup_gps,
        teardown=gps.teardown_gps,
        ensure_helpers=gps.ensure_helpers,
        default=True,
    ),
    CONF_NOTIFICATIONS_ENABLED: Module(
        setup=push.setup_push,
        teardown=push.teardown_push,
        default=True,
    ),
    CONF_HEALTH_MODULE: Module(
        setup=health.setup_health,
        teardown=health.teardown_health,
        ensure_helpers=health.ensure_helpers,
        default=True,
    ),
    CONF_WALK_MODULE: Module(
        setup=walk.setup_walk,
        teardown=walk.teardown_walk,
        ensure_helpers=walk.ensure_helpers,
        default=True,
    ),
}


_LOGGER = logging.getLogger(__name__)


async def ensure_helpers(hass: HomeAssistant, opts: Dict[str, bool]) -> None:
    """Ensure helpers for all enabled modules.

    Errors from individual modules are logged but do not halt processing.
    """
    for key, module in MODULES.items():
        if opts.get(key, module.default) and module.ensure_helpers:
            try:
                await module.ensure_helpers(hass, opts)
            except Exception as err:  # pragma: no cover - defensive programming
                _LOGGER.error("Error ensuring helpers for module %s: %s", key, err)


async def setup_modules(
    hass: HomeAssistant, entry: ConfigEntry, opts: Dict[str, bool]
) -> None:
    """Set up or tear down modules based on options.

    Setup errors for individual modules are logged and other modules continue.
    """

    for key, module in MODULES.items():
        try:
            if opts.get(key, module.default):
                await module.setup(hass, entry)
            elif module.teardown:
                await module.teardown(hass, entry)
        except Exception as err:  # pragma: no cover - defensive programming
            action = "setting up" if opts.get(key, module.default) else "tearing down"
            _LOGGER.error("Error %s module %s: %s", action, key, err)


async def unload_modules(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Unload all modules that define a teardown handler.

    Errors during teardown are logged to avoid interrupting unloading.
    """

    for key, module in MODULES.items():
        if module.teardown:
            try:
                await module.teardown(hass, entry)
            except Exception as err:  # pragma: no cover - defensive programming
                _LOGGER.error("Error tearing down module %s: %s", key, err)


# Backwards compatible aliases used by the tests and legacy code
async_ensure_helpers = ensure_helpers
async_setup_modules = setup_modules
async_unload_modules = unload_modules

__all__ = [
    "Module",
    "MODULES",
    "async_ensure_helpers",
    "async_setup_modules",
    "async_unload_modules",
]
