"""Config flow for Paw Control integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_DOG_NAME,
    CONF_DOG_BREED,
    CONF_DOG_AGE,
    CONF_DOG_WEIGHT,
    CONF_FEEDING_TIMES,
    CONF_WALK_DURATION,
    CONF_VET_CONTACT,
    CONF_GPS_ENABLE,
    CONF_UPDATE_INTERVAL,
    CONF_GEOFENCE_RADIUS,
    CONF_NOTIFICATIONS_ENABLED,
    DEFAULT_WALK_DURATION,
    DEFAULT_FEEDING_TIMES,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_GEOFENCE_RADIUS,
)
from .exceptions import InvalidDogName
from .utils import validate_dog_name, validate_weight, validate_age

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input."""
    dog_name = data[CONF_DOG_NAME].strip()
    
    if not validate_dog_name(dog_name):
        raise InvalidDogName("Invalid dog name format")
    
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data.get(CONF_DOG_NAME, "").lower() == dog_name.lower():
            raise InvalidDogName("Dog with this name already exists")
    
    if not validate_weight(data.get(CONF_DOG_WEIGHT, 0)):
        raise InvalidDogName("Invalid dog weight")
    
    if not validate_age(data.get(CONF_DOG_AGE, 0)):
        raise InvalidDogName("Invalid dog age")
    
    return {"title": dog_name}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Paw Control."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except InvalidDogName as exc:
                if "already exists" in str(exc):
                    errors["dog_name"] = "name_exists"
                else:
                    errors["dog_name"] = "invalid_dog_name"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                dog_name = user_input[CONF_DOG_NAME].strip()
                await self.async_set_unique_id(dog_name.lower())
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_DOG_NAME): str,
            vol.Optional(CONF_DOG_BREED, default=""): str,
            vol.Required(CONF_DOG_AGE, default=5): vol.All(vol.Coerce(int), vol.Range(min=0, max=30)),
            vol.Required(CONF_DOG_WEIGHT, default=25.0): vol.All(vol.Coerce(float), vol.Range(min=0.5, max=100.0)),
            vol.Optional(CONF_FEEDING_TIMES, default=DEFAULT_FEEDING_TIMES): str,
            vol.Optional(CONF_WALK_DURATION, default=DEFAULT_WALK_DURATION): vol.All(vol.Coerce(int), vol.Range(min=5, max=180)),
            vol.Optional(CONF_VET_CONTACT, default=""): str,
            vol.Optional(CONF_GPS_ENABLE, default=True): bool,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Paw Control."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        dog_name = self.config_entry.data.get(CONF_DOG_NAME, "Unknown")
        
        data_schema = vol.Schema({
            vol.Optional(
                CONF_FEEDING_TIMES,
                default=self.config_entry.options.get(CONF_FEEDING_TIMES, DEFAULT_FEEDING_TIMES)
            ): str,
            vol.Optional(
                CONF_WALK_DURATION,
                default=self.config_entry.options.get(CONF_WALK_DURATION, DEFAULT_WALK_DURATION)
            ): vol.All(vol.Coerce(int), vol.Range(min=5, max=180)),
            vol.Optional(
                CONF_UPDATE_INTERVAL,
                default=self.config_entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
            ): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
            vol.Optional(
                CONF_GEOFENCE_RADIUS,
                default=self.config_entry.options.get(CONF_GEOFENCE_RADIUS, DEFAULT_GEOFENCE_RADIUS)
            ): vol.All(vol.Coerce(int), vol.Range(min=10, max=1000)),
            vol.Optional(
                CONF_NOTIFICATIONS_ENABLED,
                default=self.config_entry.options.get(CONF_NOTIFICATIONS_ENABLED, True)
            ): bool,
            vol.Optional(
                CONF_VET_CONTACT,
                default=self.config_entry.options.get(CONF_VET_CONTACT, "")
            ): str,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            description_placeholders={"dog_name": dog_name}
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
