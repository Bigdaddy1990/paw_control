import builtins
import logging
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import AsyncMock

import pytest

# Ensure custom component package is importable
sys.path.insert(0, str(Path().resolve()))

from custom_components.pawcontrol import (
    async_setup_entry,
    async_unload_entry,
    dashboard,
)
from custom_components.pawcontrol.const import CONF_DOG_NAME, DOMAIN


class DummyConfigEntry:
    def __init__(self, options=None, data=None):
        self.options = options or {}
        self.data = data or {}


class FakeServices:
    def __init__(self):
        self._services = {}

    def async_register(self, domain, service, func):
        self._services[(domain, service)] = func

    def has_service(self, domain, service):
        return (domain, service) in self._services

    async def async_call(self, domain, service):
        await self._services[(domain, service)](None)


class FakeHass:
    def __init__(self):
        self.services = FakeServices()


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio("asyncio")
async def test_modules_load_and_unload(monkeypatch):
    called = []

    for module_name in ["gps_system", "health_system"]:
        module = ModuleType(module_name)

        async def setup(_hass, _entry, name=module_name):
            called.append(("setup", name))

        async def unload(_hass, _entry, name=module_name):
            called.append(("unload", name))

        module.async_setup_entry = setup  # type: ignore[attr-defined]
        module.async_unload_entry = unload  # type: ignore[attr-defined]
        monkeypatch.setitem(
            sys.modules, f"custom_components.pawcontrol.{module_name}", module
        )

    original_import = builtins.__import__

    def fake_import(name, _globals=None, _locals=None, fromlist=(), level=0):
        if level == 1 and name in (".gps_system", ".health_system"):
            return sys.modules[f"custom_components.pawcontrol.{name[1:]}"]
        return original_import(name, _globals, _locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    hass = FakeHass()
    entry = DummyConfigEntry(options={"modules": ["gps", "health"]})

    await async_setup_entry(hass, entry)

    assert ("setup", "gps_system") in called
    assert ("setup", "health_system") in called

    await async_unload_entry(hass, entry)

    assert ("unload", "gps_system") in called
    assert ("unload", "health_system") in called


@pytest.mark.anyio("asyncio")
async def test_dashboard_service_registration_and_call(monkeypatch):
    hass = FakeHass()
    entry = DummyConfigEntry(data={CONF_DOG_NAME: "Rex"})

    module = ModuleType("gps_system")

    async def setup(_hass, _entry):
        pass

    async def unload(_hass, _entry):
        pass

    module.async_setup_entry = setup  # type: ignore[attr-defined]
    module.async_unload_entry = unload  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "custom_components.pawcontrol.gps_system", module)

    original_import = builtins.__import__

    def fake_import(name, _globals=None, _locals=None, fromlist=(), level=0):
        if level == 1 and name == ".gps_system":
            return sys.modules["custom_components.pawcontrol.gps_system"]
        return original_import(name, _globals, _locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    create_dashboard = AsyncMock()
    monkeypatch.setattr(dashboard, "create_dashboard", create_dashboard)

    await async_setup_entry(hass, entry)

    assert hass.services.has_service(DOMAIN, "create_dashboard")

    await hass.services.async_call(DOMAIN, "create_dashboard")

    create_dashboard.assert_awaited_once_with(hass, "Rex")


@pytest.mark.anyio("asyncio")
async def test_dashboard_service_missing_function(monkeypatch, caplog):
    hass = FakeHass()
    entry = DummyConfigEntry(data={CONF_DOG_NAME: "Rex"})

    module = ModuleType("gps_system")

    async def setup(_hass, _entry):
        pass

    async def unload(_hass, _entry):
        pass

    module.async_setup_entry = setup  # type: ignore[attr-defined]
    module.async_unload_entry = unload  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "custom_components.pawcontrol.gps_system", module)

    original_import = builtins.__import__

    def fake_import(name, _globals=None, _locals=None, fromlist=(), level=0):
        if level == 1 and name == ".gps_system":
            return sys.modules["custom_components.pawcontrol.gps_system"]
        return original_import(name, _globals, _locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    monkeypatch.delattr(dashboard, "create_dashboard", raising=False)

    await async_setup_entry(hass, entry)

    assert hass.services.has_service(DOMAIN, "create_dashboard")

    with caplog.at_level(logging.ERROR):
        await hass.services.async_call(DOMAIN, "create_dashboard")

    assert "missing create_dashboard function" in caplog.text
