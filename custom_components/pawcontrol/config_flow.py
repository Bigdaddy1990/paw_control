"""Config flow for Paw Control integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_DOG_NAME, CONF_DOG_BREED, CONF_DOG_AGE, CONF_DOG_WEIGHT

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input."""
    # Basic validation
    if not data.get(CONF_DOG_NAME):
        raise ValueError("Dog name is required")
    
    # Check if already configured
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data.get(CONF_DOG_NAME, "").lower() == data[CONF_DOG_NAME].lower():
            raise ValueError("Dog already configured")
    
    return {"title": data[CONF_DOG_NAME]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Paw Control."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except ValueError as err:
                if "already configured" in str(err):
                    errors["base"] = "already_configured"
                else:
                    errors["base"] = "invalid_input"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_DOG_NAME].lower())
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_DOG_NAME): str,
            vol.Optional(CONF_DOG_BREED, default=""): str,
            vol.Optional(CONF_DOG_AGE, default=3): int,
            vol.Optional(CONF_DOG_WEIGHT, default=15.0): vol.Coerce(float),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )