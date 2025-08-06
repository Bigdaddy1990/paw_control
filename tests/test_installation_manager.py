"""Tests for the InstallationManager module."""

import os
import sys
from unittest.mock import AsyncMock, patch

# Ensure the custom component package is importable
sys.path.insert(0, os.path.abspath("."))

from custom_components.pawcontrol.const import (
    CONF_CREATE_DASHBOARD,
    CONF_DOG_NAME,
    DOMAIN,
)
from custom_components.pawcontrol.installation_manager import InstallationManager
from homeassistant import config_entries


def test_dashboard_not_created_without_dog_name():
    """Dashboard is skipped when no dog name was provided."""

    async def run_test() -> None:
        manager = InstallationManager()
        hass = object()
        entry = config_entries.ConfigEntry(
            version=1,
            minor_version=1,
            domain=DOMAIN,
            title="Fido",
            data={},
            source="user",
            options={CONF_CREATE_DASHBOARD: True},
        )

        ensure_mock = AsyncMock()
        setup_mock = AsyncMock()
        dash_mock = AsyncMock()

        with (
            patch(
                "custom_components.pawcontrol.installation_manager.async_ensure_helpers",
                ensure_mock,
            ),
            patch(
                "custom_components.pawcontrol.installation_manager.async_setup_modules",
                setup_mock,
            ),
            patch(
                "custom_components.pawcontrol.dashboard.create_dashboard",
                dash_mock,
            ),
        ):
            await manager.setup_entry(hass, entry)

        ensure_mock.assert_called_once()
        setup_mock.assert_called_once()
        dash_mock.assert_not_called()
        called_opts = ensure_mock.call_args[0][1]
        assert called_opts[CONF_DOG_NAME] == "Fido"

    import asyncio

    asyncio.run(run_test())


def test_dashboard_created_when_dog_name_present():
    """Dashboard is created when dog name exists and option is enabled."""

    async def run_test() -> None:
        manager = InstallationManager()
        hass = object()
        entry = config_entries.ConfigEntry(
            version=1,
            minor_version=1,
            domain=DOMAIN,
            title="Rex",
            data={CONF_DOG_NAME: "Rex", CONF_CREATE_DASHBOARD: True},
            source="user",
        )

        ensure_mock = AsyncMock()
        setup_mock = AsyncMock()
        dash_mock = AsyncMock()

        with (
            patch(
                "custom_components.pawcontrol.installation_manager.async_ensure_helpers",
                ensure_mock,
            ),
            patch(
                "custom_components.pawcontrol.installation_manager.async_setup_modules",
                setup_mock,
            ),
            patch(
                "custom_components.pawcontrol.dashboard.create_dashboard",
                dash_mock,
            ),
        ):
            await manager.setup_entry(hass, entry)

        dash_mock.assert_called_once_with(hass, "Rex")
        ensure_mock.assert_called_once()
        setup_mock.assert_called_once()

    import asyncio

    asyncio.run(run_test())


def test_unload_entry_calls_module_unload():
    """Unloading an entry triggers module unload helpers."""

    async def run_test() -> None:
        manager = InstallationManager()
        hass = object()
        entry = config_entries.ConfigEntry(
            version=1,
            minor_version=1,
            domain=DOMAIN,
            title="Fido",
            data={},
            source="user",
        )

        unload_mock = AsyncMock()
        remove_mock = AsyncMock()

        with (
            patch(
                "custom_components.pawcontrol.installation_manager.async_unload_modules",
                unload_mock,
            ),
            patch(
                "custom_components.pawcontrol.installation_manager.async_remove_helpers_for_dog",
                remove_mock,
            ),
        ):
            result = await manager.unload_entry(hass, entry)

        unload_mock.assert_called_once_with(hass, entry)
        remove_mock.assert_called_once_with(hass, "Fido")
        assert result is True

    import asyncio

    asyncio.run(run_test())

