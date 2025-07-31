from __future__ import annotations

from homeassistant.const import Platform


DOMAIN = "paw_control"
NAME = "Paw Control"
VERSION = "1.0.0"

# Configuration keys
CONF_DOG_NAME = "dog_name"
CONF_DOG_BREED = "dog_breed"
CONF_DOG_AGE = "dog_age"
CONF_DOG_WEIGHT = "dog_weight"
CONF_GPS_PROVIDER = "gps_provider"
CONF_HEALTH_MONITORING = "health_monitoring"
CONF_AUTO_NOTIFICATIONS = "auto_notifications"
CONF_FEEDING_TIMES = "feeding_times"
CONF_WALK_DURATION = "walk_duration"
CONF_VET_CONTACT = "vet_contact"
CONF_PUSH_DEVICES = "push_devices"
CONF_PERSON_TRACKING = "person_tracking"
CONF_CREATE_DASHBOARD = "create_dashboard"
CONF_DOOR_SENSOR = "door_sensor"
CONF_RESET_TIME = "reset_time"
CONF_GPS_TRACKER = "gps_tracker"
CONF_GPS_ENABLE = "gps_enable"
CONF_GPS_SOURCE = "gps_source"
CONF_GPS_ENTITY = "gps_entity"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_GEOFENCE_RADIUS = "geofence_radius"
CONF_NOTIFICATIONS_ENABLED = "notifications_enabled"

# Default values
DEFAULT_DOG_NAME = "hund"
DEFAULT_CREATE_DASHBOARD = True
DEFAULT_PERSON_TRACKING = True
DEFAULT_RESET_TIME = "23:59:00"
DEFAULT_WALK_DURATION = 30
DEFAULT_FEEDING_TIMES = "07:00,12:00,18:00,15:00"
DEFAULT_UPDATE_INTERVAL = 30
DEFAULT_GEOFENCE_RADIUS = 100
DEFAULT_GPS_ACCURACY_THRESHOLD = 20.0

# Platforms
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.BUTTON]

# =========================
# ICONS - VOLLSTÄNDIGE SAMMLUNG
# =========================

ICONS = {
    # Basic activity icons
    "food": "mdi:food",
    "walk": "mdi:walk", 
    "play": "mdi:tennis",
    "training": "mdi:school",
    "sleep": "mdi:sleep",
    "poop": "mdi:toilet",
    "outside": "mdi:tree",
    
    # Health & care icons
    "health": "mdi:heart-pulse",
    "weight": "mdi:weight-kilogram",
    "temperature": "mdi:thermometer",
    "medication": "mdi:pill",
    "vet": "mdi:stethoscope",
    "vaccination": "mdi:needle",
    "grooming": "mdi:shower",
    
    # GPS & location icons
    "gps": "mdi:crosshairs-gps",
    "location": "mdi:map-marker",
    "route": "mdi:map-marker-path",
    "distance": "mdi:map-marker-distance",
    "speed": "mdi:speedometer",
    "signal": "mdi:signal",
    "battery": "mdi:battery",
    
    # Status & system icons
    "status": "mdi:information",
    "emergency": "mdi:alert",
    "visitor": "mdi:account-group",
    "attention": "mdi:bell-alert",
    "success": "mdi:check-circle",
    "warning": "mdi:alert-circle",
    "error": "mdi:close-circle",
    
    # Mood & behavior icons
    "happy": "mdi:emoticon-happy",
    "sad": "mdi:emoticon-sad", 
    "excited": "mdi:emoticon-excited",
    "sleepy": "mdi:emoticon-neutral",
    "sick": "mdi:emoticon-sick",
    "stressed": "mdi:emoticon-dead",
    
    # Time & scheduling icons
    "morning": "mdi:weather-sunrise",
    "lunch": "mdi:weather-sunny",
    "evening": "mdi:weather-sunset",
    "night": "mdi:weather-night",
    "calendar": "mdi:calendar",
    "clock": "mdi:clock",
    
    # Dog-specific icons
    "dog": "mdi:dog",
    "bone": "mdi:bone",
    "collar": "mdi:necklace",
    "leash": "mdi:link",
    "bowl": "mdi:bowl",
    "toy": "mdi:tennis",
    "notes": "mdi:note-text",
    "mood": "mdi:emoticon-happy",
    "bell": "mdi:bell",
}

# Legacy icon constants (für Rückwärtskompatibilität)
ICON_DOG = ICONS["dog"]
ICON_FOOD = ICONS["food"] 
ICON_WALK = ICONS["walk"]
ICON_PLAY = ICONS["play"]
ICON_TRAINING = ICONS["training"]
ICON_HEALTH = ICONS["health"]
ICON_WEIGHT = ICONS["weight"]
ICON_MOOD_HAPPY = ICONS["happy"]
ICON_STATUS = ICONS["status"]
ICON_BELL = ICONS["attention"]
ICON_SLEEP = ICONS["sleep"]

# =========================
# FEEDING SYSTEM - ERWEITERTE KONFIGURATION
# =========================

FEEDING_TYPES = ["morning", "lunch", "evening", "snack"]

MEAL_TYPES = {
    "morning": "Frühstück",
    "lunch": "Mittagessen", 
    "evening": "Abendessen",
    "snack": "Leckerli"
}

MEAL_ICONS = {
    "morning": ICONS["morning"],
    "lunch": ICONS["lunch"],
    "evening": ICONS["evening"],
    "snack": ICONS["bone"]
}

PORTION_SIZES = {
    "small": {"name": "Klein", "grams": 50, "calories": 150},
    "normal": {"name": "Normal", "grams": 100, "calories": 300},
    "large": {"name": "Groß", "grams": 150, "calories": 450},
    "extra_large": {"name": "Extra Groß", "grams": 200, "calories": 600}
}

FOOD_TYPES = {
    "dry_food": {"name": "Trockenfutter", "calories_per_gram": 3.0},
    "wet_food": {"name": "Nassfutter", "calories_per_gram": 1.2},
    "treats": {"name": "Leckerlis", "calories_per_gram": 4.5},
    "raw_food": {"name": "Rohfutter", "calories_per_gram": 2.0},
    "special_diet": {"name": "Spezialdiät", "calories_per_gram": 2.5}
}

# Default feeding times as dict
DEFAULT_FEEDING_TIMES_DICT = {
    "morning": "07:00:00",
    "lunch": "12:00:00",
    "evening": "18:00:00",
    "snack": "15:00:00"
}

# =========================
# ACTIVITY SYSTEM - VOLLSTÄNDIGE DEFINITIONEN
# =========================

ACTIVITY_TYPES = {
    "walk": {"name": "Gassi gehen", "icon": ICONS["walk"], "calories_per_minute": 5},
    "run": {"name": "Laufen", "icon": "mdi:run", "calories_per_minute": 12},
    "play": {"name": "Spielen", "icon": ICONS["play"], "calories_per_minute": 8},
    "training": {"name": "Training", "icon": ICONS["training"], "calories_per_minute": 6},
    "swimming": {"name": "Schwimmen", "icon": "mdi:pool", "calories_per_minute": 15},
    "hiking": {"name": "Wandern", "icon": "mdi:hiking", "calories_per_minute": 7},
    "outside": "Draußen",
    "other": "Sonstiges",
    "poop": "Geschäft gemacht",
    "vet": "Tierarzt",
    "grooming": "Pflege"
}

ACTIVITY_INTENSITY = {
    "low": {"name": "Niedrig", "multiplier": 0.7},
    "medium": {"name": "Mittel", "multiplier": 1.0},
    "high": {"name": "Hoch", "multiplier": 1.4},
    "extreme": {"name": "Extrem", "multiplier": 1.8}
}

PLAY_TYPES = {
    "fetch": {"name": "Apportieren", "icon": "mdi:tennis"},
    "tug_of_war": {"name": "Tauziehen", "icon": "mdi:rope"},
    "chase": {"name": "Fangspiel", "icon": "mdi:run-fast"},
    "puzzle": {"name": "Denkspiel", "icon": "mdi:puzzle"},
    "social": {"name": "Soziales Spiel", "icon": "mdi:dog"},
    "water": {"name": "Wasserspiel", "icon": "mdi:pool"}
}

# Activity level definitions
ACTIVITY_LEVELS = {
    "very_low": {"daily_walk_min": 15, "daily_play_min": 5},
    "low": {"daily_walk_min": 30, "daily_play_min": 10},
    "normal": {"daily_walk_min": 60, "daily_play_min": 20},
    "high": {"daily_walk_min": 90, "daily_play_min": 30},
    "very_high": {"daily_walk_min": 120, "daily_play_min": 45}
}

