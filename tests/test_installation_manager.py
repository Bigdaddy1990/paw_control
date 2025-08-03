import asyncio
import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries

sys.path.insert(0, os.path.abspath("."))

from custom_components.pawcontrol.const import (
    DOMAIN,
    CONF_CREATE_DASHBOARD,
    CONF_DOG_NAME,
)
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
            expected_opts = {
                CONF_CREATE_DASHBOARD: True,
                CONF_DOG_NAME: "Test",
            }
            ensure_helpers.assert_awaited_once_with(hass, expected_opts)
            setup_modules.assert_awaited_once_with(
                hass, entry, expected_opts
            )
            create_dashboard.assert_not_called()

    asyncio.run(run_test())


@pytest.mark.parametrize("dog_in_options", [False, True])
def test_setup_entry_creates_dashboard_when_dog_name_present(dog_in_options):
    """Dashboard creation should occur when dog name explicitly provided."""

    async def run_test():
        hass = SimpleNamespace()
        data = {CONF_DOG_NAME: "Fido"} if not dog_in_options else {}
        entry = config_entries.ConfigEntry(
            version=1,
            minor_version=1,
            domain=DOMAIN,
            title="Test Title",
            data=data,
            source="user",
        )
        entry.options = {CONF_CREATE_DASHBOARD: True}
        if dog_in_options:
            entry.options[CONF_DOG_NAME] = "Fido"

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
            expected_opts = {
                CONF_CREATE_DASHBOARD: True,
                CONF_DOG_NAME: "Fido",
            }
            ensure_helpers.assert_awaited_once_with(hass, expected_opts)
            setup_modules.assert_awaited_once_with(hass, entry, expected_opts)
            create_dashboard.assert_awaited_once_with(hass, "Fido")

    asyncio.run(run_test())

