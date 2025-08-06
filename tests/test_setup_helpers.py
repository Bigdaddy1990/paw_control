import asyncio
from unittest.mock import AsyncMock, patch

from custom_components.pawcontrol import setup_helpers


def test_async_create_helpers_for_dog_invokes_expected_services():
    """Ensure helper creation issues the correct service calls."""

    async def run_test() -> None:
        hass = object()
        with patch(
            "custom_components.pawcontrol.setup_helpers.safe_service_call",
            AsyncMock(),
        ) as mock_call:
            await setup_helpers.async_create_helpers_for_dog(hass, "rex")
        # Three base helpers + three counter helpers
        assert mock_call.await_count == 6
        domains = [call.args[1] for call in mock_call.await_args_list]
        services = [call.args[2] for call in mock_call.await_args_list]
        assert domains.count("input_datetime") == 1
        assert domains.count("input_boolean") == 1
        assert domains.count("input_text") == 1
        assert domains.count("counter") == 3
        assert "set_datetime" in services
        assert "turn_off" in services
        assert "set_value" in services
        assert services.count("configure") == 3

    asyncio.run(run_test())
