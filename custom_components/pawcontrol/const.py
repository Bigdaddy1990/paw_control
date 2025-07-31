"""Konstanten für Paw Control."""

DOMAIN = "pawcontrol"

# Konfigurations-Keys (ConfigFlow, Options, Helper etc.)
CONF_DOG_NAME = "dog_name"
CONF_DOG_BREED = "dog_breed"
CONF_DOG_AGE = "dog_age"
CONF_DOG_WEIGHT = "dog_weight"
CONF_FEEDING_TIMES = "feeding_times"
CONF_WALK_DURATION = "walk_duration"
CONF_VET_CONTACT = "vet_contact"
CONF_GPS_ENABLE = "gps_enable"
CONF_NOTIFICATIONS_ENABLED = "notifications_enabled"
CONF_HEALTH_MODULE = "health_module"
CONF_WALK_MODULE = "walk_module"
CONF_CREATE_DASHBOARD = "create_dashboard"

# Sensors, States, Helper
ATTR_LAST_FED = "last_fed"
ATTR_LAST_WALK = "last_walk"
ATTR_HEALTH_STATUS = "health_status"
ATTR_GPS_LOCATION = "gps_location"
ATTR_FEEDING_COUNTER = "feeding_counter"
ATTR_WALK_COUNTER = "walk_counter"
ATTR_PUSH_TARGET = "push_target"
ATTR_PERSON_ID = "person_id"
ATTR_ACTION = "action"
ATTR_TIMESTAMP = "timestamp"
ATTR_DEVICE_TRACKER = "device_tracker"
ATTR_MEDICATION = "medication"
ATTR_SYMPTOMS = "symptoms"
ATTR_WEIGHT_HISTORY = "weight_history"
ATTR_ACTIVITY_LOG = "activity_log"
ATTR_LAST_EVENT = "last_event"
ATTR_DASHBOARD_VIEW = "dashboard_view"
ATTR_EVENT_TYPE = "event_type"
ATTR_EVENT_DETAIL = "event_detail"

# Standardwerte
DEFAULT_FEEDING_TIMES = []
DEFAULT_WALK_DURATION = 30
DEFAULT_HEALTH_STATUS = "ok"
DEFAULT_GPS_LOCATION = "unknown"

# Weitere interne Konstanten (z. B. Entity-ID-Präfixe)
SENSOR_PREFIX = "sensor"
INPUT_BOOLEAN_PREFIX = "input_boolean"
INPUT_NUMBER_PREFIX = "input_number"
INPUT_TEXT_PREFIX = "input_text"
COUNTER_PREFIX = "counter"

# Beispiel-Service-Namen
SERVICE_FEED_DOG = "feed_dog"
SERVICE_START_WALK = "start_walk"
SERVICE_LOG_HEALTH = "log_health"
SERVICE_SEND_NOTIFICATION = "send_notification"
SERVICE_LOG_ACTIVITY = "log_activity"
SERVICE_SET_WEIGHT = "set_weight"

# Für die optionale Modularisierung: Alle Feature-Flags zentral gesammelt
ALL_MODULE_FLAGS = [
    CONF_GPS_ENABLE,
    CONF_NOTIFICATIONS_ENABLED,
    CONF_HEALTH_MODULE,
    CONF_WALK_MODULE,
    CONF_CREATE_DASHBOARD,
]
