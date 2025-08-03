import os
import sys
import pytest

# Ensure custom component package is importable
sys.path.insert(0, os.path.abspath('.'))

from custom_components.pawcontrol.utils import calculate_dog_calories_per_day


def test_calculate_dog_calories_positive():
    """Calorie calculation should match expected value for typical weight."""
    assert calculate_dog_calories_per_day(10) == 629


def test_calculate_dog_calories_invalid_weight():
    """Invalid or negative weights should return 0 calories instead of raising errors."""
    assert calculate_dog_calories_per_day(-5) == 0
    assert calculate_dog_calories_per_day("bad") == 0
