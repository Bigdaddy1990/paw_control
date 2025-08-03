"""Config flow for Paw Control with dynamic module options."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import *
from .module_registry import MODULES

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle initial configuration for Paw Control."""

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Hier können Validierungen ergänzt werden!
            return self.async_create_entry(title=user_input[CONF_DOG_NAME], data=user_input)

        schema = {
            vol.Required(CONF_DOG_NAME): str,
            vol.Optional(CONF_DOG_BREED, default=""): str,
            vol.Optional(CONF_DOG_AGE, default=0): int,
            vol.Optional(CONF_DOG_WEIGHT, default=0.0): float,
            vol.Optional(CONF_FEEDING_TIMES, default=DEFAULT_FEEDING_TIMES): list,
            vol.Optional(CONF_WALK_DURATION, default=DEFAULT_WALK_DURATION): int,
            vol.Optional(CONF_VET_CONTACT, default=""): str,
        }
        for key, module in MODULES.items():
            schema[vol.Optional(key, default=module.default)] = bool
        schema[vol.Optional(CONF_CREATE_DASHBOARD, default=False)] = bool

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(schema),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle option flow for Paw Control to enable/disable modules."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):  # pragma: no cover - HA handles step name
        data = self.config_entry.options or self.config_entry.data

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = {}
        for key, module in MODULES.items():
            schema[vol.Optional(key, default=data.get(key, module.default))] = bool
        schema[vol.Optional(CONF_CREATE_DASHBOARD, default=data.get(CONF_CREATE_DASHBOARD, False))] = bool

        return self.async_show_form(step_id="init", data_schema=vol.Schema(schema))
