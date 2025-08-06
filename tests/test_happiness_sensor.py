import os
import sys

sys.path.insert(0, os.path.abspath("."))

from custom_components.pawcontrol.coordinator import PawControlCoordinator
from custom_components.pawcontrol.sensor import PawControlHappinessSensor


class DummyCoordinator:
    def __init__(self, data=None):
        self.data = data or {}


def test_happiness_sensor_reads_state():
    coordinator = DummyCoordinator({"happiness_status": "Happy"})
    sensor = PawControlHappinessSensor(coordinator, "Bello")
    assert sensor.native_value == "Happy"

    coordinator.data["happiness_status"] = "Needs attention"
    assert sensor.native_value == "Needs attention"


def test_calculate_happiness_logic():
    coordinator = PawControlCoordinator.__new__(PawControlCoordinator)
    data = {
        "feeding_status": {"morning_fed": True, "evening_fed": True},
        "activity_status": {"walked_today": True},
    }
    assert coordinator._calculate_happiness(data) == "Happy"

    data["feeding_status"]["evening_fed"] = False
    assert coordinator._calculate_happiness(data) == "Needs attention"

    data["feeding_status"]["evening_fed"] = True
    data["activity_status"]["walked_today"] = False
    assert coordinator._calculate_happiness(data) == "Needs attention"

