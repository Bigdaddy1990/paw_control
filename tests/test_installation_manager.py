import asyncio
import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries

sys.path.insert(0, os.path.abspath("."))

from custom_components.pawcontrol.const import DOMAIN, CONF_CREATE_DASHBOARD
from custom_components.pawcontrol.installation_manager import InstallationManager


def test_setup_entry_handles_missing_dog_name():
    """Dashboard creation should be skipped gracefully if dog name missing."""

    async def run_test():
        hass = SimpleNamespace()
        entry = config_entries.ConfigEntry(
            version=1,
            minor_version=1,
            domain=DOMAIN,
            title="Test",
            data={},
            source="user",
        )
        entry.options = {CONF_CREATE_DASHBOARD: True}

        manager = InstallationManager()

        with patch(
            "custom_components.pawcontrol.installation_manager.async_ensure_helpers",
            new=AsyncMock(),
        ) as ensure_helpers, patch(
            "custom_components.pawcontrol.installation_manager.async_setup_modules",
            new=AsyncMock(),
        ) as setup_modules, patch(
            "custom_components.pawcontrol.dashboard.create_dashboard",
            new=AsyncMock(),
        ) as create_dashboard:
            result = await manager.setup_entry(hass, entry)
            assert result is True
            ensure_helpers.assert_awaited_once_with(hass, {CONF_CREATE_DASHBOARD: True})
            setup_modules.assert_awaited_once_with(
                hass, entry, {CONF_CREATE_DASHBOARD: True}
            )
            create_dashboard.assert_not_called()

    asyncio.run(run_test())
