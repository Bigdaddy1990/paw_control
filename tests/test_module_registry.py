import os
import sys

import logging

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
        helper_mock.assert_called_once()
        called_hass, called_opts = helper_mock.call_args[0]
        assert called_hass is hass
        assert called_opts[module_key] is True
        assert called_opts[CONF_DOG_NAME] == 'Fido'
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
        helper_mock.assert_called_once()
        called_hass2, called_opts2 = helper_mock.call_args[0]
        assert called_hass2 is hass
        assert called_opts2[module_key] is True
        assert called_opts2[CONF_DOG_NAME] == 'Fido'
        teardown_mock.assert_not_called()

    import asyncio
    asyncio.run(run_test())


def test_module_helpers_and_unload():
    """Verify helper creation, setup and unload utilities."""

    async def run_test():
        test_module = module_registry.Module(
            setup=AsyncMock(),
            teardown=AsyncMock(),
            ensure_helpers=AsyncMock(),
        )
        hass = object()
        entry = object()
        opts = {"test": True}

        with patch.dict(module_registry.MODULES, {"test": test_module}, clear=True):
            await module_registry.async_ensure_helpers(hass, opts)
            test_module.ensure_helpers.assert_called_once_with(hass, opts)

            await module_registry.async_setup_modules(hass, entry, opts)
            test_module.setup.assert_called_once_with(hass, entry)

            await module_registry.async_unload_modules(hass, entry)
            test_module.teardown.assert_called_once_with(hass, entry)

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


def test_module_error_handling(caplog):
    """Modules raising errors should log exceptions and not stop processing."""

    async def run_test():
        failing = module_registry.Module(
            setup=AsyncMock(side_effect=Exception("boom")),
            teardown=AsyncMock(side_effect=Exception("boom")),
            ensure_helpers=AsyncMock(side_effect=Exception("boom")),
        )
        working = module_registry.Module(
            setup=AsyncMock(),
            teardown=AsyncMock(),
            ensure_helpers=AsyncMock(),
        )

        hass = object()
        entry = object()
        opts = {"fail": True, "ok": True}

        with patch.dict(module_registry.MODULES, {"fail": failing, "ok": working}, clear=True):
            with patch.object(
                module_registry._LOGGER, "exception", wraps=module_registry._LOGGER.exception
            ) as log_exc:
                with caplog.at_level(logging.ERROR):
                    await module_registry.async_ensure_helpers(hass, opts)
                    await module_registry.async_setup_modules(hass, entry, opts)
                    await module_registry.async_unload_modules(hass, entry)

        failing.ensure_helpers.assert_called_once_with(hass, opts)
        failing.setup.assert_called_once_with(hass, entry)
        failing.teardown.assert_called_once_with(hass, entry)
        working.ensure_helpers.assert_called_once_with(hass, opts)
        working.setup.assert_called_once_with(hass, entry)
        working.teardown.assert_called_once_with(hass, entry)

        assert log_exc.call_count == 3
        log_exc.assert_any_call("Error ensuring helpers for module %s", "fail")
        log_exc.assert_any_call("Error %s module %s", "setting up", "fail")
        log_exc.assert_any_call("Error tearing down module %s", "fail")

        assert "Error ensuring helpers for module fail" in caplog.text
        assert "Error setting up module fail" in caplog.text
        assert "Error tearing down module fail" in caplog.text

    import asyncio
    asyncio.run(run_test())


def test_default_opt_precedence():
    """Defaults and opts determine module enablement."""

    async def run_test():
        default_on = module_registry.Module(
            setup=AsyncMock(),
            teardown=AsyncMock(),
            ensure_helpers=AsyncMock(),
            default=True,
        )
        default_off = module_registry.Module(
            setup=AsyncMock(),
            teardown=AsyncMock(),
            ensure_helpers=AsyncMock(),
            default=False,
        )

        hass = object()
        entry = object()

        with patch.dict(module_registry.MODULES, {"on": default_on, "off": default_off}, clear=True):
            # No opts provided -> use defaults
            await module_registry.async_ensure_helpers(hass, {})
            await module_registry.async_setup_modules(hass, entry, {})

            default_on.ensure_helpers.assert_called_once_with(hass, {})
            default_on.setup.assert_called_once_with(hass, entry)
            default_on.teardown.assert_not_called()
            default_off.ensure_helpers.assert_not_called()
            default_off.setup.assert_not_called()
            default_off.teardown.assert_called_once_with(hass, entry)

            default_on.ensure_helpers.reset_mock()
            default_on.setup.reset_mock()
            default_on.teardown.reset_mock()
            default_off.ensure_helpers.reset_mock()
            default_off.setup.reset_mock()
            default_off.teardown.reset_mock()

            # opts override defaults
            opts = {"on": False, "off": True}
            await module_registry.async_ensure_helpers(hass, opts)
            await module_registry.async_setup_modules(hass, entry, opts)

            default_on.ensure_helpers.assert_not_called()
            default_on.setup.assert_not_called()
            default_on.teardown.assert_called_once_with(hass, entry)
            default_off.ensure_helpers.assert_called_once_with(hass, opts)
            default_off.setup.assert_called_once_with(hass, entry)
            default_off.teardown.assert_not_called()

    import asyncio
    asyncio.run(run_test())