# =========================
# HEALTH SYSTEM - UMFASSENDE KONFIGURATION
# =========================

HEALTH_STATUS_OPTIONS = [
    "Ausgezeichnet", "Sehr gut", "Gut", "Normal", 
    "Leicht unwohl", "Unwohl", "Krank", "Sehr krank", "Notfall"
]

MOOD_OPTIONS = [
    "😄 Sehr glücklich", "😊 Glücklich", "🙂 Zufrieden", "😐 Neutral",
    "😴 Müde", "😟 Traurig", "😠 Ärgerlich", "😰 Ängstlich", "🤒 Unwohl"
]

ENERGY_LEVELS = [
    "Sehr müde", "Müde", "Ruhig", "Normal", 
    "Lebhaft", "Energiegeladen", "Hyperaktiv"
]

APPETITE_LEVELS = [
    "Kein Appetit", "Sehr wenig", "Wenig Appetit", "Normal",
    "Guter Appetit", "Sehr hungrig", "Gierig"
]

SYMPTOMS = {
    "digestive": ["Erbrechen", "Durchfall", "Verstopfung", "Blähungen"],
    "respiratory": ["Husten", "Niesen", "Atemnot", "Röcheln"],
    "behavioral": ["Lethargie", "Unruhe", "Aggression", "Verstecken"],
    "physical": ["Hinken", "Zittern", "Kratzen", "Kopfschütteln"],
    "eating": ["Futterverweigerung", "Übermäßiges Trinken", "Sabbern"]
}

VACCINATION_TYPES = {
    "rabies": {"name": "Tollwut", "interval_months": 12, "required": True},
    "distemper": {"name": "Staupe", "interval_months": 12, "required": True},
    "hepatitis": {"name": "Hepatitis", "interval_months": 12, "required": True},
    "parvovirus": {"name": "Parvovirose", "interval_months": 12, "required": True},
    "parainfluenza": {"name": "Parainfluenza", "interval_months": 12, "required": True},
    "kennel_cough": {"name": "Zwingerhusten", "interval_months": 12, "required": False},
    "lyme": {"name": "Borreliose", "interval_months": 12, "required": False}
}

# Health monitoring thresholds
HEALTH_THRESHOLDS = {
    "max_hours_without_food": 12,
    "max_hours_without_outside": 8,
    "max_days_without_poop": 2,
    "min_daily_activities": 2,
}

# Health monitoring ranges
HEALTH_RANGES = {
    "temperature": {
        "normal_min": 38.0,
        "normal_max": 39.5,
        "critical_min": 37.0,
        "critical_max": 41.0
    },
    "heart_rate": {
        "normal_min": 70,
        "normal_max": 120,
        "critical_min": 50,
        "critical_max": 180
    },
    "weight_change": {
        "warning_threshold": 0.1,  # 10% change
        "critical_threshold": 0.2   # 20% change
    }
}

# Vaccination status options
VACCINATION_STATUS_OPTIONS = [
    "Vollständig geimpft", "Grundimmunisierung abgeschlossen", "Grundimmunisierung läuft", 
    "Auffrischung fällig", "Überfällig", "Noch nicht begonnen"
]

SPECIFIC_VACCINATION_STATUS_OPTIONS = [
    "Aktuell", "Auffrischung in 6 Monaten", "Auffrischung in 3 Monaten", 
    "Auffrischung in 1 Monat", "Überfällig", "Nie geimpft"
]

# Core vs. optional vaccines
CORE_VACCINES = ["rabies", "distemper", "hepatitis", "parvovirus"]
OPTIONAL_VACCINES = ["parainfluenza", "leptospirosis", "bordetella"]

# Impfintervalle in Monaten
VACCINATION_INTERVALS = {
    "rabies": 36,           # 3 Jahre
    "distemper": 36,        # 3 Jahre
    "hepatitis": 36,        # 3 Jahre
    "parvovirus": 36,       # 3 Jahre
    "parainfluenza": 12,    # 1 Jahr
    "leptospirosis": 12,    # 1 Jahr
    "bordetella": 12        # 1 Jahr
}

VACCINATION_NAMES = {
    "rabies": "Tollwut",
    "distemper": "Staupe",
    "hepatitis": "Hepatitis", 
    "parvovirus": "Parvovirose",
    "parainfluenza": "Parainfluenza",
    "leptospirosis": "Leptospirose",
    "bordetella": "Zwingerhusten"
}

# =========================
# GPS SYSTEM - VOLLSTÄNDIGE KONFIGURATION
# =========================

GPS_PROVIDERS = {
    "tractive": {
        "name": "Tractive GPS",
        "api_endpoint": "https://graph.tractive.com/3/",
        "update_interval": 30,
        "accuracy_threshold": 10,
        "api_url": "https://graph.tractive.com/3/",
        "requires_auth": True,
    },
    "fressnapf": {
        "name": "Fressnapf GPS",
        "api_endpoint": "https://api.fressnapf.com/v1/",
        "update_interval": 60,
        "accuracy_threshold": 15
    },
    "smartphone": {
        "name": "Smartphone GPS",
        "api_endpoint": None,
        "update_interval": 15,
        "accuracy_threshold": 5,
        "webhook_enabled": True,
    },
    "manual": {
        "name": "Manuelle Eingabe",
        "api_endpoint": None,
        "update_interval": 0,
        "accuracy_threshold": 50
    }
}

GPS_TRACKING_MODES = {
    "continuous": {"name": "Kontinuierlich", "battery_usage": "high"},
    "walk_only": {"name": "Nur bei Spaziergängen", "battery_usage": "medium"}, 
    "scheduled": {"name": "Geplant", "battery_usage": "low"},
    "emergency_only": {"name": "Nur Notfall", "battery_usage": "minimal"}
}

GEOFENCE_TYPES = {
    "home": {"name": "Zuhause", "radius_default": 50, "color": "green"},
    "park": {"name": "Park", "radius_default": 100, "color": "blue"},
    "vet": {"name": "Tierarzt", "radius_default": 30, "color": "red"},
    "forbidden": {"name": "Verboten", "radius_default": 25, "color": "red"},
    "safe_zone": {"name": "Sichere Zone", "radius_default": 75, "color": "yellow"}
}

# Standard GPS Koordinaten
DEFAULT_GPS_COORDINATES = {
    "home": {"lat": 52.233333, "lon": 8.966667, "name": "Detmold, Deutschland"},
    "emergency": {"lat": 52.233333, "lon": 8.966667, "name": "Standard Notfall-Position"}
}

# GPS and tracking constants
GPS_CONFIG = {
    "default_accuracy_threshold": 10,  # meters
    "geofence_radius": 100,  # meters
    "tracking_interval": 30,  # seconds
    "max_route_points": 1000,
    "auto_walk_detection_threshold": 50,  # meters
    "walk_end_timeout": 300,  # seconds
}

# GPS limits
MIN_GPS_ACCURACY = 100.0  # meters
MAX_GPS_AGE = 300  # seconds
GEOFENCE_MIN_RADIUS = 10
GEOFENCE_MAX_RADIUS = 1000

# Walk detection thresholds  
WALK_START_DISTANCE_THRESHOLD = 50  # meters
WALK_MIN_DURATION = 5  # minutes
WALK_MAX_SPEED = 25  # km/h

# =========================
# SERVICE DEFINITIONS - VOLLSTÄNDIGES ECOSYSTEM
# =========================

