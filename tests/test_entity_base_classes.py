import os
import sys
from datetime import datetime

import asyncio

sys.path.insert(0, os.path.abspath("."))

from custom_components.pawcontrol.entities.text import PawControlTextEntity
from custom_components.pawcontrol.entities.number import PawControlNumberEntity
from custom_components.pawcontrol.entities.select import PawControlSelectEntity
from custom_components.pawcontrol.entities.datetime import PawControlDateTimeEntity


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
