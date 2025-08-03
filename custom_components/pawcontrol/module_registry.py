"""Registry and helpers for optional Paw Control modules."""
from __future__ import annotations

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


async def ensure_helpers(hass: HomeAssistant, opts: Dict[str, bool]) -> None:
  
    """Ensure helpers for all enabled modules."""
    for key, module in MODULES.items():
        if opts.get(key, module.default) and module.ensure_helpers:
            await module.ensure_helpers(hass, opts)


async def setup_modules(
    hass: HomeAssistant, entry: ConfigEntry, opts: Dict[str, bool]
) -> None:
    """Set up or tear down modules based on options."""

    for key, module in MODULES.items():
        if opts.get(key, module.default):
            await module.setup(hass, entry)
        elif module.teardown:
            await module.teardown(hass, entry)


async def unload_modules(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Unload all modules that define a teardown handler."""

    for module in MODULES.values():
        if module.teardown:
            await module.teardown(hass, entry)