SERVICES = {
    # Feeding Services
    "feed_dog": {
        "name": "Hund füttern",
        "description": "Fütterung des Hundes dokumentieren",
        "icon": ICONS["food"],
        "category": "feeding"
    },
    "schedule_feeding": {
        "name": "Fütterung planen",
        "description": "Fütterungszeiten festlegen",
        "icon": ICONS["calendar"],
        "category": "feeding"
    },
    
    # Activity Services
    "start_walk": {
        "name": "Spaziergang starten",
        "description": "Spaziergang beginnen und tracken",
        "icon": ICONS["walk"],
        "category": "activity"
    },
    "end_walk": {
        "name": "Spaziergang beenden",
        "description": "Spaziergang beenden und speichern",
        "icon": ICONS["walk"],
        "category": "activity"
    },
    "start_playtime": {
        "name": "Spielzeit starten",
        "description": "Spielsession beginnen",
        "icon": ICONS["play"],
        "category": "activity"
    },
    "end_playtime": {
        "name": "Spielzeit beenden",
        "description": "Spielsession beenden",
        "icon": ICONS["play"],
        "category": "activity"
    },
    "start_training": {
        "name": "Training starten",
        "description": "Trainingseinheit beginnen",
        "icon": ICONS["training"],
        "category": "activity"
    },
    "end_training": {
        "name": "Training beenden", 
        "description": "Trainingseinheit beenden",
        "icon": ICONS["training"],
        "category": "activity"
    },
    
    # Health Services
    "log_health_data": {
        "name": "Gesundheitsdaten erfassen",
        "description": "Gesundheitsinformationen dokumentieren",
        "icon": ICONS["health"],
        "category": "health"
    },
    "give_medication": {
        "name": "Medikament geben",
        "description": "Medikamentengabe dokumentieren",
        "icon": ICONS["medication"],
        "category": "health"
    },
    "schedule_vet_visit": {
        "name": "Tierarzttermin planen",
        "description": "Tierarztbesuch terminieren",
        "icon": ICONS["vet"],
        "category": "health"
    },
    "add_vaccination": {
        "name": "Impfung hinzufügen",
        "description": "Impfung dokumentieren",
        "icon": ICONS["vaccination"],
        "category": "health"
    },
    "health_check": {
        "name": "Gesundheitscheck",
        "description": "Allgemeine Gesundheitsprüfung",
        "icon": ICONS["health"],
        "category": "health"
    },
    
    # GPS Services
    "update_gps_simple": {
        "name": "GPS Position aktualisieren",
        "description": "Aktuelle GPS Position erfassen",
        "icon": ICONS["gps"],
        "category": "gps"
    },
    "start_walk_tracking": {
        "name": "GPS Tracking starten",
        "description": "GPS-basiertes Tracking beginnen",
        "icon": ICONS["gps"],
        "category": "gps"
    },
    "end_walk_tracking": {
        "name": "GPS Tracking beenden",
        "description": "GPS-basiertes Tracking beenden",
        "icon": ICONS["gps"],
        "category": "gps"
    },
    "setup_automatic_gps": {
        "name": "Automatisches GPS einrichten",
        "description": "GPS Automatisierung konfigurieren",
        "icon": ICONS["gps"],
        "category": "gps"
    },
    "set_geofence": {
        "name": "Geofence definieren",
        "description": "Geografische Bereiche festlegen",
        "icon": ICONS["location"],
        "category": "gps"
    },
    "find_lost_dog": {
        "name": "Verlorenen Hund suchen",
        "description": "Notfall-GPS-Ortung",
        "icon": ICONS["emergency"],
        "category": "gps"
    },
    "create_webhook_gps": {
        "name": "GPS-Webhook erstellen",
        "description": "Webhook für GPS-Updates",
        "icon": ICONS["gps"],
        "category": "gps"
    },
    "analyze_gps_data": {
        "name": "GPS-Daten analysieren",
        "description": "GPS-Aktivitätsmuster auswerten",
        "icon": ICONS["gps"],
        "category": "gps"
    },
    
    # System Services
    "activate_emergency_mode": {
        "name": "Notfallmodus aktivieren",
        "description": "Notfallprotokoll starten",
        "icon": ICONS["emergency"],
        "category": "system"
    },
    "toggle_visitor_mode": {
        "name": "Besuchermodus umschalten",
        "description": "Besuchermodus aktivieren/deaktivieren",
        "icon": ICONS["visitor"],
        "category": "system"
    },
    "daily_reset": {
        "name": "Tägliche Zurücksetzung",
        "description": "Tägliche Daten zurücksetzen",
        "icon": "mdi:refresh",
        "category": "system"
    },
    "generate_report": {
        "name": "Bericht generieren",
        "description": "Aktivitätsbericht erstellen",
        "icon": "mdi:file-document",
        "category": "system"
    },
    "backup_data": {
        "name": "Daten sichern",
        "description": "Datensicherung erstellen",
        "icon": "mdi:backup-restore",
        "category": "system"
    },
    
    # Integration Services
    "sync_fressnapf_data": {
        "name": "Fressnapf Daten synchronisieren",
        "description": "Mit Fressnapf Tracker synchronisieren",
        "icon": "mdi:sync",
        "category": "integration"
    },
    "setup_fressnapf_tracker": {
        "name": "Fressnapf Tracker einrichten",
        "description": "Fressnapf GPS-Tracker konfigurieren",
        "icon": "mdi:cog",
        "category": "integration"
    },
    "connect_tractive": {
        "name": "Tractive verbinden",
        "description": "Tractive GPS-Tracker verbinden",
        "icon": "mdi:link",
        "category": "integration"
    },
    
    # Automation Services
    "setup_automation": {
        "name": "Automatisierung einrichten",
        "description": "Automatische Abläufe konfigurieren",
        "icon": "mdi:robot",
        "category": "automation"
    },
    "schedule_reminder": {
        "name": "Erinnerung planen",
        "description": "Automatische Erinnerungen einrichten",
        "icon": ICONS["attention"],
        "category": "automation"
    }
}

# Service-Kategorien für UI-Organisation
SERVICE_CATEGORIES = {
    "feeding": {"name": "Fütterung", "icon": ICONS["food"], "color": "green"},
    "activity": {"name": "Aktivität", "icon": ICONS["walk"], "color": "blue"},
    "health": {"name": "Gesundheit", "icon": ICONS["health"], "color": "red"},
    "gps": {"name": "GPS", "icon": ICONS["gps"], "color": "purple"},
    "system": {"name": "System", "icon": ICONS["status"], "color": "orange"},
    "integration": {"name": "Integration", "icon": "mdi:puzzle", "color": "teal"},
    "automation": {"name": "Automatisierung", "icon": "mdi:robot", "color": "indigo"}
}

# Service parameter keys - COMPLETE LIST
SERVICE_ENTITY_ID = "entity_id"
SERVICE_FOOD_TYPE = "food_type"
SERVICE_FOOD_AMOUNT = "food_amount"
SERVICE_AMOUNT = "amount"
SERVICE_NOTES = "notes"
SERVICE_WALK_TYPE = "walk_type"
SERVICE_LOCATION = "location"
SERVICE_RATING = "rating"
SERVICE_DURATION = "duration"
SERVICE_WEIGHT = "weight"
SERVICE_TEMPERATURE = "temperature"
SERVICE_ENERGY_LEVEL = "energy_level"
SERVICE_SYMPTOMS = "symptoms"
SERVICE_MOOD = "mood"
SERVICE_REASON = "reason"
SERVICE_TRAINING_TYPE = "training_type"
SERVICE_DURATION_PLANNED = "duration_planned"
SERVICE_SUCCESS_RATING = "success_rating"
SERVICE_LEARNED_COMMANDS = "learned_commands"
SERVICE_MEDICATION_NAME = "medication_name"
SERVICE_MEDICATION_AMOUNT = "medication_amount"
SERVICE_MEDICATION_UNIT = "medication_unit"
SERVICE_DOSAGE = "dosage"
SERVICE_NEXT_DOSE = "next_dose"
SERVICE_APPOINTMENT_DATE = "appointment_date"
SERVICE_VISIT_TYPE = "visit_type"
SERVICE_VET_NAME = "vet_name"
SERVICE_VET_DATE = "vet_date"
SERVICE_VET_REASON = "vet_reason"
SERVICE_PLAY_TYPE = "play_type"
SERVICE_FUN_RATING = "fun_rating"
SERVICE_ENERGY_AFTERWARDS = "energy_afterwards"
SERVICE_CONFIRM_RESET = "confirm_reset"
SERVICE_BACKUP_DATA = "backup_data"

# Service names
SERVICE_TRIGGER_FEEDING_REMINDER = "trigger_feeding_reminder"
SERVICE_DAILY_RESET = "daily_reset"
SERVICE_SEND_NOTIFICATION = "send_notification"
SERVICE_SET_VISITOR_MODE = "set_visitor_mode"
SERVICE_LOG_ACTIVITY = "log_activity"
SERVICE_ADD_DOG = "add_dog"
SERVICE_TEST_NOTIFICATION = "test_notification"
SERVICE_EMERGENCY_CONTACT = "emergency_contact"
SERVICE_HEALTH_CHECK = "health_check"
# =========================
# SERVICE PARAMETER KEYS - COMPLETE LIST (für __init__.py)
# =========================

