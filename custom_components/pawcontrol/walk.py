"""Gassi-/Spaziergangsmodul für Paw Control."""

from datetime import UTC, datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_DOG_NAME
from .utils import call_service


async def setup_walk(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Initialisiert Gassi-Tracking, Counter, Sensoren und Helper."""
    dog = entry.data[CONF_DOG_NAME]

    # Sensor für letztes Gassi
    last_walk_id = f"sensor.{dog}_last_walk"
    hass.states.async_set(
        last_walk_id,
        datetime.now(UTC).isoformat(),
        {"friendly_name": f"{dog} Letzter Spaziergang"},
    )

    # Counter für Anzahl Spaziergänge
    walk_counter_id = f"counter.{dog}_walks"
    if not hass.states.get(walk_counter_id):
        await call_service(
            hass,
            "counter",
            "create",
            {
                "name": f"{dog} Spaziergänge",
                "entity_id": walk_counter_id,
                "initial": 0,
                "step": 1,
            },
        )

    # Helper für laufenden Status (input_boolean)
    walk_active_id = f"input_boolean.{dog}_walk_active"
    if not hass.states.get(walk_active_id):
        await call_service(
            hass,
            "input_boolean",
            "create",
            {"name": f"{dog} Gassi läuft", "entity_id": walk_active_id},
        )


async def teardown_walk(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Entfernt Gassi-Sensoren und Helper."""
    dog = entry.data[CONF_DOG_NAME]
    last_walk_id = f"sensor.{dog}_last_walk"
    walk_counter_id = f"counter.{dog}_walks"
    walk_active_id = f"input_boolean.{dog}_walk_active"

    hass.states.async_remove(last_walk_id)
    if hass.states.get(walk_counter_id):
        await call_service(hass, "counter", "reset", {"entity_id": walk_counter_id})
        await call_service(hass, "counter", "remove", {"entity_id": walk_counter_id})
    if hass.states.get(walk_active_id):
        await call_service(
            hass, "input_boolean", "remove", {"entity_id": walk_active_id}
        )


async def ensure_helpers(hass: HomeAssistant, opts: dict) -> None:
    """Stellt sicher, dass Gassi-Helper existieren."""
    dog = opts[CONF_DOG_NAME]
    walk_counter_id = f"counter.{dog}_walks"
    walk_active_id = f"input_boolean.{dog}_walk_active"

    if not hass.states.get(walk_counter_id):
        await call_service(
            hass,
            "counter",
            "create",
            {
                "name": f"{dog} Spaziergänge",
                "entity_id": walk_counter_id,
                "initial": 0,
                "step": 1,
            },
        )
    if not hass.states.get(walk_active_id):
        await call_service(
            hass,
            "input_boolean",
            "create",
            {"name": f"{dog} Gassi läuft", "entity_id": walk_active_id},
        )
