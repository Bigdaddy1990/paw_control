import asyncio

from custom_components.pawcontrol.coordinator import PawControlCoordinator


class DummyState:
    def __init__(self, state):
        self.state = state


class DummyStates:
    def __init__(self, states):
        self._states = states

    def get(self, entity_id):
        return self._states.get(entity_id)


class DummyHass:
    def __init__(self, states):
        self.states = DummyStates(states)


def make_coordinator(morning="off", evening="off"):
    coordinator = PawControlCoordinator.__new__(PawControlCoordinator)
    coordinator.hass = DummyHass(
        {
            "input_boolean.Bello_feeding_morning": DummyState(morning),
            "input_boolean.Bello_feeding_evening": DummyState(evening),
        }
    )
    coordinator.dog_name = "Bello"
    return coordinator


def test_needs_feeding_logic():
    status = asyncio.run(make_coordinator("on", "off")._get_feeding_status())
    assert status["needs_feeding"]

    status = asyncio.run(make_coordinator("on", "on")._get_feeding_status())
    assert not status["needs_feeding"]

    status = asyncio.run(make_coordinator("off", "off")._get_feeding_status())
    assert status["needs_feeding"]