# Core service parameters
SERVICE_ENTITY_ID = "entity_id"
SERVICE_FOOD_TYPE = "food_type"
SERVICE_FOOD_AMOUNT = "food_amount"
SERVICE_AMOUNT = "amount"
SERVICE_NOTES = "notes"
SERVICE_WALK_TYPE = "walk_type"
SERVICE_LOCATION = "location"
SERVICE_RATING = "rating"
SERVICE_DURATION = "duration"
SERVICE_WEIGHT = "weight"
SERVICE_TEMPERATURE = "temperature"
SERVICE_ENERGY_LEVEL = "energy_level"
SERVICE_SYMPTOMS = "symptoms"
SERVICE_MOOD = "mood"
SERVICE_REASON = "reason"
SERVICE_TRAINING_TYPE = "training_type"
SERVICE_DURATION_PLANNED = "duration_planned"
SERVICE_SUCCESS_RATING = "success_rating"
SERVICE_LEARNED_COMMANDS = "learned_commands"
SERVICE_MEDICATION_NAME = "medication_name"
SERVICE_MEDICATION_AMOUNT = "medication_amount"
SERVICE_MEDICATION_UNIT = "medication_unit"
SERVICE_DOSAGE = "dosage"
SERVICE_NEXT_DOSE = "next_dose"
SERVICE_APPOINTMENT_DATE = "appointment_date"
SERVICE_VISIT_TYPE = "visit_type"
SERVICE_VET_NAME = "vet_name"
SERVICE_VET_DATE = "vet_date"
SERVICE_VET_REASON = "vet_reason"
SERVICE_PLAY_TYPE = "play_type"
SERVICE_FUN_RATING = "fun_rating"
SERVICE_ENERGY_AFTERWARDS = "energy_afterwards"
SERVICE_CONFIRM_RESET = "confirm_reset"
SERVICE_BACKUP_DATA = "backup_data"

# Service names (für Service-Registrierung)
SERVICE_START_WALK = "start_walk"
SERVICE_STOP_WALK = "stop_walk"
SERVICE_FEED_DOG = "feed_dog"
SERVICE_UPDATE_WEIGHT = "update_weight"
SERVICE_UPDATE_GPS_POSITION = "update_gps_position"
SERVICE_SET_MEDICATION = "set_medication"
SERVICE_SET_VET_APPOINTMENT = "set_vet_appointment"
SERVICE_CREATE_BACKUP = "create_backup"
SERVICE_RESTORE_BACKUP = "restore_backup"

# =========================
# ENTITY DEFINITIONS - 143 VOLLSTÄNDIGE ENTITIES
# =========================

