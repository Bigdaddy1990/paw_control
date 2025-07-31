"""Constants for Paw Control integration."""
from __future__ import annotations

from homeassistant.const import Platform

# Integration details
DOMAIN = "pawcontrol"
PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]

# Configuration keys
CONF_DOG_NAME = "dog_name"
CONF_DOG_BREED = "dog_breed"
CONF_DOG_AGE = "dog_age"
CONF_DOG_WEIGHT = "dog_weight"
CONF_GPS_ENABLE = "gps_enable"
CONF_NOTIFICATIONS_ENABLED = "notifications_enabled"
CONF_AUTO_WALK_DETECTION = "auto_walk_detection"
CONF_GEOFENCE_RADIUS = "geofence_radius"
CONF_HOME_LATITUDE = "home_latitude"
CONF_HOME_LONGITUDE = "home_longitude"

# Default values
DEFAULT_DOG_AGE = 3
DEFAULT_DOG_WEIGHT = 15.0
DEFAULT_GEOFENCE_RADIUS = 100
DEFAULT_HOME_COORDINATES = (52.233333, 8.966667)

# Validation constraints
MIN_DOG_NAME_LENGTH = 2
MAX_DOG_NAME_LENGTH = 50
MIN_DOG_WEIGHT = 0.5
MAX_DOG_WEIGHT = 100.0
MIN_DOG_AGE = 0
MAX_DOG_AGE = 25
DOG_NAME_PATTERN = r'^[a-zA-ZäöüÄÖÜß0-9\s\-_.]+$'

# GPS and location
GPS_ACCURACY_THRESHOLDS = {
    "excellent": 5,
    "good": 15,
    "acceptable": 50,
    "poor": 100
}

GEOFENCE_MIN_RADIUS = 10
GEOFENCE_MAX_RADIUS = 1000

# Feeding types and meal mappings
FEEDING_TYPES = ["morning", "lunch", "evening", "snack"]
MEAL_TYPES = {
    "morning": "Frühstück",
    "lunch": "Mittagessen",
    "evening": "Abendessen",
    "snack": "Leckerli"
}

DEFAULT_FEEDING_TIMES = {
    "morning": "07:00",
    "lunch": "12:00",
    "evening": "18:00",
    "snack": "15:00"
}

DEFAULT_FEEDING_TIMES_DICT = {meal: time for meal, time in DEFAULT_FEEDING_TIMES.items()}

# Activity levels and categories
ACTIVITY_LEVELS = [
    "Sehr niedrig",
    "Niedrig",
    "Normal",
    "Hoch",
    "Sehr hoch"
]

SIZE_CATEGORIES = [
    "Toy (unter 4kg)",
    "Klein (4-10kg)",
    "Mittel (10-25kg)",
    "Groß (25-45kg)",
    "Riesig (über 45kg)"
]

# Health status options
HEALTH_STATUS_OPTIONS = [
    "Ausgezeichnet",
    "Sehr gut",
    "Gut",
    "Normal",
    "Unwohl",
    "Krank",
    "Notfall"
]

MOOD_OPTIONS = [
    "😊 Sehr glücklich",
    "😃 Glücklich",
    "😐 Neutral",
    "😟 Traurig",
    "😠 Ärgerlich",
    "😰 Ängstlich",
    "😴 Müde",
    "🤒 Krank"
]

ENERGY_LEVEL_OPTIONS = [
    "Sehr niedrig",
    "Niedrig",
    "Normal",
    "Hoch",
    "Sehr hoch"
]

APPETITE_LEVEL_OPTIONS = [
    "Kein Appetit",
    "Wenig Appetit",
    "Normal",
    "Guter Appetit",
    "Sehr guter Appetit"
]

# Emergency levels
EMERGENCY_LEVELS = [
    "Normal",
    "Achtung",
    "Warnung",
    "Kritisch",
    "Notfall"
]

# Training types
TRAINING_TYPES = [
    "Grundgehorsam",
    "Leinenführigkeit",
    "Sozialisierung",
    "Tricks",
    "Agility",
    "Schutztraining",
    "Therapiehund",
    "Sonstiges"
]

# Walk types
WALK_TYPES = [
    "Kurzer Gassigang",
    "Normaler Spaziergang",
    "Langer Spaziergang",
    "Joggen",
    "Wanderung",
    "Freilauf",
    "Training",
    "Sozialisierung"
]

# Play types
PLAY_TYPES = [
    "Freies Spiel",
    "Ball spielen",
    "Tauziehen",
    "Verstecken",
    "Apportieren",
    "Wasserspiele",
    "Suchspiele",
    "Agilitätsspiele"
]

