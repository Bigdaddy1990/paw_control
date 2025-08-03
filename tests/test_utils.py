import os
import sys

import pytest

# Ensure custom component package is importable
sys.path.insert(0, os.path.abspath("."))

from custom_components.pawcontrol.utils import (
    calculate_dog_calories_per_day,
    format_distance,
    format_duration,
    format_weight,
)


def test_calculate_dog_calories_positive():
    """Calorie calculation should match expected value for typical weight."""
    assert calculate_dog_calories_per_day(10) == 629


def test_calculate_dog_calories_invalid_weight():
    """Invalid or negative weights should return 0 calories instead of raising errors."""
    assert calculate_dog_calories_per_day(-5) == 0
    assert calculate_dog_calories_per_day("bad") == 0


def test_format_distance_handles_various_inputs():
    """Distances should be formatted and invalid values handled gracefully."""
    assert format_distance(500) == "500m"
    assert format_distance(1500) == "1.5km"
    assert format_distance(1000) == "1km"
    assert format_distance(-100) == "0m"
    assert format_distance("oops") == "0m"


def test_format_weight_handles_various_inputs():
    """Weights should be formatted and invalid values handled gracefully."""
    assert format_weight(10) == "10.0kg"
    assert format_weight("bad") == "0.0kg"
    assert format_weight(-5) == "0.0kg"


@pytest.mark.parametrize("value", [None, "10", 5.5, -1, 0])
def test_format_duration_invalid_types_and_values(value):
    """Invalid types or non-positive durations should return '0 min'."""
    assert format_duration(value) == "0 min"


def test_format_duration_under_an_hour():
    """Durations under an hour should be shown in minutes."""
    assert format_duration(45) == "45 min"


def test_format_duration_exact_hours():
    """Exact multiples of an hour should omit minutes."""
    assert format_duration(120) == "2h"


def test_format_duration_hours_and_minutes():
    """Durations with remaining minutes should show hours and minutes."""
    assert format_duration(125) == "2h 5min"