ENTITIES = {
    "input_boolean": {
        # Feeding entities
        "feeding_morning": {"name": "Frühstück", "icon": ICONS["morning"]},
        "feeding_lunch": {"name": "Mittagessen", "icon": ICONS["lunch"]},
        "feeding_evening": {"name": "Abendessen", "icon": ICONS["evening"]},
        "feeding_snack": {"name": "Leckerli", "icon": ICONS["bone"]},
        
        # Activity entities
        "outside": {"name": "War draußen", "icon": ICONS["outside"]},
        "was_dog": {"name": "War es der Hund?", "icon": ICONS["dog"]},
        "poop_done": {"name": "Geschäft gemacht", "icon": ICONS["poop"]},
        "walked_today": {"name": "Heute spaziert", "icon": ICONS["walk"]},
        "played_today": {"name": "Heute gespielt", "icon": ICONS["play"]},
        
        # GPS tracking entities
        "walk_in_progress": {"name": "Spaziergang aktiv", "icon": ICONS["walk"]},
        "auto_walk_detection": {"name": "Auto-Spaziergang Erkennung", "icon": "mdi:radar"},
        "gps_tracking_enabled": {"name": "GPS-Tracking aktiviert", "icon": ICONS["gps"]},
        
        # Status entities
        "visitor_mode_input": {"name": "Besuchsmodus", "icon": ICONS["visitor"]},
        "emergency_mode": {"name": "Notfallmodus", "icon": ICONS["emergency"]},
        "medication_given": {"name": "Medikament gegeben", "icon": ICONS["medication"]},
        "feeling_well": {"name": "Fühlt sich wohl", "icon": ICONS["health"]},
        "appetite_normal": {"name": "Normaler Appetit", "icon": ICONS["food"]},
        "energy_normal": {"name": "Normale Energie", "icon": "mdi:flash"},
        "auto_reminders": {"name": "Automatische Erinnerungen", "icon": ICONS["attention"]},
        "tracking_enabled": {"name": "Tracking aktiviert", "icon": ICONS["location"]},
        "weather_alerts": {"name": "Wetter-Warnungen", "icon": "mdi:weather-partly-cloudy"},
        "needs_grooming": {"name": "Braucht Fellpflege", "icon": ICONS["grooming"]},
        "training_session": {"name": "Training läuft", "icon": ICONS["training"]},
        "needs_attention": {"name": "Braucht Aufmerksamkeit", "icon": ICONS["attention"]},
        "socialized_today": {"name": "Heute sozialisiert", "icon": "mdi:account-group"},
        "is_walking": {"name": "Spaziergang aktiv"},
        "needs_feeding": {"name": "Fütterung erforderlich"},
        "needs_medication": {"name": "Medikament erforderlich"},
        "gps_tracking_active": {"name": "GPS-Tracking aktiv"},
        "inside_geofence": {"name": "In Sicherheitszone"},
        "health_alert": {"name": "Gesundheitsalarm"},
        "vet_visit_due": {"name": "Tierarztbesuch fällig"}
    },
    
    "input_number": {
        # GPS & Walk metrics
        "current_walk_distance": {"name": "Aktuelle Spaziergang Distanz", "min": 0, "max": 20, "step": 0.01, "unit": "km", "icon": ICONS["distance"]},
        "current_walk_duration": {"name": "Aktuelle Spaziergang Dauer", "min": 0, "max": 300, "step": 1, "unit": "min", "icon": ICONS["clock"]},
        "current_walk_speed": {"name": "Aktuelle Geschwindigkeit", "min": 0, "max": 15, "step": 0.1, "unit": "km/h", "icon": ICONS["speed"]},
        "current_walk_calories": {"name": "Aktuelle Spaziergang Kalorien", "min": 0, "max": 1000, "step": 1, "unit": "kcal", "icon": "mdi:fire"},
        "walk_distance_today": {"name": "Heutige Spaziergang Distanz", "min": 0, "max": 30, "step": 0.1, "unit": "km", "icon": ICONS["distance"]},
        "walk_distance_weekly": {"name": "Wöchentliche Gehstrecke", "min": 0, "max": 200, "step": 0.1, "unit": "km", "icon": ICONS["distance"]},
        "walk_distance_monthly": {"name": "Monatliche Gehstrecke", "min": 0, "max": 900, "step": 0.1, "unit": "km", "icon": ICONS["distance"]},
        "max_distance_from_home": {"name": "Max. Entfernung von Zuhause", "min": 0, "max": 10, "step": 0.1, "initial": 5, "unit": "km", "icon": ICONS["distance"]},
        "average_walk_speed": {"name": "Durchschnittliche Gehgeschwindigkeit", "min": 0, "max": 10, "step": 0.1, "unit": "km/h", "icon": ICONS["speed"]},
        "walks_count_today": {"name": "Spaziergänge heute", "min": 0, "max": 10, "step": 1, "icon": ICONS["walk"]},
        "walks_count_weekly": {"name": "Spaziergänge diese Woche", "min": 0, "max": 50, "step": 1, "icon": ICONS["walk"]},
        "calories_burned_walk": {"name": "Verbrannte Kalorien Spaziergang", "min": 0, "max": 2000, "step": 10, "unit": "kcal", "icon": "mdi:fire"},
        "steps_count_estimated": {"name": "Geschätzte Schritte", "min": 0, "max": 50000, "step": 100, "unit": "Schritte", "icon": "mdi:shoe-print"},
        
        # GPS technical metrics
        "gps_battery_level": {"name": "GPS-Tracker Akku", "min": 0, "max": 100, "step": 1, "initial": 100, "unit": "%", "icon": ICONS["battery"]},
        "gps_signal_strength": {"name": "GPS-Signalstärke", "min": 0, "max": 100, "step": 1, "initial": 100, "unit": "%", "icon": ICONS["signal"]},
        "current_latitude": {"name": "Aktuelle Latitude", "min": -90, "max": 90, "step": 0.000001, "initial": 52.233333, "icon": ICONS["gps"]},
        "current_longitude": {"name": "Aktuelle Longitude", "min": -180, "max": 180, "step": 0.000001, "initial": 8.966667, "icon": ICONS["gps"]},
        "home_latitude": {"name": "Zuhause Latitude", "min": -90, "max": 90, "step": 0.000001, "initial": 52.233333, "icon": "mdi:home"},
        "home_longitude": {"name": "Zuhause Longitude", "min": -180, "max": 180, "step": 0.000001, "initial": 8.966667, "icon": "mdi:home"},
        
        # Health metrics
        "weight": {"name": "Gewicht", "min": 0.5, "max": 100.0, "step": 0.1, "initial": 15, "unit": "kg", "icon": ICONS["weight"]},
        "target_weight": {"name": "Zielgewicht", "min": 0.5, "max": 100.0, "step": 0.1, "initial": 15, "unit": "kg", "icon": ICONS["weight"]},
        "height": {"name": "Schulterhöhe", "min": 10, "max": 100, "step": 1, "initial": 50, "unit": "cm", "icon": "mdi:ruler"},
        "length": {"name": "Körperlänge", "min": 20, "max": 150, "step": 1, "initial": 60, "unit": "cm", "icon": "mdi:ruler"},
        "temperature": {"name": "Körpertemperatur", "min": 35, "max": 42, "step": 0.1, "initial": 38.5, "unit": "°C", "icon": ICONS["temperature"]},
        "heart_rate": {"name": "Herzfrequenz", "min": 60, "max": 200, "step": 1, "initial": 100, "unit": "bpm", "icon": ICONS["health"]},
        "health_score": {"name": "Gesundheits Score", "min": 0, "max": 100, "step": 1, "initial": 85, "unit": "%", "icon": ICONS["health"]},
        "happiness_score": {"name": "Glücks Score", "min": 0, "max": 10, "step": 1, "initial": 8, "icon": ICONS["happy"]},
        "energy_level": {"name": "Energie Level", "min": 0, "max": 10, "step": 1, "initial": 8, "icon": "mdi:flash"},
        "appetite_score": {"name": "Appetit Score", "min": 0, "max": 10, "step": 1, "initial": 8, "icon": ICONS["food"]},        
        "stress_level": {"name": "Stresslevel", "min": 0, "max": 10, "step": 1, "initial": 2, "icon": "mdi:head-alert"},
        "socialization_score": {"name": "Sozialisations-Score", "min": 0, "max": 10, "step": 1, "initial": 7, "icon": "mdi:account-group"},
        
        # Activity metrics
        "daily_walk_duration": {"name": "Tägliche Spaziergang Dauer", "min": 0, "max": 300, "step": 1, "unit": "min", "icon": ICONS["walk"]},
        "daily_play_time": {"name": "Tägliche Spielzeit", "min": 0, "max": 180, "step": 1, "unit": "min", "icon": ICONS["play"]},
        "daily_play_duration": {"name": "Tägliche Spielzeit", "min": 0, "max": 180, "step": 1, "unit": "min", "icon": ICONS["play"]},
        "training_duration": {"name": "Trainingsdauer", "min": 0, "max": 120, "step": 1, "unit": "min", "icon": ICONS["training"]},
        "daily_training_duration": {"name": "Tägliche Trainingsdauer", "min": 0, "max": 120, "step": 1, "unit": "min", "icon": ICONS["training"]},
        "daily_food_amount": {"name": "Tägliche Futtermenge", "min": 0, "max": 2000, "step": 10, "initial": 400, "unit": "g", "icon": ICONS["food"]},
        "treat_amount": {"name": "Leckerli Menge", "min": 0, "max": 200, "step": 5, "initial": 20, "unit": "g", "icon": ICONS["bone"]},
        "water_intake": {"name": "Wasseraufnahme", "min": 0, "max": 3000, "step": 50, "initial": 500, "unit": "ml", "icon": "mdi:cup-water"},
        "daily_water_amount": {"name": "Tägliche Wassermenge", "min": 0, "max": 3000, "step": 50, "initial": 500, "unit": "ml", "icon": "mdi:cup-water"},
        "sleep_hours": {"name": "Schlafstunden", "min": 8, "max": 20, "step": 0.5, "initial": 12, "unit": "h", "icon": ICONS["sleep"]},
        "calories_burned_today": {"name": "Verbrannte Kalorien heute", "min": 0, "max": 5000, "step": 1, "unit": "kcal"},
        
        # Age/medication
        "age_years": {"name": "Alter (Jahre)", "min": 0, "max": 20, "step": 0.1, "initial": 3, "unit": "Jahre", "icon": "mdi:cake-variant"},
        "age_months": {"name": "Alter (Monate)", "min": 0, "max": 240, "step": 1, "initial": 36, "unit": "Monate", "icon": "mdi:cake-variant"},
        "expected_lifespan": {"name": "Erwartete Lebenszeit", "min": 8, "max": 20, "step": 1, "initial": 13, "unit": "Jahre", "icon": "mdi:heart"},
        "medication_dosage": {"name": "Medikament Dosis", "min": 0, "max": 500, "step": 0.5, "initial": 5, "unit": "mg", "icon": ICONS["medication"]},
        "days_since_vet": {"name": "Tage seit Tierarzt", "min": 0, "max": 1000, "step": 1, "icon": ICONS["vet"]},
        "days_since_grooming": {"name": "Tage seit Fellpflege", "min": 0, "max": 365, "step": 1, "icon": ICONS["grooming"]},
        "feeding_streak": {"name": "Fütterungs-Serie", "min": 0, "max": 365, "step": 1, "icon": ICONS["food"]},
        "walk_streak": {"name": "Spaziergang-Serie", "min": 0, "max": 365, "step": 1, "icon": ICONS["walk"]}
    },
    
    "input_text": {
        # GPS & Location
        "current_location": {"name": "Aktueller Standort", "max": 255, "icon": ICONS["location"]},
        "last_known_location": {"name": "Letzter bekannter Standort", "max": 100, "icon": ICONS["location"]},
        "home_coordinates": {"name": "Zuhause Koordinaten", "max": 50, "icon": "mdi:home-map-marker"},
        "home_location": {"name": "Zuhause Standort", "max": 100, "icon": "mdi:home-map-marker"},
        "current_walk_route": {"name": "Aktuelle Spaziergang-Route", "max": 2000, "icon": ICONS["route"]},
        "current_walk_data": {"name": "Aktuelle Spaziergang-Daten", "max": 1000, "icon": ICONS["walk"]},
        "favorite_walk_locations": {"name": "Lieblings-Spaziergänge", "max": 500, "icon": "mdi:star"},
        "favorite_walks": {"name": "Lieblings-Spaziergänge", "max": 500, "icon": "mdi:star"},
        "walk_history_today": {"name": "Heutige Spaziergang-Historie", "max": 2000, "icon": "mdi:history"},
        "gps_tracker_id": {"name": "GPS-Tracker ID", "max": 50, "icon": ICONS["gps"]},
        "geofence_alerts": {"name": "Geofence Benachrichtigungen", "max": 255, "icon": ICONS["attention"]},
        "walk_statistics_summary": {"name": "Spaziergang-Statistiken", "max": 2000, "icon": "mdi:chart-box"},
        "gps_tracker_status": {"name": "GPS-Tracker Status", "max": 255, "icon": ICONS["gps"]},
        "last_walk_route": {"name": "Letzte Spaziergangsroute", "max": 1000},
        
        # Notes and documentation
        "notes": {"name": "Allgemeine Notizen", "max": 1000, "icon": "mdi:note-text"},
        "daily_notes": {"name": "Tagesnotizen", "max": 255, "icon": "mdi:note-text"},
        "behavior_notes": {"name": "Verhaltensnotizen", "max": 255, "icon": "mdi:note-text"},
        "last_activity_notes": {"name": "Letzte Aktivität Notizen", "max": 255, "icon": "mdi:note-text"},
        "walk_notes": {"name": "Spaziergang Notizen", "max": 255, "icon": "mdi:note-text"},
        "play_notes": {"name": "Spiel Notizen", "max": 255, "icon": "mdi:note-text"},
        "training_notes": {"name": "Training Notizen", "max": 255, "icon": "mdi:note-text"},
        
        # Health information
        "health_notes": {"name": "Gesundheitsnotizen", "max": 500, "icon": ICONS["health"]},
        "medication_notes": {"name": "Medikamentenotizen", "max": 255, "icon": ICONS["medication"]},
        "vet_notes": {"name": "Tierarztnotizen", "max": 255, "icon": ICONS["vet"]},
        "symptoms": {"name": "Symptome", "max": 255, "icon": "mdi:emoticon-sad"},
        "allergies": {"name": "Allergien", "max": 255, "icon": "mdi:alert"},
        "current_medication": {"name": "Aktuelle Medikation", "max": 500},
        
        # Emergency and contacts
        "emergency_contact": {"name": "Notfallkontakt", "max": 150, "icon": ICONS["emergency"]},
        "vet_contact": {"name": "Tierarztkontakt", "max": 150, "icon": ICONS["vet"]},
        "backup_contact": {"name": "Backup-Kontakt", "max": 150, "icon": "mdi:phone"},
        
        # Dog information
        "breed": {"name": "Rasse", "max": 100, "icon": ICONS["dog"]},
        "color": {"name": "Farbe/Markierungen", "max": 100, "icon": "mdi:palette"},
        "microchip_id": {"name": "Mikrochip ID", "max": 50, "icon": "mdi:barcode"},
        "insurance_number": {"name": "Versicherungsnummer", "max": 50, "icon": "mdi:card-account-details"},
        
        # Visitor information
        "visitor_name": {"name": "Besucher Name", "max": 150, "icon": ICONS["visitor"]},
        "visitor_contact": {"name": "Besucher Kontakt", "max": 150, "icon": "mdi:phone"},
        "visitor_notes": {"name": "Besucher Notizen", "max": 255, "icon": "mdi:note-text"},
        "visitor_instructions": {"name": "Besucher Anweisungen", "max": 500, "icon": "mdi:note-text"},
        
        # Food information
        "food_brand": {"name": "Futtermarke", "max": 150, "icon": ICONS["food"]},
        "food_allergies": {"name": "Futterallergien", "max": 255, "icon": "mdi:alert"},
        "favorite_treats": {"name": "Lieblings-Leckerlis", "max": 150, "icon": ICONS["bone"]},
        "feeding_instructions": {"name": "Fütterungsanweisungen", "max": 500, "icon": ICONS["food"]},
        
        # Status and preferences
        "current_mood": {"name": "Aktuelle Stimmung", "max": 50, "icon": ICONS["happy"]},
        "weather_preference": {"name": "Wetterpräferenz", "max": 50, "icon": "mdi:weather-sunny"},
        "special_instructions": {"name": "Besondere Anweisungen", "max": 500, "icon": "mdi:note-text"},
        
        # Vaccination records
        "vaccination_records": {"name": "Impfaufzeichnungen", "max": 500, "icon": ICONS["vaccination"]},
        "vaccination_vet_name": {"name": "Impfender Tierarzt", "max": 100, "icon": ICONS["vet"]},
        "vaccination_certificate_number": {"name": "Impfzertifikat Nummer", "max": 50, "icon": "mdi:file-certificate"}
    },
    
    "input_datetime": {
        # Last activities
        "last_walk": {"name": "Letzter Spaziergang", "has_date": True, "has_time": True, "icon": ICONS["walk"]},
        "last_feeding": {"name": "Letzte Fütterung", "has_date": True, "has_time": True},
        "last_feeding_morning": {"name": "Letztes Frühstück", "has_date": True, "has_time": True, "icon": ICONS["morning"]},
        "last_feeding_lunch": {"name": "Letztes Mittagessen", "has_date": True, "has_time": True, "icon": ICONS["lunch"]},
        "last_feeding_evening": {"name": "Letztes Abendessen", "has_date": True, "has_time": True, "icon": ICONS["evening"]},
        "last_feeding_snack": {"name": "Letztes Leckerli", "has_date": True, "has_time": True, "icon": ICONS["bone"]},
        "last_outside": {"name": "Letztes Mal draußen", "has_date": True, "has_time": True, "icon": ICONS["outside"]},
        "last_play": {"name": "Letztes Spielen", "has_date": True, "has_time": True, "icon": ICONS["play"]},
        "last_training": {"name": "Letztes Training", "has_date": True, "has_time": True, "icon": ICONS["training"]},
        "last_poop": {"name": "Letztes Geschäft", "has_date": True, "has_time": True, "icon": ICONS["poop"]},
        "last_activity": {"name": "Letzte Aktivität", "has_date": True, "has_time": True, "icon": ICONS["status"]},
        "last_door_ask": {"name": "Letztes Tür-Anfordern", "has_date": True, "has_time": True, "icon": "mdi:door"},
        "last_medication": {"name": "Letzte Medikation", "has_date": True, "has_time": True, "icon": ICONS["medication"]},
        "last_grooming": {"name": "Letzte Fellpflege", "has_date": True, "has_time": True, "icon": ICONS["grooming"]},
        "last_weight_check": {"name": "Letzte Gewichtskontrolle", "has_date": True, "has_time": False},
        
        # Feeding schedule times
        "feeding_morning_time": {"name": "Frühstückszeit", "has_date": False, "has_time": True, "initial": "07:00:00", "icon": ICONS["morning"]},
        "feeding_lunch_time": {"name": "Mittagszeit", "has_date": False, "has_time": True, "initial": "12:00:00", "icon": ICONS["lunch"]},
        "feeding_evening_time": {"name": "Abendzeit", "has_date": False, "has_time": True, "initial": "18:00:00", "icon": ICONS["evening"]},
        
        # Health & vet appointments
        "last_vet_visit": {"name": "Letzter Tierarztbesuch", "has_date": True, "has_time": True, "icon": ICONS["vet"]},
        "next_vet_appointment": {"name": "Nächster Tierarzttermin", "has_date": True, "has_time": True, "icon": ICONS["vet"]},
        "last_vaccination": {"name": "Letzte Impfung", "has_date": True, "has_time": True, "icon": ICONS["vaccination"]},
        "next_vaccination": {"name": "Nächste Impfung", "has_date": True, "has_time": True, "icon": ICONS["vaccination"]},
        "medication_time": {"name": "Medikamentenzeit", "has_date": False, "has_time": True, "initial": "08:00:00", "icon": ICONS["medication"]},
        "next_medication": {"name": "Nächste Medikation", "has_date": True, "has_time": True, "icon": ICONS["medication"]},
        "next_grooming": {"name": "Nächste Fellpflege", "has_date": True, "has_time": True, "icon": ICONS["grooming"]},
        
        # Detailed vaccination timeline
        "last_rabies_vaccination": {"name": "Letzte Tollwutimpfung", "has_date": True, "has_time": True, "icon": ICONS["vaccination"]},
        "next_rabies_vaccination": {"name": "Nächste Tollwutimpfung", "has_date": True, "has_time": True, "icon": ICONS["vaccination"]},
        "last_distemper_vaccination": {"name": "Letzte Staupeimpfung", "has_date": True, "has_time": True, "icon": ICONS["vaccination"]},
        "next_distemper_vaccination": {"name": "Nächste Staupeimpfung", "has_date": True, "has_time": True, "icon": ICONS["vaccination"]},
        "last_hepatitis_vaccination": {"name": "Letzte Hepatitisimpfung", "has_date": True, "has_time": True, "icon": ICONS["vaccination"]},
        "next_hepatitis_vaccination": {"name": "Nächste Hepatitisimpfung", "has_date": True, "has_time": True, "icon": ICONS["vaccination"]},
        
        # Special events
        "emergency_contact_time": {"name": "Notfallkontaktzeit", "has_date": True, "has_time": True, "icon": ICONS["emergency"]},
        "visitor_start": {"name": "Besuchsbeginn", "has_date": True, "has_time": True, "icon": ICONS["visitor"]},
        "visitor_end": {"name": "Besuchsende", "has_date": True, "has_time": True, "icon": ICONS["visitor"]},
        "birth_date": {"name": "Geburtsdatum", "has_date": True, "has_time": False, "icon": "mdi:cake-variant"}
    },
    
    "counter": {
        # Feeding counters
        "feeding_morning_count": {"name": "Frühstück Anzahl", "initial": 0, "step": 1, "icon": ICONS["morning"]},
        "feeding_lunch_count": {"name": "Mittagessen Anzahl", "initial": 0, "step": 1, "icon": ICONS["lunch"]},
        "feeding_evening_count": {"name": "Abendessen Anzahl", "initial": 0, "step": 1, "icon": ICONS["evening"]},
        "feeding_snack_count": {"name": "Leckerli Anzahl", "initial": 0, "step": 1, "icon": ICONS["bone"]},
        "feeding_count_today": {"name": "Fütterungen heute", "initial": 0, "step": 1},
        
        # Activity counters
        "outside_count": {"name": "Draußen Anzahl", "initial": 0, "step": 1, "icon": ICONS["outside"]},
        "activity_count": {"name": "Aktivitäten Anzahl", "initial": 0, "step": 1, "icon": ICONS["status"]},
        "walk_count": {"name": "Spaziergang Anzahl", "initial": 0, "step": 1, "icon": ICONS["walk"]},
        "play_count": {"name": "Spielzeit Anzahl", "initial": 0, "step": 1, "icon": ICONS["play"]},
        "training_count": {"name": "Training Anzahl", "initial": 0, "step": 1, "icon": ICONS["training"]},
        "poop_count": {"name": "Geschäft Anzahl", "initial": 0, "step": 1, "icon": ICONS["poop"]},
        
        # Daily/Weekly/Monthly counters  
        "daily_walks": {"name": "Tägliche Spaziergänge", "initial": 0, "step": 1, "icon": ICONS["walk"]},
        "weekly_walks": {"name": "Wöchentliche Spaziergänge", "initial": 0, "step": 1, "icon": ICONS["walk"]},
        "monthly_walks": {"name": "Monatliche Spaziergänge", "initial": 0, "step": 1, "icon": ICONS["walk"]},
        "total_walks": {"name": "Gesamt-Spaziergänge", "initial": 0, "step": 1, "icon": ICONS["walk"]},
        
        # Health counters
        "vet_visits_count": {"name": "Tierarztbesuche", "initial": 0, "step": 1, "icon": ICONS["vet"]},
        "medication_count": {"name": "Medikamente Anzahl", "initial": 0, "step": 1, "icon": ICONS["medication"]},
        "grooming_count": {"name": "Pflege Anzahl", "initial": 0, "step": 1, "icon": ICONS["grooming"]},
        
        # Vaccination counters
        "total_vaccinations_count": {"name": "Gesamt-Impfungen", "initial": 0, "step": 1, "icon": ICONS["vaccination"]},
        "rabies_vaccinations_count": {"name": "Tollwut-Impfungen", "initial": 0, "step": 1, "icon": ICONS["vaccination"]},
        "distemper_vaccinations_count": {"name": "Staupe-Impfungen", "initial": 0, "step": 1, "icon": ICONS["vaccination"]},
        
        # Emergency counters
        "emergency_calls": {"name": "Notfälle", "initial": 0, "step": 1, "icon": ICONS["emergency"]},
        "missed_feedings": {"name": "Verpasste Fütterungen", "initial": 0, "step": 1, "icon": "mdi:alert"},
        "daily_score": {"name": "Täglicher Score", "initial": 0, "step": 1, "icon": "mdi:star"},
        "social_interactions": {"name": "Soziale Interaktionen", "initial": 0, "step": 1, "icon": "mdi:account-group"},
        "behavior_incidents": {"name": "Verhaltensvorfälle", "initial": 0, "step": 1, "icon": "mdi:alert-circle"},
        "rewards_given": {"name": "Belohnungen gegeben", "initial": 0, "step": 1, "icon": "mdi:gift"},
        
        # Weekly/Monthly summary counters
        "weekly_activities": {"name": "Wöchentliche Aktivitäten", "initial": 0, "step": 1, "icon": "mdi:calendar-week"},
        "monthly_vet_visits": {"name": "Monatliche Tierarztbesuche", "initial": 0, "step": 1, "icon": "mdi:calendar-month"}
    },
    
    "input_select": {
        # Core status selects
        "activity_level": {"name": "Aktivitätslevel", "options": ["Sehr niedrig", "Niedrig", "Normal", "Hoch", "Sehr hoch"], "initial": "Normal", "icon": ICONS["play"]},
        "mood": {"name": "Stimmung", "options": MOOD_OPTIONS, "initial": "😊 Glücklich", "icon": ICONS["happy"]},
        "mood_select": {"name": "Stimmung", "options": MOOD_OPTIONS, "initial": "😊 Glücklich", "icon": ICONS["happy"]},
        "energy_level_category": {"name": "Energie Kategorie", "options": ENERGY_LEVELS, "initial": "Normal", "icon": "mdi:flash"},
        "appetite_level": {"name": "Appetit Level", "options": APPETITE_LEVELS, "initial": "Normal", "icon": ICONS["food"]},
        "health_status": {"name": "Gesundheitsstatus", "options": HEALTH_STATUS_OPTIONS, "initial": "Gut", "icon": ICONS["health"]},
        "health_status_select": {"name": "Gesundheitsstatus", "options": HEALTH_STATUS_OPTIONS, "initial": "Gut", "icon": ICONS["health"]},
        
        # Preferences and categories
        "weather_preference": {"name": "Wetterpräferenz", "options": ["Sonnig bevorzugt", "Bewölkt OK", "Leichter Regen OK", "Starker Regen vermeiden", "Schnee OK", "Alle Wetter"], "initial": "Sonnig bevorzugt", "icon": "mdi:weather-partly-cloudy"},
        "size_category": {"name": "Größenkategorie", "options": ["Toy (bis 4kg)", "Klein (4-10kg)", "Mittel (10-25kg)", "Groß (25-40kg)", "Riesig (über 40kg)"], "initial": "Mittel (10-25kg)", "icon": ICONS["dog"]},
        "seasonal_mode": {"name": "Saison-Modus", "options": ["Frühling", "Sommer", "Herbst", "Winter", "Automatisch"], "initial": "Automatisch", "icon": "mdi:leaf"},
        "training_level": {"name": "Trainingslevel", "options": ["Untrainiert", "Anfänger", "Grundlagen", "Fortgeschritten", "Gut trainiert", "Experte", "Champion"], "initial": "Grundlagen", "icon": ICONS["training"]},
        "emergency_level": {"name": "Notfalllevel", "options": ["Normal", "Beobachten", "Aufmerksamkeit", "Warnung", "Dringend", "Kritisch", "Notfall"], "initial": "Normal", "icon": ICONS["emergency"]},
        "coat_type": {"name": "Fellart", "options": ["Kurzhaar", "Langhaar", "Drahthaar", "Locken", "Kahl"], "initial": "Kurzhaar", "icon": ICONS["grooming"]},
        "age_group": {"name": "Altersgruppe", "options": ["Welpe", "Junghund", "Adult", "Senior"], "initial": "Adult", "icon": "mdi:cake-variant"},
        "obedience_level": {"name": "Gehorsam", "options": ["Schlecht", "Verbesserungsbedürftig", "Durchschnitt", "Gut", "Sehr gut", "Exzellent"], "initial": "Durchschnitt", "icon": ICONS["training"]},
        "living_situation": {"name": "Wohnsituation", "options": ["Wohnung", "Haus mit Garten", "Bauernhof", "Sonstiges"], "initial": "Haus mit Garten", "icon": "mdi:home"},
        "socialization": {"name": "Sozialisierung", "options": ["Sehr schüchtern", "Schüchtern", "Normal", "Aufgeschlossen", "Sehr sozial"], "initial": "Normal", "icon": "mdi:account-group"},
        
        # Activity and feeding preferences
        "current_activity": {"name": "Aktuelle Aktivität", "options": ["Schläft", "Frisst", "Spielt", "Spaziergang", "Ruht", "Aktiv"], "initial": "Ruht"},
        "feeding_schedule": {"name": "Fütterungsplan", "options": ["1x täglich", "2x täglich", "3x täglich", "Nach Bedarf"], "initial": "2x täglich"},
        "walk_frequency": {"name": "Spaziergang-Häufigkeit", "options": ["1x täglich", "2x täglich", "3x täglich", "Nach Bedarf"], "initial": "2x täglich"},
        
        # Vaccination status
        "vaccination_status": {"name": "Impfungsstatus", "options": VACCINATION_STATUS_OPTIONS, "initial": "Vollständig geimpft", "icon": ICONS["vaccination"]},
        "rabies_vaccination_status": {"name": "Tollwut-Impfungsstatus", "options": SPECIFIC_VACCINATION_STATUS_OPTIONS, "initial": "Aktuell", "icon": ICONS["vaccination"]},
        "distemper_vaccination_status": {"name": "Staupe-Impfungsstatus", "options": SPECIFIC_VACCINATION_STATUS_OPTIONS, "initial": "Aktuell", "icon": ICONS["vaccination"]},
        "hepatitis_vaccination_status": {"name": "Hepatitis-Impfungsstatus", "options": SPECIFIC_VACCINATION_STATUS_OPTIONS, "initial": "Aktuell", "icon": ICONS["vaccination"]}
    }
}

