import os
import sys

import pytest
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace

# Ensure the custom component package is importable
sys.path.insert(0, os.path.abspath("."))

from custom_components.pawcontrol import config_flow
import custom_components.pawcontrol as integration
from custom_components.pawcontrol.const import DOMAIN, CONF_DOG_NAME, CONF_CREATE_DASHBOARD
from custom_components.pawcontrol import module_registry
from homeassistant import config_entries


@pytest.mark.parametrize('module_key', list(module_registry.MODULES.keys()))
def test_module_enable_disable(monkeypatch, module_key):
    async def run_test():
        patched = {}
        for key, mod in module_registry.MODULES.items():
            setup_mock = AsyncMock()
            teardown_mock = AsyncMock()
            helper_mock = AsyncMock()
            monkeypatch.setattr(mod, 'setup', setup_mock)
            monkeypatch.setattr(mod, 'teardown', teardown_mock)
            monkeypatch.setattr(mod, 'ensure_helpers', helper_mock)
            patched[key] = (setup_mock, teardown_mock, helper_mock)

        user_input = {CONF_DOG_NAME: 'Fido'}
        for key in module_registry.MODULES.keys():
            user_input[key] = (key == module_key)

        flow = config_flow.ConfigFlow()
        flow.hass = SimpleNamespace()
        with patch.object(config_flow.ConfigFlow, 'async_create_entry', return_value={'data': user_input}):
            result = await flow.async_step_user(user_input)

        entry = config_entries.ConfigEntry(
            version=1,
            minor_version=1,
            domain=DOMAIN,
            title='Fido',
            data=result['data'],
            source='user',
        )

        hass = SimpleNamespace(config_entries=SimpleNamespace(async_entries=lambda domain: [entry]))

        await integration.async_setup_entry(hass, entry)

        setup_mock, teardown_mock, helper_mock = patched[module_key]
        setup_mock.assert_called_once_with(hass, entry)
        helper_mock.assert_called_once_with(hass, result['data'])
        teardown_mock.assert_not_called()

        setup_mock.reset_mock()
        teardown_mock.reset_mock()
        helper_mock.reset_mock()

        options_input = {key: False for key in module_registry.MODULES.keys()}
        options_flow = config_flow.OptionsFlowHandler(entry)
        options_flow.hass = hass
        with patch.object(config_flow.OptionsFlowHandler, 'async_create_entry', return_value={'data': options_input}):
            result2 = await options_flow.async_step_init(options_input)

        entry.options = result2['data']

        await integration.async_setup_entry(hass, entry)

        setup_mock.assert_not_called()
        helper_mock.assert_not_called()
        teardown_mock.assert_called_once_with(hass, entry)

        # Re-enable the module through options
        setup_mock.reset_mock()
        teardown_mock.reset_mock()
        helper_mock.reset_mock()

        options_input2 = {key: (key == module_key) for key in module_registry.MODULES.keys()}
        options_flow2 = config_flow.OptionsFlowHandler(entry)
        options_flow2.hass = hass
        with patch.object(config_flow.OptionsFlowHandler, 'async_create_entry', return_value={'data': options_input2}):
            await options_flow2.async_step_init(options_input2)

        entry.options = options_input2

        await integration.async_setup_entry(hass, entry)

        setup_mock.assert_called_once_with(hass, entry)
        helper_mock.assert_called_once_with(hass, entry.options)
        teardown_mock.assert_not_called()

    import asyncio
    asyncio.run(run_test())


def test_options_flow_defaults_and_persistence():
    """Ensure options flow shows correct defaults and persists selections."""

    async def run_test():
        data = {CONF_DOG_NAME: "Fido"}
        for key, mod in module_registry.MODULES.items():
            data[key] = mod.default

        entry = config_entries.ConfigEntry(
            version=1,
            minor_version=1,
            domain=DOMAIN,
            title="Fido",
            data=data,
            source="user",
        )

        # options flow defaults come from entry data
        flow_handler = config_flow.ConfigFlow.async_get_options_flow(entry)
        assert isinstance(flow_handler, config_flow.OptionsFlowHandler)
        flow_handler.hass = SimpleNamespace()
        result = await flow_handler.async_step_init()
        assert result["type"] == "form" and result["step_id"] == "init"
        defaults = {
            opt.schema: opt.default() if callable(opt.default) else opt.default
            for opt in result["data_schema"].schema.keys()
        }
        for key, mod in module_registry.MODULES.items():
            assert defaults[key] == mod.default
        assert defaults[CONF_CREATE_DASHBOARD] is False

        # submit new options disabling all modules and enabling dashboard
        options_input = {key: False for key in module_registry.MODULES.keys()}
        options_input[CONF_CREATE_DASHBOARD] = True
        with patch.object(
            config_flow.OptionsFlowHandler,
            "async_create_entry",
            return_value={"data": options_input},
        ) as create_entry:
            result2 = await flow_handler.async_step_init(options_input)
            create_entry.assert_called_once_with(title="", data=options_input)

        entry.options = result2["data"]

        # second run should use options as defaults
        flow_handler2 = config_flow.OptionsFlowHandler(entry)
        flow_handler2.hass = SimpleNamespace()
        result3 = await flow_handler2.async_step_init()
        defaults2 = {
            opt.schema: opt.default() if callable(opt.default) else opt.default
            for opt in result3["data_schema"].schema.keys()
        }
        for key in module_registry.MODULES.keys():
            assert defaults2[key] is False
        assert defaults2[CONF_CREATE_DASHBOARD] is True

    import asyncio
    asyncio.run(run_test())
