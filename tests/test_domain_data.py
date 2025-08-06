import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0, os.path.abspath("."))

import custom_components.pawcontrol as integration
from custom_components.pawcontrol.const import DOMAIN
from custom_components.pawcontrol.installation_manager import InstallationManager
from homeassistant import config_entries


def test_manager_lifecycle(monkeypatch):
    async def run_test():
        entry = config_entries.ConfigEntry(
            version=1,
            minor_version=1,
            domain=DOMAIN,
            title="Fido",
            data={},
            source="user",
        )

        hass = SimpleNamespace()

        setup_mock = AsyncMock(return_value=True)
        unload_mock = AsyncMock(return_value=True)
        monkeypatch.setattr(InstallationManager, "setup_entry", setup_mock)
        monkeypatch.setattr(InstallationManager, "unload_entry", unload_mock)

        await integration.async_setup_entry(hass, entry)
        manager = integration.get_manager(hass, entry.entry_id)
        assert isinstance(manager, InstallationManager)

        await integration.async_unload_entry(hass, entry)
        assert integration.get_manager(hass, entry.entry_id) is None
        assert entry.entry_id not in integration.get_domain_data(hass)
        setup_mock.assert_awaited_once_with(hass, entry)
        unload_mock.assert_awaited_once_with(hass, entry)

    import asyncio
    asyncio.run(run_test())