# =========================
# STATUS MESSAGES & UI
# =========================

STATUS_MESSAGES = {
    "excellent": "🌟 Ausgezeichnet",
    "very_good": "😊 Sehr gut", 
    "good": "👍 Gut",
    "needs_attention": "⚠️ Braucht Aufmerksamkeit",
    "concern": "😟 Bedenklich",
    "emergency": "🚨 Notfall",
    "unknown": "❓ Unbekannt",
    "all_good": "Alles in Ordnung",
    "needs_feeding": "Fütterung erforderlich",
    "needs_outside": "Muss raus",
    "visitor_mode": "Besuchsmodus aktiv",
    "attention_needed": "Aufmerksamkeit erforderlich",
    "sick": "Gesundheitsprobleme",
    "happy": "Zufrieden",
    "active": "Sehr aktiv",
    "bored": "Gelangweilt",
    "tired": "Müde"
}

ACTIVITY_STATUS = {
    "all_done": "✅ Alles erledigt",
    "partially_done": "📝 Teilweise erledigt", 
    "needs_feeding": "🍽️ Fütterung ausstehend",
    "needs_walk": "🚶 Spaziergang ausstehend",
    "needs_both": "⏰ Fütterung & Spaziergang ausstehend",
    "visitor_mode": "👥 Besuchsmodus aktiv",
    "emergency": "🚨 Notfallmodus aktiv",
}