# Status messages
STATUS_MESSAGES = {
    "all_done": "✅ Alles erledigt",
    "partially_done": "📝 Teilweise erledigt",
    "needs_feeding": "🍽️ Fütterung ausstehend",
    "needs_walk": "🚶 Spaziergang ausstehend",
    "needs_attention": "⚠️ Aufmerksamkeit erforderlich",
    "emergency": "🚨 NOTFALL",
    "visitor_mode": "👥 Besuchermodus",
    "initializing": "⏳ Initialisierung..."
}

# Icons for different entities
ICONS = {
    # Basic activities
    "food": "mdi:food-bowl",
    "walk": "mdi:walk",
    "play": "mdi:tennis",
    "training": "mdi:school",
    "sleep": "mdi:sleep",
    
    # Health
    "health": "mdi:heart-pulse",
    "weight": "mdi:weight-kilogram",
    "temperature": "mdi:thermometer",
    "medication": "mdi:pill",
    "vet": "mdi:stethoscope",
    
    # Location/GPS
    "location": "mdi:map-marker",
    "gps": "mdi:crosshairs-gps",
    "signal": "mdi:signal",
    "home": "mdi:home",
    "outside": "mdi:door-open",
    
    # Status
    "status": "mdi:information",
    "emergency": "mdi:alert",
    "visitor": "mdi:account-group",
    "mood": "mdi:emoticon",
    
    # Time-based
    "morning": "mdi:weather-sunrise",
    "lunch": "mdi:weather-sunny",
    "evening": "mdi:weather-sunset",
    "night": "mdi:weather-night",
    
    # Counters/Stats
    "counter": "mdi:counter",
    "statistics": "mdi:chart-line",
    "report": "mdi:file-chart",
    
    # System
    "settings": "mdi:cog",
    "automation": "mdi:robot",
    "notification": "mdi:bell",
    "battery": "mdi:battery",
    
    # Activities
    "poop": "mdi:toilet",
    "grooming": "mdi:content-cut",
    "socialization": "mdi:account-multiple"
}

# Service parameter constants
SERVICE_DOG_NAME = "dog_name"
SERVICE_FOOD_TYPE = "food_type"
SERVICE_FOOD_AMOUNT = "food_amount"
SERVICE_MEAL_TYPE = "meal_type"
SERVICE_DURATION = "duration"
SERVICE_WALK_TYPE = "walk_type"
SERVICE_DISTANCE = "distance"
SERVICE_WEIGHT = "weight"
SERVICE_TEMPERATURE = "temperature"
SERVICE_ENERGY_LEVEL = "energy_level"
SERVICE_SYMPTOMS = "symptoms"
SERVICE_NOTES = "notes"
SERVICE_MOOD = "mood"
SERVICE_VET_DATE = "vet_date"
SERVICE_LATITUDE = "latitude"
SERVICE_LONGITUDE = "longitude"
SERVICE_ACCURACY = "accuracy"

# Validation rules for numeric inputs
VALIDATION_RULES = {
    "weight": {"min": MIN_DOG_WEIGHT, "max": MAX_DOG_WEIGHT, "unit": "kg"},
    "age": {"min": MIN_DOG_AGE, "max": MAX_DOG_AGE, "unit": "Jahre"},
    "temperature": {"min": 35.0, "max": 42.0, "unit": "°C"},
    "duration": {"min": 1, "max": 300, "unit": "Minuten"},
    "distance": {"min": 0.1, "max": 50.0, "unit": "km"},
    "accuracy": {"min": 1, "max": 1000, "unit": "m"},
    "food_amount": {"min": 10, "max": 2000, "unit": "g"}
}

# Entity attribute names
ATTR_DOG_NAME = "dog_name"
ATTR_LAST_UPDATED = "last_updated"
ATTR_ENTITY_COUNT = "entity_count"
ATTR_SUCCESS_RATE = "success_rate"
ATTR_GPS_COORDINATES = "gps_coordinates"
ATTR_GPS_ACCURACY = "gps_accuracy"
ATTR_HOME_DISTANCE = "home_distance"
ATTR_WALK_STATS = "walk_stats"
ATTR_HEALTH_SCORE = "health_score"
ATTR_ACTIVITY_LEVEL = "activity_level"

