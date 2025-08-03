"""Registry for optional Paw Control modules."""
from __future__ import annotations

from typing import Awaitable, Callable, Dict, Optional

from .const import (
    CONF_GPS_ENABLE,
    CONF_NOTIFICATIONS_ENABLED,
    CONF_HEALTH_MODULE,
    CONF_WALK_MODULE,
)

from . import gps, push, health, walk

ModuleFunc = Callable[..., Awaitable[None]]


class Module:
    """Container for module handlers."""

    def __init__(
        self,
        setup: ModuleFunc,
        teardown: Optional[ModuleFunc] = None,
        ensure_helpers: Optional[ModuleFunc] = None,
        default: bool = True,
    ) -> None:
        self.setup = setup
        self.teardown = teardown
        self.ensure_helpers = ensure_helpers
        self.default = default


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