# =========================
# VALIDATION & LIMITS
# =========================

VALIDATION_RULES = {
    "weight": {"min": 0.5, "max": 100, "unit": "kg"},
    "temperature": {"min": 35.0, "max": 42.0, "unit": "°C"},
    "heart_rate": {"min": 60, "max": 250, "unit": "bpm"},
    "gps_accuracy": {"min": 1, "max": 100, "unit": "m"},
    "walk_distance": {"min": 0, "max": 50, "unit": "km"},
    "walk_duration": {"min": 0, "max": 600, "unit": "minutes"},
    "food_amount": {"min": 0, "max": 5000, "unit": "g"},
    "water_amount": {"min": 0, "max": 5000, "unit": "ml"}
}

GPS_ACCURACY_THRESHOLDS = {
    "excellent": 5,    # < 5m
    "good": 15,        # 5-15m
    "acceptable": 50,  # 15-50m
    "poor": 100        # > 50m
}

NOTIFICATION_PRIORITIES = {
    "low": {"color": "green", "sound": False, "persistent": False},
    "normal": {"color": "blue", "sound": True, "persistent": False},
    "high": {"color": "orange", "sound": True, "persistent": True},
    "critical": {"color": "red", "sound": True, "persistent": True}
}

# Validation limits
MIN_DOG_NAME_LENGTH = 2
MAX_DOG_NAME_LENGTH = 50
MIN_DOG_WEIGHT = 0.5
MAX_DOG_WEIGHT = 100.0
MIN_DOG_AGE = 0
MAX_DOG_AGE = 30

