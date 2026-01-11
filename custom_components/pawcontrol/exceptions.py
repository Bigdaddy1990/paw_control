"""Exceptions for Paw Control integration."""


class PawControlError(Exception):
    """Base exception for Paw Control."""


class InvalidCoordinates(PawControlError):
    """Exception for invalid GPS coordinates."""


class DataValidationError(PawControlError):
    """Exception for data validation errors."""


class EntityCreationError(PawControlError):
    """Exception for entity creation errors."""


class ServiceCallError(PawControlError):
    """Exception for service call errors."""
