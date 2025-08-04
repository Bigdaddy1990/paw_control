import logging
import datetime
from typing import List, Dict, Optional
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity, EntityCategory
from homeassistant.components.binary_sensor import BinarySensorEntity
from .const import DOMAIN
from .utils import register_services

_LOGGER = logging.getLogger(__name__)

class ActivityLogger:
    def __init__(self):
        self._activity_log: List[Dict] = []

    def log_activity(self, activity_type: str, details: Dict):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": activity_type,
            "details": details
        }
        self._activity_log.append(entry)
        _LOGGER.info("Activity logged: %s", entry)

    def get_latest(self, activity_type: Optional[str] = None) -> Optional[Dict]:
        for entry in reversed(self._activity_log):
            if activity_type is None or entry["type"] == activity_type:
                return entry
        return None

    def get_all(self, activity_type: Optional[str] = None) -> List[Dict]:
        if activity_type is None:
            return list(self._activity_log)
        return [e for e in self._activity_log if e["type"] == activity_type]

def get_activity_logger(hass: HomeAssistant) -> ActivityLogger:
    if "activity_logger" not in hass.data[DOMAIN]:
        hass.data[DOMAIN]["activity_logger"] = ActivityLogger()
    return hass.data[DOMAIN]["activity_logger"]

class PawControlHealthSensor(Entity):
    def __init__(self, activity_logger, entry_id: str):
        self._activity_logger = activity_logger
        self._attr_name = "PawControl Gesundheitsstatus"
        self._attr_unique_id = f"{DOMAIN}_health_status_{entry_id}"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def state(self):
        latest = self._activity_logger.get_latest("health")
        return latest["details"].get("status", "unknown") if latest else "unknown"

    @property
    def extra_state_attributes(self):
        latest = self._activity_logger.get_latest("health")
        return latest or {}

class PawControlHealthAlertBinarySensor(BinarySensorEntity):
    def __init__(self, activity_logger, entry_id: str):
        self._activity_logger = activity_logger
        self._attr_name = "PawControl Health Alert"
        self._attr_unique_id = f"{DOMAIN}_health_alert_{entry_id}"

    @property
    def is_on(self):
        latest = self._activity_logger.get_latest("health")
        return latest and latest["details"].get("alert", False)

    @property
    def extra_state_attributes(self):
        latest = self._activity_logger.get_latest("health")
        return latest or {}

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
