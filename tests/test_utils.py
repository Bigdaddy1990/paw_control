import asyncio
import sys
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

# Ensure custom component package is importable
sys.path.insert(0, str(Path().resolve()))

from custom_components.pawcontrol.exceptions import InvalidCoordinates
from custom_components.pawcontrol.utils import (
    calculate_dog_calories_per_day,
    calculate_speed_kmh,
    call_service,
    format_distance,
    format_duration,
    format_weight,
    merge_entry_options,
    parse_coordinates_string,
    time_since_last_activity,
    validate_dog_name,
    validate_weight,
)


def test_calculate_dog_calories_positive():
    """Calorie calculation should match expected value for typical weight."""
    assert calculate_dog_calories_per_day(10) == 629


def test_calculate_dog_calories_invalid_weight():
    """Invalid or negative weights return 0 calories."""
    assert calculate_dog_calories_per_day(-5) == 0
    assert calculate_dog_calories_per_day("bad") == 0


def test_merge_entry_options_overrides_data():
    """Options should override data when merged."""
    entry = SimpleNamespace(data={"a": 1, "c": 3}, options={"b": 2, "c": 4})
    assert merge_entry_options(entry) == {"a": 1, "b": 2, "c": 4}


def test_call_service_wrapper():
    """call_service should proxy to hass.services.async_call."""

    async def run_test():
        mock_call = AsyncMock()
        hass = SimpleNamespace(services=SimpleNamespace(async_call=mock_call))
        await call_service(hass, "test", "do", {"x": 1})
        mock_call.assert_called_once_with("test", "do", {"x": 1}, blocking=True)

    asyncio.run(run_test())


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


def test_validate_weight_rejects_invalid_values():
    """validate_weight should reject non-finite or non-positive values."""
    assert validate_weight(10)
    assert not validate_weight(0)
    assert not validate_weight(-1)
    assert not validate_weight(float("nan"))
    assert not validate_weight(float("inf"))
    assert not validate_weight("bad")


def test_calculate_speed_kmh_handles_invalid_inputs():
    """Speed calculations should handle invalid or negative values gracefully."""
    assert calculate_speed_kmh(1000, 3600) == 1.0
    assert calculate_speed_kmh(-100, 10) == 0.0
    assert calculate_speed_kmh(100, 0) == 0.0
    assert calculate_speed_kmh("bad", 10) == 0.0
    assert calculate_speed_kmh(100, "bad") == 0.0


@pytest.mark.parametrize("value", [None, "bad", -1, 0])
def test_format_duration_invalid_types_and_values(value):
    """Invalid types or non-positive durations should return '0 min'."""
    assert format_duration(value) == "0 min"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("10", "10 min"),
        (5.5, "5 min"),
        (125.0, "2h 5min"),
    ],
)
def test_format_duration_accepts_numeric_strings_and_floats(value, expected):
    """Numeric strings and floats should be converted to minutes."""
    assert format_duration(value) == expected


def test_format_duration_under_an_hour():
    """Durations under an hour should be shown in minutes."""
    assert format_duration(45) == "45 min"


def test_format_duration_exact_hours():
    """Exact multiples of an hour should omit minutes."""
    assert format_duration(120) == "2h"


def test_format_duration_hours_and_minutes():
    """Durations with remaining minutes should show hours and minutes."""
    assert format_duration(125) == "2h 5min"


def test_time_since_last_activity_handles_naive_and_aware():
    """Ensure time_since_last_activity works for naive and timezone-aware inputs."""
    tolerance = timedelta(seconds=1)

    # Naive timestamp without timezone info
    past_naive = datetime.now(UTC) - timedelta(minutes=5)
    past_naive = past_naive.replace(tzinfo=None)
    naive_result = time_since_last_activity(past_naive.isoformat())
    expected_naive = datetime.now(UTC).replace(tzinfo=None) - past_naive
    assert isinstance(naive_result, timedelta)
    assert abs(naive_result - expected_naive) <= tolerance

    # UTC timestamp with trailing 'Z'
    past_utc = datetime.now(UTC) - timedelta(minutes=5)
    utc_result = time_since_last_activity(past_utc.isoformat().replace("+00:00", "Z"))
    expected_utc = datetime.now(UTC) - past_utc
    assert abs(utc_result - expected_utc) <= tolerance

    # Timestamp with explicit timezone offset
    tz = timezone(timedelta(hours=2))
    past_offset = datetime.now(tz) - timedelta(minutes=5)
    offset_result = time_since_last_activity(past_offset.isoformat())
    expected_offset = datetime.now(tz) - past_offset
    assert abs(offset_result - expected_offset) <= tolerance


def test_time_since_last_activity_accepts_datetime_object():
    """Datetime objects should be handled directly without requiring conversion."""
    tolerance = timedelta(seconds=1)
    past_time = datetime.now(UTC) - timedelta(minutes=5)
    result = time_since_last_activity(past_time)
    expected = datetime.now(UTC) - past_time
    assert isinstance(result, timedelta)
    assert abs(result - expected) <= tolerance


def test_time_since_last_activity_future_time_clamped():
    """Future timestamps should be treated as 0 elapsed time."""
    future_time = datetime.now(UTC) + timedelta(minutes=5)
    result = time_since_last_activity(future_time.isoformat())
    assert result == timedelta(0)

def test_validate_dog_name_enforces_rules():
    """Dog names must follow pattern, length and start with a letter."""
    assert validate_dog_name("Buddy")
    assert not validate_dog_name("1Buddy")
    assert not validate_dog_name("Bad!")
    assert not validate_dog_name("a" * 31)


def test_parse_coordinates_string_accepts_various_separators():
    """Valid coordinate strings may use commas, semicolons or whitespace."""
    assert parse_coordinates_string("10 , 20") == (10.0, 20.0)
    assert parse_coordinates_string("10 ;20") == (10.0, 20.0)
    assert parse_coordinates_string("10 20") == (10.0, 20.0)


def test_parse_coordinates_string_invalid_inputs():
    """parse_coordinates_string should raise InvalidCoordinates for bad input."""
    with pytest.raises(InvalidCoordinates):
        parse_coordinates_string("10")  # missing lon
    with pytest.raises(InvalidCoordinates):
        parse_coordinates_string(None)
