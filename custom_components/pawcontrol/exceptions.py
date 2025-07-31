"""Custom exceptions for Paw Control."""
from homeassistant.exceptions import HomeAssistantError


class PawControlError(HomeAssistantError):
    """Base exception for Paw Control."""


class InvalidDogName(PawControlError):
    """Exception for invalid dog names."""


class GPSError(PawControlError):
    """Base exception for GPS-related errors."""


class GPSProviderError(GPSError):
    """Exception for GPS provider errors."""


class GPSAccuracyError(GPSError):
    """Exception for GPS accuracy issues."""


class InvalidCoordinates(GPSError):
    """Exception for invalid GPS coordinates."""


class GeofenceError(PawControlError):
    """Exception for geofence-related errors."""


class EntityCreationError(PawControlError):
    """Exception for entity creation failures."""


class ServiceCallError(PawControlError):
    """Exception for service call failures."""


class BackupError(PawControlError):
    """Exception for backup/restore operations."""


class DataValidationError(PawControlError):
    """Exception for data validation failures."""


class ConfigurationError(PawControlError):
    """Exception for configuration issues."""


class HealthMonitoringError(PawControlError):
    """Exception for health monitoring issues."""


class WalkTrackingError(PawControlError):
    """Exception for walk tracking issues."""