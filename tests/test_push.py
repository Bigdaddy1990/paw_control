import asyncio
import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

sys.path.insert(0, os.path.abspath("."))

from custom_components.pawcontrol.push import send_notification


def _hass(states_state="on"):
    return SimpleNamespace(
        states=SimpleNamespace(get=lambda _: SimpleNamespace(state=states_state)),
        services=SimpleNamespace(async_call=AsyncMock()),
        components=SimpleNamespace(
            persistent_notification=SimpleNamespace(create=Mock())
        ),
    )


def test_send_notification_helper_off():
    async def run_test():
        hass = _hass(states_state="off")
        await send_notification(hass, "Buddy", "input_boolean.Buddy_push_active", "Hi", "Title")
        hass.services.async_call.assert_not_called()
        hass.components.persistent_notification.create.assert_not_called()
    asyncio.run(run_test())


def test_send_notification_with_target_calls_notify():
    async def run_test():
        hass = _hass()
        await send_notification(
            hass,
            "Buddy",
            "input_boolean.Buddy_push_active",
            "Hello",
            "Title",
            "mobile",
        )
        hass.services.async_call.assert_called_once_with(
            "notify", "mobile", {"message": "Buddy: Hello", "title": "Title"}, blocking=True
        )
        hass.components.persistent_notification.create.assert_not_called()
    asyncio.run(run_test())


def test_send_notification_without_target_creates_persistent_notification():
    async def run_test():
        hass = _hass()
        await send_notification(
            hass,
            "Buddy",
            "input_boolean.Buddy_push_active",
            "Hello",
            "Title",
        )
        hass.components.persistent_notification.create.assert_called_once_with(
            "Buddy: Hello", title="Title"
        )
        hass.services.async_call.assert_not_called()
    asyncio.run(run_test())
