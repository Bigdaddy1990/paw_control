import asyncio
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.abspath("."))

from custom_components.pawcontrol import async_setup
from custom_components.pawcontrol.const import DOMAIN


def _hass():
    services: dict[str, dict[str, object]] = {}

    def async_register(domain, service, handler):
        services.setdefault(domain, {})[service] = handler

    def has_service(domain, service):
        return service in services.get(domain, {})

    return SimpleNamespace(
        data={},
        services=SimpleNamespace(
            async_register=async_register, has_service=has_service
        ),
    )


def test_async_setup_registers_actionable_service():
    async def run_test():
        hass = _hass()
        assert await async_setup(hass, {})
        assert hass.services.has_service(DOMAIN, "send_notification")

    asyncio.run(run_test())
