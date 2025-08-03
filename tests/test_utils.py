import os
import sys
import pytest

# Ensure custom component package is importable
sys.path.insert(0, os.path.abspath('.'))

from custom_components.pawcontrol.utils import (
    calculate_dog_calories_per_day,
    format_distance,
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
    assert format_distance(-100) == "0m"
    assert format_distance("oops") == "0m"
