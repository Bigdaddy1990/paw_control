import asyncio
from types import SimpleNamespace

from custom_components.pawcontrol import dashboard


class DummyStates:
    def __init__(self) -> None:
        self.calls = []

    def async_set(self, entity_id, state, attrs=None):
        self.calls.append((entity_id, state, attrs))


def test_create_dashboard_slugifies_name():
    async def run_test() -> None:
        hass = SimpleNamespace(states=DummyStates())
        await dashboard.create_dashboard(hass, "Mr Fido")
        assert hass.states.calls, "Dashboard sensor not created"
        entity_id, yaml_content, _ = hass.states.calls[0]
        assert entity_id == "sensor.mr_fido_dashboard_yaml"
        assert "sensor.mr_fido_health" in yaml_content

    asyncio.run(run_test())
