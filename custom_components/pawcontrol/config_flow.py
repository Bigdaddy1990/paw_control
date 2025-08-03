"""Config flow for Paw Control with dynamic module options."""

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from .const import (
    CONF_CREATE_DASHBOARD,
    CONF_DOG_AGE,
    CONF_DOG_BREED,
    CONF_DOG_NAME,
    CONF_DOG_WEIGHT,
    CONF_FEEDING_TIMES,
    CONF_VET_CONTACT,
    CONF_WALK_DURATION,
    DEFAULT_FEEDING_TIMES,
    DEFAULT_WALK_DURATION,
    DOMAIN,
)

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_CREATE_DASHBOARD,
    CONF_DOG_AGE,
    CONF_DOG_BREED,
    CONF_DOG_NAME,
    CONF_DOG_WEIGHT,
    CONF_FEEDING_TIMES,
    CONF_VET_CONTACT,
    CONF_WALK_DURATION,
    DEFAULT_FEEDING_TIMES,
    DEFAULT_WALK_DURATION,
    DOMAIN,
)

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import *

from .module_registry import MODULES

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle initial configuration for Paw Control."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step of the config flow.

        The form allows users to enter basic dog information and enables a
        checkbox for every registered module.  Submitted values are stored in the
        config entry's data so the integration starts with the selected modules
        activated.

        Args:
            user_input: Values provided by the user when the form is submitted,
                or ``None`` to show the form for the first time.

        Returns:
            A ``FlowResult`` describing the next step in the flow. This is either
            a form to be displayed again or an entry creation result when the user
            has completed the setup.
        """

        errors: dict[str, str] = {}
        if user_input is not None:
            # Hier können Validierungen ergänzt werden!
            return self.async_create_entry(
                title=user_input[CONF_DOG_NAME], data=user_input
            )



    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step of the config flow.

        The form allows users to enter basic dog information and enables a
        checkbox for every registered module.  Submitted values are stored in the
        config entry's data so the integration starts with the selected modules
        activated.

        Args:
            user_input: Values provided by the user when the form is submitted,
                or ``None`` to show the form for the first time.

        Returns:
            A ``FlowResult`` describing the next step in the flow. This is either
            a form to be displayed again or an entry creation result when the user
            has completed the setup.
        """

        errors: dict[str, str] = {}
        if user_input is not None:
            # Hier können Validierungen ergänzt werden!

            return self.async_create_entry(
                title=user_input[CONF_DOG_NAME], data=user_input
            )
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
        """Create an options flow handler for an existing config entry.

        Args:
            config_entry: The configuration entry for which the options flow
                should be opened.

        Args:
            config_entry: The configuration entry for which the options flow
                should be opened.
        Returns:
            An ``OptionsFlowHandler`` instance that manages the options flow.
        """


        """Return the options flow handler."""


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle option flow for Paw Control to enable/disable modules."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:

        """Store the config entry so existing options can be loaded.



        """Store the config entry so existing options can be loaded.
        Args:
            config_entry: Entry whose options will be edited. Existing options
                are used as defaults when presenting the form.
        """

        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:  # pragma: no cover - HA handles step name
        """Show and persist module options during configuration.

        When presented without ``user_input`` the method displays a form with a
        toggle for every known module. Each toggle defaults to the value stored in
        the existing options or, if never set, the module's predefined default.
        When ``user_input`` is provided, the chosen values are saved to the config
        entry so that selections persist across reloads and Home Assistant
        restarts.

        Args:
            user_input: Optional mapping of module keys to boolean values when
                the user submits the form.

        Returns:
            A ``FlowResult`` that either shows the form again or writes the
            provided options to the configuration entry.
        """

        # Use existing options if present so changes persist across restarts

        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):  # pragma: no cover - HA handles step name

        data = self.config_entry.options or self.config_entry.data

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = {}
        for key, module in MODULES.items():
            schema[vol.Optional(key, default=data.get(key, module.default))] = bool
        schema[vol.Optional(
            CONF_CREATE_DASHBOARD, default=data.get(CONF_CREATE_DASHBOARD, False)
        )] = bool

        return self.async_show_form(step_id="init", data_schema=vol.Schema(schema))
