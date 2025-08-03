"""Utilities for building configuration and option schemas."""
from __future__ import annotations

from typing import Any, Dict

import voluptuous as vol

from .const import CONF_CREATE_DASHBOARD
from .module_registry import MODULES


def build_module_schema(data: Dict[str, Any] | None = None) -> Dict[Any, Any]:
    """Create schema entries for module toggles.

    Parameters
    ----------
    data: Existing configuration or options. If provided, values from this dict
        are used as defaults. Otherwise module defaults are used.
    """
    schema: Dict[Any, Any] = {}
    for key, module in MODULES.items():
        default_value = module.default if data is None else data.get(key, module.default)
        schema[vol.Optional(key, default=default_value)] = bool
    dashboard_default = False if data is None else data.get(CONF_CREATE_DASHBOARD, False)
    schema[vol.Optional(CONF_CREATE_DASHBOARD, default=dashboard_default)] = bool
    return schema

