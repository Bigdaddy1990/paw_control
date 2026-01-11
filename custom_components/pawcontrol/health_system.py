import datetime
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN
from .entities import PawControlHealthEntity
from .utils import register_services

_LOGGER = logging.getLogger(__name__)


class ActivityLogger:
    def __init__(self):
        self._activity_log: list[dict] = []

    def log_activity(self, activity_type: str, details: dict):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": activity_type,
            "details": details,
        }
        self._activity_log.append(entry)
        _LOGGER.info("Activity logged: %s", entry)

    def get_latest(self, activity_type: str | None = None) -> dict | None:
        for entry in reversed(self._activity_log):
            if activity_type is None or entry["type"] == activity_type:
                return entry
        return None

    def get_all(self, activity_type: str | None = None) -> list[dict]:
        if activity_type is None:
            return list(self._activity_log)
        return [e for e in self._activity_log if e["type"] == activity_type]


def get_activity_logger(hass: HomeAssistant) -> ActivityLogger:
    if "activity_logger" not in hass.data[DOMAIN]:
        hass.data[DOMAIN]["activity_logger"] = ActivityLogger()
    return hass.data[DOMAIN]["activity_logger"]


class PawControlHealthSensor(PawControlHealthEntity):
    def __init__(self, activity_logger, entry_id: str):
        super().__init__(
            activity_logger,
            entry_id,
            "PawControl Gesundheitsstatus",
            "health_status",
        )
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def state(self):
        latest = self._latest_health
        return latest["details"].get("status", "unknown") if latest else "unknown"


class PawControlHealthAlertBinarySensor(PawControlHealthEntity, BinarySensorEntity):
    def __init__(self, activity_logger, entry_id: str):
        super().__init__(
            activity_logger,
            entry_id,
            "PawControl Health Alert",
            "health_alert",
        )

    @property
    def is_on(self):
        latest = self._latest_health
        return bool(latest and latest["details"].get("alert", False))


async def async_setup_entry(hass: HomeAssistant, entry):
    _LOGGER.info("Setting up PawControl Health Logger from config entry")
    get_activity_logger(hass)

    async def handle_log_activity(call):
        logger = get_activity_logger(hass)
        activity_type = call.data.get("type", "unknown")
        details = call.data.get("details", {})
        logger.log_activity(activity_type, details)

    async def handle_get_latest_activity(call):
        logger = get_activity_logger(hass)
        activity_type = call.data.get("type")
        latest = logger.get_latest(activity_type)
        _LOGGER.info("Latest activity: %s", latest)

    register_services(
        hass,
        DOMAIN,
        {
            "log_activity": handle_log_activity,
            "get_latest_activity": handle_get_latest_activity,
        },
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry):
    _LOGGER.info("Unloading PawControl Health Logger")
    return True