# Complete entity definitions for helper creation
ENTITIES = {
    "input_boolean": {
        # Daily feeding status
        "feeding_morning": {"name": "Frühstück gegeben", "icon": "mdi:weather-sunrise"},
        "feeding_lunch": {"name": "Mittagessen gegeben", "icon": "mdi:weather-sunny"},
        "feeding_evening": {"name": "Abendessen gegeben", "icon": "mdi:weather-sunset"},
        "feeding_snack": {"name": "Leckerli gegeben", "icon": "mdi:food"},
        
        # Daily activities
        "outside": {"name": "War draußen", "icon": "mdi:door-open"},
        "walked_today": {"name": "Heute spaziert", "icon": "mdi:walk"},
        "played_today": {"name": "Heute gespielt", "icon": "mdi:tennis"},
        "poop_done": {"name": "Geschäft gemacht", "icon": "mdi:toilet"},
        "socialized_today": {"name": "Heute sozialisiert", "icon": "mdi:account-multiple"},
        
        # Session status
        "walk_in_progress": {"name": "Spaziergang läuft", "icon": "mdi:walk"},
        "training_session": {"name": "Training läuft", "icon": "mdi:school"},
        "playtime_session": {"name": "Spielzeit läuft", "icon": "mdi:tennis"},
        
        # Health and care
        "medication_given": {"name": "Medikament gegeben", "icon": "mdi:pill"},
        "needs_grooming": {"name": "Pflege nötig", "icon": "mdi:content-cut"},
        
        # System modes
        "emergency_mode": {"name": "Notfallmodus", "icon": "mdi:alert"},
        "visitor_mode_input": {"name": "Besuchsmodus", "icon": "mdi:account-group"},
        "auto_walk_detection": {"name": "Auto-Spaziergang-Erkennung", "icon": "mdi:crosshairs-gps"}
    },
    
    "input_number": {
        # Physical metrics
        "weight": {"name": "Gewicht", "min": 0.5, "max": 100, "step": 0.1, "unit": "kg", "icon": "mdi:weight-kilogram"},
        "age_years": {"name": "Alter (Jahre)", "min": 0, "max": 25, "step": 0.1, "unit": "Jahre", "icon": "mdi:calendar"},
        "age_months": {"name": "Alter (Monate)", "min": 0, "max": 300, "step": 1, "unit": "Monate", "icon": "mdi:calendar"},
        "temperature": {"name": "Körpertemperatur", "min": 35, "max": 42, "step": 0.1, "unit": "°C", "icon": "mdi:thermometer"},
        
        # Daily amounts and durations
        "daily_food_amount": {"name": "Tägliche Futtermenge", "min": 0, "max": 2000, "step": 10, "unit": "g", "icon": "mdi:food"},
        "daily_walk_duration": {"name": "Tägliche Spaziergang-Dauer", "min": 0, "max": 480, "step": 5, "unit": "min", "icon": "mdi:walk"},
        "daily_play_duration": {"name": "Tägliche Spielzeit", "min": 0, "max": 240, "step": 5, "unit": "min", "icon": "mdi:tennis"},
        "training_duration": {"name": "Training-Dauer", "min": 0, "max": 120, "step": 1, "unit": "min", "icon": "mdi:school"},
        
        # GPS and location
        "gps_signal_strength": {"name": "GPS-Signalstärke", "min": 0, "max": 100, "step": 1, "unit": "%", "icon": "mdi:signal"},
        "gps_battery_level": {"name": "GPS-Tracker Akku", "min": 0, "max": 100, "step": 1, "unit": "%", "icon": "mdi:battery"},
        "home_distance": {"name": "Entfernung zu Hause", "min": 0, "max": 10000, "step": 1, "unit": "m", "icon": "mdi:home"},
        
        # Walk statistics
        "current_walk_distance": {"name": "Aktuelle Spaziergang-Distanz", "min": 0, "max": 50, "step": 0.01, "unit": "km", "icon": "mdi:walk"},
        "current_walk_duration": {"name": "Aktuelle Spaziergang-Dauer", "min": 0, "max": 300, "step": 1, "unit": "min", "icon": "mdi:walk"},
        "current_walk_speed": {"name": "Aktuelle Geschwindigkeit", "min": 0, "max": 50, "step": 0.1, "unit": "km/h", "icon": "mdi:speedometer"},
        "walk_distance_today": {"name": "Spaziergang-Distanz heute", "min": 0, "max": 50, "step": 0.01, "unit": "km", "icon": "mdi:chart-line"},
        "walk_distance_weekly": {"name": "Spaziergang-Distanz Woche", "min": 0, "max": 200, "step": 0.1, "unit": "km", "icon": "mdi:chart-line"},
        "calories_burned_walk": {"name": "Verbrannte Kalorien", "min": 0, "max": 2000, "step": 1, "unit": "kcal", "icon": "mdi:fire"},
        
        # Health scores
        "health_score": {"name": "Gesundheitsscore", "min": 0, "max": 10, "step": 0.1, "unit": "", "icon": "mdi:heart-pulse"},
        "happiness_score": {"name": "Glücksscore", "min": 0, "max": 10, "step": 0.1, "unit": "", "icon": "mdi:emoticon"},
        "activity_score": {"name": "Aktivitätsscore", "min": 0, "max": 10, "step": 0.1, "unit": "", "icon": "mdi:run"},
        
        # Geofencing
        "geofence_radius": {"name": "Geofence-Radius", "min": GEOFENCE_MIN_RADIUS, "max": GEOFENCE_MAX_RADIUS, "step": 10, "unit": "m", "icon": "mdi:map-marker-radius"}
    },
    
    "input_text": {
        # Basic information
        "breed": {"name": "Rasse", "max": 100, "icon": "mdi:dog"},
        "notes": {"name": "Tagesnotizen", "max": 255, "icon": "mdi:note-text"},
        "daily_notes": {"name": "Tägliche Notizen", "max": 500, "icon": "mdi:note-text-outline"},
        
        # Health notes
        "health_notes": {"name": "Gesundheitsnotizen", "max": 255, "icon": "mdi:heart-pulse"},
        "medication_notes": {"name": "Medikamentennotizen", "max": 255, "icon": "mdi:pill"},
        "vet_contact": {"name": "Tierarzt Kontakt", "max": 255, "icon": "mdi:stethoscope"},
        
        # Location and GPS
        "current_location": {"name": "Aktuelle Position", "max": 100, "icon": "mdi:map-marker"},
        "home_coordinates": {"name": "Zuhause-Koordinaten", "max": 50, "icon": "mdi:home"},
        "current_walk_route": {"name": "Aktuelle Route", "max": 1000, "icon": "mdi:map"},
        "favorite_walk_routes": {"name": "Lieblings-Routen", "max": 1000, "icon": "mdi:heart"},
        
        # GPS tracker management
        "gps_tracker_status": {"name": "GPS-Tracker Status", "max": 500, "icon": "mdi:crosshairs-gps"},
        "gps_tracker_config": {"name": "GPS-Tracker Konfiguration", "max": 1000, "icon": "mdi:cog"},
        
        # Visitor mode
        "visitor_name": {"name": "Besucher Name", "max": 100, "icon": "mdi:account"},
        "visitor_instructions": {"name": "Besucher-Anweisungen", "max": 500, "icon": "mdi:information"},
        
        # Activity history
        "walk_history_today": {"name": "Spaziergang-Historie heute", "max": 500, "icon": "mdi:history"},
        "activity_history": {"name": "Aktivitäts-Historie", "max": 1000, "icon": "mdi:history"},
        "last_activity": {"name": "Letzte Aktivität", "max": 255, "icon": "mdi:clock"}
    },
    
    "input_datetime": {
        # Feeding times
        "last_feeding_morning": {"name": "Letzte Frühstück", "has_date": True, "has_time": True, "icon": "mdi:weather-sunrise"},
        "last_feeding_lunch": {"name": "Letztes Mittagessen", "has_date": True, "has_time": True, "icon": "mdi:weather-sunny"},
        "last_feeding_evening": {"name": "Letztes Abendessen", "has_date": True, "has_time": True, "icon": "mdi:weather-sunset"},
        "last_feeding": {"name": "Letzte Fütterung", "has_date": True, "has_time": True, "icon": "mdi:food"},
        
        # Feeding schedule
        "feeding_morning_time": {"name": "Frühstück Zeit", "has_date": False, "has_time": True, "icon": "mdi:clock"},
        "feeding_lunch_time": {"name": "Mittagessen Zeit", "has_date": False, "has_time": True, "icon": "mdi:clock"},
        "feeding_evening_time": {"name": "Abendessen Zeit", "has_date": False, "has_time": True, "icon": "mdi:clock"},
        
        # Activity times
        "last_walk": {"name": "Letzter Spaziergang", "has_date": True, "has_time": True, "icon": "mdi:walk"},
        "last_outside": {"name": "Letztes Mal draußen", "has_date": True, "has_time": True, "icon": "mdi:door-open"},
        "last_play": {"name": "Letztes Spielen", "has_date": True, "has_time": True, "icon": "mdi:tennis"},
        "last_training": {"name": "Letztes Training", "has_date": True, "has_time": True, "icon": "mdi:school"},
        "last_grooming": {"name": "Letzte Pflege", "has_date": True, "has_time": True, "icon": "mdi:content-cut"},
        "last_activity": {"name": "Letzte Aktivität", "has_date": True, "has_time": True, "icon": "mdi:clock"},
        
        # Health and vet
        "last_vet_visit": {"name": "Letzter Tierarztbesuch", "has_date": True, "has_time": True, "icon": "mdi:stethoscope"},
        "next_vet_appointment": {"name": "Nächster Tierarzttermin", "has_date": True, "has_time": True, "icon": "mdi:calendar"},
        "last_medication": {"name": "Letzte Medikamentengabe", "has_date": True, "has_time": True, "icon": "mdi:pill"},
        "last_weight_check": {"name": "Letzte Gewichtskontrolle", "has_date": True, "has_time": True, "icon": "mdi:weight"},
        
        # Visitor mode
        "visitor_start": {"name": "Besuch Start", "has_date": True, "has_time": True, "icon": "mdi:account-clock"},
        "visitor_end": {"name": "Besuch Ende", "has_date": True, "has_time": True, "icon": "mdi:account-clock"},
        
        # Emergency
        "emergency_contact_time": {"name": "Notfall-Kontakt Zeit", "has_date": True, "has_time": True, "icon": "mdi:alert-circle"}
    },
    
    "input_select": {
        # Health status
        "health_status": {"name": "Gesundheitsstatus", "options": HEALTH_STATUS_OPTIONS, "icon": "mdi:heart-pulse"},
        "mood": {"name": "Stimmung", "options": MOOD_OPTIONS, "icon": "mdi:emoticon"},
        "energy_level_category": {"name": "Energielevel", "options": ENERGY_LEVEL_OPTIONS, "icon": "mdi:battery"},
        "appetite_level": {"name": "Appetit", "options": APPETITE_LEVEL_OPTIONS, "icon": "mdi:food"},
        "activity_level": {"name": "Aktivitätslevel", "options": ACTIVITY_LEVELS, "icon": "mdi:run"},
        
        # Physical characteristics
        "size_category": {"name": "Größenkategorie", "options": SIZE_CATEGORIES, "icon": "mdi:ruler"},
        
        # Emergency
        "emergency_level": {"name": "Notfall-Level", "options": EMERGENCY_LEVELS, "icon": "mdi:alert"},
        
        # GPS and walk types
        "preferred_walk_type": {"name": "Bevorzugter Spaziergang-Typ", "options": WALK_TYPES, "icon": "mdi:walk"},
        "gps_source_type": {"name": "GPS-Quelle", "options": ["Smartphone", "Tractive", "Manual", "Webhook", "MQTT"], "icon": "mdi:crosshairs-gps"}
    },
    
    "counter": {
        # Daily counters (reset daily)
        "walk_count": {"name": "Spaziergänge", "initial": 0, "step": 1, "icon": "mdi:walk"},
        "outside_count": {"name": "Draußen Anzahl", "initial": 0, "step": 1, "icon": "mdi:door-open"},
        "play_count": {"name": "Spielsessions", "initial": 0, "step": 1, "icon": "mdi:tennis"},
        "training_count": {"name": "Trainingseinheiten", "initial": 0, "step": 1, "icon": "mdi:school"},
        "poop_count": {"name": "Geschäfte", "initial": 0, "step": 1, "icon": "mdi:toilet"},
        "medication_count": {"name": "Medikamentengaben", "initial": 0, "step": 1, "icon": "mdi:pill"},
        "grooming_count": {"name": "Pflegesessions", "initial": 0, "step": 1, "icon": "mdi:content-cut"},
        
        # Feeding counters by type
        "feeding_morning_count": {"name": "Frühstück Anzahl", "initial": 0, "step": 1, "icon": "mdi:weather-sunrise"},
        "feeding_lunch_count": {"name": "Mittagessen Anzahl", "initial": 0, "step": 1, "icon": "mdi:weather-sunny"},
        "feeding_evening_count": {"name": "Abendessen Anzahl", "initial": 0, "step": 1, "icon": "mdi:weather-sunset"},
        "feeding_snack_count": {"name": "Leckerli Anzahl", "initial": 0, "step": 1, "icon": "mdi:food"},
        "feeding_count": {"name": "Fütterungen Gesamt", "initial": 0, "step": 1, "icon": "mdi:food"},
        
        # Lifetime counters
        "total_walks": {"name": "Spaziergänge Gesamt", "initial": 0, "step": 1, "icon": "mdi:counter"},
        "vet_visits_count": {"name": "Tierarztbesuche", "initial": 0, "step": 1, "icon": "mdi:stethoscope"},
        "emergency_calls": {"name": "Notfälle", "initial": 0, "step": 1, "icon": "mdi:alert"}
    }
}