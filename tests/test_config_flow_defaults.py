import asyncio
import os
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.abspath("."))

import custom_components.pawcontrol.config_flow as config_flow
import custom_components.pawcontrol.const as const

from custom_components.pawcontrol.const import CONF_DOG_NAME, CONF_FEEDING_TIMES


@pytest.mark.parametrize(
    "defaults",
    [
        [],
        ["08:00"],
        ["08:00", "20:00"],
    ],
)
def test_feeding_times_default_is_copied(defaults, monkeypatch):
    monkeypatch.setattr(const, "DEFAULT_FEEDING_TIMES", list(defaults))
    monkeypatch.setattr(
        config_flow, "DEFAULT_FEEDING_TIMES", const.DEFAULT_FEEDING_TIMES
    )

    flow = config_flow.ConfigFlow()
    flow.hass = SimpleNamespace()

    result = asyncio.run(flow.async_step_user())
    data = result["data_schema"]({CONF_DOG_NAME: "Rex"})
    assert data[CONF_FEEDING_TIMES] == defaults
    assert data[CONF_FEEDING_TIMES] is not config_flow.DEFAULT_FEEDING_TIMES
    data[CONF_FEEDING_TIMES].append("extra")
    assert config_flow.DEFAULT_FEEDING_TIMES == defaults
    assert const.DEFAULT_FEEDING_TIMES == defaults
