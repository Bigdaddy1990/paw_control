import os
import sys
from datetime import datetime

import asyncio

sys.path.insert(0, os.path.abspath("."))

from custom_components.pawcontrol.const import (
    ATTR_DOG_NAME,
    ATTR_LAST_UPDATED,
    DOMAIN,
)
from custom_components.pawcontrol.entities import (
    PawControlBaseEntity,
    PawControlBinarySensorEntity,
    PawControlButtonEntity,
    PawControlDateTimeEntity,
    PawControlNumberEntity,
    PawControlSelectEntity,
    PawControlSensorEntity,
    PawControlSwitchEntity,
    PawControlTextEntity,
)


class DummyCoordinator:
    def __init__(self, data=None):
        self.data = data or {}

    async def async_request_refresh(self):
        return None


def test_text_entity_clamps_value():
    entity = PawControlTextEntity(DummyCoordinator(), "Name", dog_name="Bello", unique_suffix="name", max_length=5)
    asyncio.run(entity.async_set_value("abcdefgh"))
    assert entity.native_value == "abcde"


def test_number_entity_clamps_value():
    entity = PawControlNumberEntity(
        DummyCoordinator(), "Level", dog_name="Bello", unique_suffix="level", min_value=0, max_value=10
    )
    asyncio.run(entity.async_set_native_value(15))
    assert entity.native_value == 10
    asyncio.run(entity.async_set_native_value(-5))
    assert entity.native_value == 0


def test_select_entity_validates_option():
    entity = PawControlSelectEntity(
        DummyCoordinator(), "Mode", dog_name="Bello", unique_suffix="mode", options=["a", "b"]
    )
    asyncio.run(entity.async_select_option("c"))
    assert entity.current_option == "a"
    asyncio.run(entity.async_select_option("b"))
    assert entity.current_option == "b"


def test_datetime_entity_converts_value():
    coordinator = DummyCoordinator({"Time": "2023-10-10T10:00:00+00:00"})
    entity = PawControlDateTimeEntity(coordinator, "Time")
    entity._update_state()
    value = entity.native_value
    assert isinstance(value, datetime)
    assert value.year == 2023
    assert value.month == 10
    assert value.day == 10
    assert value.hour == 10
    assert value.minute == 0


def test_binary_sensor_inherits_attributes_and_converts():
    coordinator = DummyCoordinator({"Door": "on"})
    entity = PawControlBinarySensorEntity(
        coordinator, "Door", dog_name="Bello", unique_suffix="door"
    )
    entity._update_state()
    assert entity.is_on is True
    assert entity.unique_id == f"{DOMAIN}_bello_door"
    assert entity.device_info["name"] == "Paw Control - Bello"
    attrs = entity.extra_state_attributes
    assert attrs[ATTR_DOG_NAME] == "Bello"
    assert ATTR_LAST_UPDATED in attrs

    coordinator = DummyCoordinator({"Door": "off"})
    entity = PawControlBinarySensorEntity(
        coordinator, "Door", dog_name="Bello", unique_suffix="door"
    )
    entity._update_state()
    assert entity.is_on is False


def test_sensor_entity_inherits_state_and_device_info():
    coordinator = DummyCoordinator({"Temp": 25})
    entity = PawControlSensorEntity(
        coordinator, "Temp", dog_name="Bello", unique_suffix="temp"
    )
    entity._update_state()
    assert entity.state == 25
    assert entity.unique_id == f"{DOMAIN}_bello_temp"
    assert entity.device_info["name"] == "Paw Control - Bello"
    attrs = entity.extra_state_attributes
    assert attrs[ATTR_DOG_NAME] == "Bello"
    assert ATTR_LAST_UPDATED in attrs


def test_switch_entity_inherits_attributes_and_converts():
    coordinator = DummyCoordinator({"Light": "true"})
    entity = PawControlSwitchEntity(
        coordinator, "Light", dog_name="Bello", unique_suffix="light"
    )
    entity._update_state()
    assert entity.is_on is True
    assert entity.unique_id == f"{DOMAIN}_bello_light"
    assert entity.device_info["name"] == "Paw Control - Bello"
    attrs = entity.extra_state_attributes
    assert attrs[ATTR_DOG_NAME] == "Bello"
    assert ATTR_LAST_UPDATED in attrs


def test_button_entity_has_device_info_and_attributes():
    entity = PawControlButtonEntity(
        DummyCoordinator(), "Feed", dog_name="Bello", unique_suffix="feed"
    )
    assert isinstance(entity, PawControlBaseEntity)
    assert entity.unique_id == f"{DOMAIN}_bello_feed"
    assert entity.device_info["name"] == "Paw Control - Bello"
    attrs = entity.extra_state_attributes
    assert attrs[ATTR_DOG_NAME] == "Bello"
    assert ATTR_LAST_UPDATED in attrs
