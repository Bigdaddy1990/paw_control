import voluptuous as vol
from homeassistant import config_entries
from .const import *

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for Paw Control."""

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Hier können Validierungen ergänzt werden!
            return self.async_create_entry(title=user_input[CONF_DOG_NAME], data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_DOG_NAME): str,
                vol.Optional(CONF_DOG_BREED, default=""): str,
                vol.Optional(CONF_DOG_AGE, default=0): int,
                vol.Optional(CONF_DOG_WEIGHT, default=0.0): float,
                vol.Optional(CONF_FEEDING_TIMES, default=DEFAULT_FEEDING_TIMES): list,
                vol.Optional(CONF_WALK_DURATION, default=DEFAULT_WALK_DURATION): int,
                vol.Optional(CONF_VET_CONTACT, default=""): str,
                # Modul-Toggles
                vol.Optional(CONF_GPS_ENABLE, default=True): bool,
                vol.Optional(CONF_NOTIFICATIONS_ENABLED, default=True): bool,
                vol.Optional(CONF_HEALTH_MODULE, default=True): bool,
                vol.Optional(CONF_WALK_MODULE, default=True): bool,
                vol.Optional(CONF_CREATE_DASHBOARD, default=False): bool,
            }),
            errors=errors
        )

    async def async_step_options(self, user_input=None):
        entry = self.hass.config_entries.async_entries(DOMAIN)[0]
        data = entry.data
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="options",
            data_schema=vol.Schema({
                vol.Optional(CONF_GPS_ENABLE, default=data.get(CONF_GPS_ENABLE, True)): bool,
                vol.Optional(CONF_NOTIFICATIONS_ENABLED, default=data.get(CONF_NOTIFICATIONS_ENABLED, True)): bool,
                vol.Optional(CONF_HEALTH_MODULE, default=data.get(CONF_HEALTH_MODULE, True)): bool,
                vol.Optional(CONF_WALK_MODULE, default=data.get(CONF_WALK_MODULE, True)): bool,
                vol.Optional(CONF_CREATE_DASHBOARD, default=data.get(CONF_CREATE_DASHBOARD, False)): bool,
            }),
        )
