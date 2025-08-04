import os
import sys

import pytest

sys.path.insert(0, os.path.abspath("."))

from custom_components.pawcontrol.helpers.entity import clamp_value, ensure_option


def test_clamp_value():
    assert clamp_value(5, 0, 10) == 5
    assert clamp_value(-1, 0, 10) == 0
    assert clamp_value(11, 0, 10) == 10


def test_ensure_option():
    options = ["a", "b"]
    assert ensure_option("b", options) == "b"
    assert ensure_option("c", options) == "a"
    assert ensure_option("c", []) == "c"
