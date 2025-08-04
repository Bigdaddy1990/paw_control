"""Walk automation helpers for Paw Control."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import Entity, EntityCategory

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class WalkAutomationSystem:
    """Simple in-memory log of walks."""

    def __init__(self) -> None:
        self._walk_log: list[dict[str, Any]] = []

    def log_walk(self, timestamp: str, details: dict[str, Any] | None = None) -> None:
        """Record a walk event."""
        entry = {"timestamp": timestamp, "details": details or {}}
        self._walk_log.append(entry)
        _LOGGER.info("Walk logged: %s", entry)

    def get_last_walk(self) -> dict[str, Any] | None:
        """Return the most recent walk entry."""
        if not self._walk_log:
            return None
        return self._walk_log[-1]

    def get_walks(self, since: datetime | None = None) -> list[dict[str, Any]]:
        """Return walks optionally filtered by timestamp."""
        if since is None:
            return list(self._walk_log)
        return [
            walk
            for walk in self._walk_log
            if datetime.fromisoformat(walk["timestamp"]) >= since
        ]


def get_walk_automation_system(hass: HomeAssistant) -> WalkAutomationSystem:
    """Get or create the walk automation system stored in hass.data."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if "walk_automation_system" not in domain_data:
        domain_data["walk_automation_system"] = WalkAutomationSystem()
    return domain_data["walk_automation_system"]


class PawControlLastWalkSensor(Entity):
    """Sensor exposing the last walk timestamp."""

    def __init__(self, walk_system: WalkAutomationSystem, entry_id: str) -> None:
        self._walk_system = walk_system
        self._attr_name = "PawControl Letzter Spaziergang"
        self._attr_unique_id = f"{DOMAIN}_last_walk_{entry_id}"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def state(self) -> str | None:
        last_walk = self._walk_system.get_last_walk()
        return last_walk["timestamp"] if last_walk else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        last_walk = self._walk_system.get_last_walk()
        return last_walk or {}


class PawControlLogWalkButton(ButtonEntity):
    """Button to manually log a walk."""

    def __init__(self, walk_system: WalkAutomationSystem, entry_id: str) -> None:
        self._walk_system = walk_system
        self._attr_name = "PawControl Walk Now"
        self._attr_unique_id = f"{DOMAIN}_log_walk_{entry_id}"

    async def async_press(self) -> None:
        self._walk_system.log_walk(datetime.now(UTC).isoformat())


async def async_setup_entry(hass: HomeAssistant, _entry: ConfigEntry) -> bool:
    """Set up the walk automation system from a config entry."""
    _LOGGER.info("Setting up PawControl Walk Automation system from config entry")
    get_walk_automation_system(hass)

    async def handle_log_walk(call: Any) -> None:
        system = get_walk_automation_system(hass)
        timestamp = call.data.get("timestamp", datetime.now(UTC).isoformat())
        details = call.data.get("details", {})
        system.log_walk(timestamp, details)

    hass.services.async_register(DOMAIN, "log_walk", handle_log_walk)

    async def handle_get_last_walk(_call: Any) -> None:
        system = get_walk_automation_system(hass)
        last_walk = system.get_last_walk()
        _LOGGER.info("Last walk: %s", last_walk)

    hass.services.async_register(DOMAIN, "get_last_walk", handle_get_last_walk)

    return True


async def async_unload_entry(_hass: HomeAssistant, _entry: ConfigEntry) -> bool:
    """Unload the walk automation system."""
    _LOGGER.info("Unloading PawControl Walk Automation system")
    return True

