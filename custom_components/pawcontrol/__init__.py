"""Initialisierung von PawControl."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

from . import dashboard
from .const import CONF_DOG_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)

# Map configuration options to their corresponding implementation modules.
# The modules follow the '<feature>_system' naming convention.
AVAILABLE_MODULES = {
    "gps": "gps_system",
    "health": "health_system",
    "walk": "walk_system",
    "push": "push",
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PawControl from a config entry."""
    _LOGGER.debug("Setting up PawControl Integration.")
    user_options = entry.options or {}
    enabled_modules = user_options.get("modules", ["gps"])
    for module_key in enabled_modules:
        module_name = AVAILABLE_MODULES.get(module_key)
        if module_name:
            module = __import__(
                f".{module_name}", globals(), locals(), ["async_setup_entry"], 1
            )
            setup_func = getattr(module, "async_setup_entry", None)
            if setup_func is None:
                setup_func = getattr(module, f"setup_{module_key}", None)
            if setup_func:
                await setup_func(hass, entry)
            else:
                _LOGGER.warning("Module %s has no setup function", module_name)

    async def handle_create_dashboard(_call: ServiceCall) -> None:
        create_fn = getattr(dashboard, "create_dashboard", None)
        if not create_fn:
            _LOGGER.error("Dashboard module missing create_dashboard function")
            return

        dog_name = entry.data.get(CONF_DOG_NAME)
        await create_fn(hass, dog_name)

    hass.services.async_register(DOMAIN, "create_dashboard", handle_create_dashboard)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload PawControl config entry."""
    user_options = entry.options or {}
    enabled_modules = user_options.get("modules", ["gps"])
    for module_key in enabled_modules:
        module_name = AVAILABLE_MODULES.get(module_key)
        if module_name:
            module = __import__(
                f".{module_name}", globals(), locals(), ["async_unload_entry"], 1
            )
            unload_func = getattr(module, "async_unload_entry", None)
            if unload_func is None:
                unload_func = getattr(module, f"teardown_{module_key}", None)
            if unload_func:
                await unload_func(hass, entry)
            else:
                _LOGGER.warning("Module %s has no unload function", module_name)
    return True