# API timeouts
API_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 5

# =========================
# ATTRIBUTE NAMES (für Rückwärtskompatibilität)
# =========================

ATTR_DOG_NAME = "dog_name"
ATTR_DOG_BREED = "dog_breed"
ATTR_DOG_AGE = "dog_age"
ATTR_DOG_WEIGHT = "dog_weight"
ATTR_LAST_UPDATED = "last_updated"
ATTR_HEALTH_STATUS = "health_status"
ATTR_ACTIVITY_LEVEL = "activity_level"
ATTR_MOOD = "mood"
ATTR_STREAK_COUNT = "streak_count"
ATTR_FOOD_TYPE = "food_type"
ATTR_FOOD_AMOUNT = "food_amount"
ATTR_WALK_DURATION = "walk_duration"
ATTR_GPS_ACCURACY = "gps_accuracy"
ATTR_GPS_PROVIDER = "gps_provider"

# =========================
# INTEGRATION CONSTANTS
# =========================

WEBHOOK_ENDPOINTS = {
    "gps_update": "/api/paw_control/gps_update",
    "health_alert": "/api/paw_control/health_alert",
    "emergency": "/api/paw_control/emergency",
    "activity_update": "/api/paw_control/activity"
}

API_TIMEOUTS = {
    "gps_update": 30,
    "health_check": 60,
    "data_sync": 120
}

BACKUP_SETTINGS = {
    "auto_backup": True,
    "backup_frequency": "daily",
    "max_backups": 30,
    "include_gps_data": True
}

# =========================
# DEFAULT CONFIGURATIONS
# =========================

DEFAULT_SETTINGS = {
    "update_interval": 300,  # 5 minutes
    "gps_update_interval": 60,  # 1 minute during walks
    "notification_enabled": True,
    "auto_walk_detection": True,
    "geofence_enabled": True,
    "health_monitoring": True,
    "backup_enabled": True,
    "debug_mode": False
}

# =========================
# DASHBOARD & EVENTS
# =========================

# Dashboard configuration
DASHBOARD_CONFIG = {
    "title": "🐶 Paw Control",
    "icon": "mdi:dog",
    "path": "paw_control",
    "show_in_sidebar": True,
    "require_admin": False
}

# Update intervals (in seconds)
UPDATE_INTERVAL = 30
HEALTH_CHECK_INTERVAL = 300  # 5 minutes

# Visitor mode settings
VISITOR_MODE_SETTINGS = {
    "reduced_notifications": True,
    "disable_automatic_reminders": True,
    "emergency_contacts_only": False
}

# Multi-dog support
MAX_DOGS = 10
DOG_NAME_PATTERN = r"^[a-z][a-z0-9_]*$"

# Blueprint automation names
BLUEPRINT_AUTOMATIONS = {
    "door_sensor": "paw_control_door_sensor",
    "feeding_reminder": "paw_control_feeding_reminder", 
    "daily_reset": "paw_control_daily_reset",
    "health_check": "paw_control_health_check",
    "gps_tracking": "paw_control_gps_tracking"
}

# Event names for automations
EVENTS = {
    "dog_outside_confirmed": "paw_control_dog_outside_confirmed",
    "dog_outside_denied": "paw_control_dog_outside_denied", 
    "feeding_completed": "paw_control_feeding_completed",
    "emergency_activated": "paw_control_emergency_activated",
    "visitor_mode_changed": "paw_control_visitor_mode_changed",
    "walk_started": "paw_control_walk_started",
    "walk_ended": "paw_control_walk_ended",
    "health_alert": "paw_control_health_alert",
    "gps_location_updated": "paw_control_gps_location_updated"
}

EVENT_WALK_STARTED = f"{DOMAIN}_walk_started"
EVENT_WALK_STOPPED = f"{DOMAIN}_walk_stopped"
EVENT_GEOFENCE_ENTERED = f"{DOMAIN}_geofence_entered"
EVENT_GEOFENCE_EXITED = f"{DOMAIN}_geofence_exited"
EVENT_FEEDING_TIME = f"{DOMAIN}_feeding_time"
EVENT_MEDICATION_DUE = f"{DOMAIN}_medication_due"
EVENT_VET_APPOINTMENT_REMINDER = f"{DOMAIN}_vet_appointment_reminder"

# Data storage keys
DATA_COORDINATOR = "coordinator"
DATA_CONFIG = "config"
DATA_LISTENERS = "listeners"
DATA_GPS_TRACKER = "gps_tracker"
DATA_SERVICES = "services"

# Weather integration
WEATHER_CONDITIONS = {
    "rain": "Regen",
    "snow": "Schnee",
    "storm": "Sturm",
    "hot": "Heiß",
    "cold": "Kalt"
}

# Seasonal adjustments
SEASONAL_ADJUSTMENTS = {
    "summer": {
        "early_morning_walk": True,
        "midday_break": True,
        "extra_water": True
    },
    "winter": {
        "shorter_walks": True,
        "warm_clothing": True,
        "de_ice_paws": True
    }
}

# Breed size categories with typical weights
BREED_SIZES = {
    "toy": {"weight_range": (1, 4), "daily_food_base": 50},
    "small": {"weight_range": (4, 10), "daily_food_base": 100},
    "medium": {"weight_range": (10, 25), "daily_food_base": 200},
    "large": {"weight_range": (25, 45), "daily_food_base": 300},
    "giant": {"weight_range": (45, 100), "daily_food_base": 400}
}

# Entity prefixes
BINARY_SENSOR_PREFIX = "binary_sensor"
SENSOR_PREFIX = "sensor"
INPUT_BOOLEAN_PREFIX = "input_boolean"
COUNTER_PREFIX = "counter"
INPUT_DATETIME_PREFIX = "input_datetime"
INPUT_TEXT_PREFIX = "input_text"
BUTTON_PREFIX = "button"

# =========================
# PAW CONTROL CONFIGURATION
# =========================

PAW_CONTROL_CONFIG = {
    "version": "1.0.0",
    "entity_count": 140,  # Total entities defined
    "service_count": len(SERVICES),
    "gps_providers": len(GPS_PROVIDERS),
    "supported_languages": ["de", "en"],
    "default_language": "de",
    "platforms": len(PLATFORMS)
}
