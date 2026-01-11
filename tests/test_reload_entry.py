import asyncio
from unittest.mock import AsyncMock, patch

from custom_components.pawcontrol import (
    async_reload_entry,
)


def test_reload_entry_calls_setup_and_unload():
    """Reloading a config entry unloads and sets it up again."""

    async def run_test() -> None:
        hass = object()
        entry = object()
        with (
            patch(
                "custom_components.pawcontrol.async_unload_entry",
                AsyncMock(return_value=True),
            ) as unload,
            patch(
                "custom_components.pawcontrol.async_setup_entry",
                AsyncMock(return_value=True),
            ) as setup,
        ):
            result = await async_reload_entry(hass, entry)
        assert result is True
        unload.assert_awaited_once_with(hass, entry)
        setup.assert_awaited_once_with(hass, entry)

    asyncio.run(run_test())


def test_reload_entry_aborts_when_unload_fails():
    """Reload fails if unloading fails."""

    async def run_test() -> None:
        hass = object()
        entry = object()
        with (
            patch(
                "custom_components.pawcontrol.async_unload_entry",
                AsyncMock(return_value=False),
            ) as unload,
            patch(
                "custom_components.pawcontrol.async_setup_entry",
                AsyncMock(return_value=True),
            ) as setup,
        ):
            result = await async_reload_entry(hass, entry)
        assert result is False
        unload.assert_awaited_once_with(hass, entry)
        setup.assert_not_awaited()

    asyncio.run(run_test())
