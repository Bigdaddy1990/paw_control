import os
import sys
import asyncio
from unittest.mock import AsyncMock, patch

# Ensure custom component package is importable
sys.path.insert(0, os.path.abspath("."))

from custom_components.pawcontrol.setup_helpers import (
    async_create_helpers_for_dog,
    async_remove_helpers_for_dog,
)


def test_async_create_helpers_for_dog_invokes_expected_services():
    """Ensure helper creation issues the correct service calls."""

    async def run_test() -> None:
        hass = object()
        with patch(
            "custom_components.pawcontrol.setup_helpers.safe_service_call",
            AsyncMock(),
        ) as mock_call:
            await async_create_helpers_for_dog(hass, "rex")
        called_entities = {c.args[3]["entity_id"] for c in mock_call.await_args_list}
        assert mock_call.await_count == 6
        assert called_entities == {
            "input_datetime.last_walk_rex",
            "input_boolean.visitor_mode_rex",
            "input_text.last_activity_rex",
            "counter.feeding_rex",
            "counter.walk_rex",
            "counter.potty_rex",
        }

    asyncio.run(run_test())


def test_remove_helpers_invokes_services():
    """Ensure helper removal calls expected services."""

    async def run_test() -> None:
        hass = object()
        with patch(
            "custom_components.pawcontrol.setup_helpers.safe_service_call",
            AsyncMock(),
        ) as mock_call:
            await async_remove_helpers_for_dog(hass, "rex")
        called_entities = {c.args[3]["entity_id"] for c in mock_call.await_args_list}
        assert mock_call.await_count == 6
        assert called_entities == {
            "input_datetime.last_walk_rex",
            "input_boolean.visitor_mode_rex",
            "input_text.last_activity_rex",
            "counter.feeding_rex",
            "counter.walk_rex",
            "counter.potty_rex",
        }

    asyncio.run(run_test())
