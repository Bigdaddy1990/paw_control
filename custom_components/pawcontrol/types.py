"""Shared typing helpers for Paw Control."""

from __future__ import annotations

from typing import Literal, NotRequired, Required, TypedDict

from .const import (
    CONF_CREATE_DASHBOARD,
    CONF_DOG_AGE,
    CONF_DOG_BREED,
    CONF_DOG_NAME,
    CONF_DOG_WEIGHT,
    CONF_FEEDING_TIMES,
    CONF_GPS_ENABLE,
    CONF_HEALTH_MODULE,
    CONF_NOTIFICATIONS_ENABLED,
    CONF_VET_CONTACT,
    CONF_WALK_DURATION,
    CONF_WALK_MODULE,
)

PawControlConfigKey = Literal[
    CONF_DOG_NAME,
    CONF_DOG_BREED,
    CONF_DOG_AGE,
    CONF_DOG_WEIGHT,
    CONF_FEEDING_TIMES,
    CONF_WALK_DURATION,
    CONF_VET_CONTACT,
]

PawControlOptionKey = Literal[
    CONF_GPS_ENABLE,
    CONF_NOTIFICATIONS_ENABLED,
    CONF_HEALTH_MODULE,
    CONF_WALK_MODULE,
    CONF_CREATE_DASHBOARD,
]

PawControlModuleKey = Literal[
    CONF_GPS_ENABLE,
    CONF_NOTIFICATIONS_ENABLED,
    CONF_HEALTH_MODULE,
    CONF_WALK_MODULE,
]


class PawControlOptions(TypedDict, total=False):
    """TypedDict for option keys in the options flow."""

    gps_enable: bool
    notifications_enabled: bool
    health_module: bool
    walk_module: bool
    create_dashboard: bool


class PawControlConfigData(TypedDict):
    """TypedDict for config entries created by the config flow."""

    dog_name: str
    dog_breed: str
    dog_age: int
    dog_weight: float
    feeding_times: list[str]
    walk_duration: int
    vet_contact: str
    gps_enable: bool
    notifications_enabled: bool
    health_module: bool
    walk_module: bool
    create_dashboard: bool


class PawControlConfigFlowInput(TypedDict, total=False):
    """TypedDict for config flow user input."""

    dog_name: Required[str]
    dog_breed: NotRequired[str]
    dog_age: NotRequired[int]
    dog_weight: NotRequired[float]
    feeding_times: NotRequired[list[str]]
    walk_duration: NotRequired[int]
    vet_contact: NotRequired[str]
    gps_enable: NotRequired[bool]
    notifications_enabled: NotRequired[bool]
    health_module: NotRequired[bool]
    walk_module: NotRequired[bool]
    create_dashboard: NotRequired[bool]


class PawControlOptionsFlowInput(TypedDict, total=False):
    """TypedDict for options flow user input."""

    gps_enable: bool
    notifications_enabled: bool
    health_module: bool
    walk_module: bool
    create_dashboard: bool
