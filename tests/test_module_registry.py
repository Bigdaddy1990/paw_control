import os
import sys

import pytest
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace

# Ensure the custom component package is importable
sys.path.insert(0, os.path.abspath("."))

from custom_components.pawcontrol import config_flow
import custom_components.pawcontrol as integration
from custom_components.pawcontrol.const import DOMAIN, CONF_DOG_NAME
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
        flow2 = config_flow.ConfigFlow()
        flow2.hass = hass
        with patch.object(config_flow.ConfigFlow, 'async_create_entry', return_value={'data': options_input}):
            result2 = await flow2.async_step_options(options_input)

        entry.options = result2['data']

        await integration.async_setup_entry(hass, entry)

        setup_mock.assert_not_called()
        helper_mock.assert_not_called()
        teardown_mock.assert_called_once_with(hass, entry)

    import asyncio
    asyncio.run(run_test())
