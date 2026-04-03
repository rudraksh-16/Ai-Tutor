"""Common exception definitions for the AI Tutor application.

Following Rule 469 of CODING_REGULATIONS.md: 
Standardizing on raising specific, named exceptions instead of returning error codes.
"""

from fastapi import status


class BaseAppError(Exception):
    """Base class for all application-specific exceptions."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str, details: dict = None, status_code: int = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        if status_code:
            self.status_code = status_code


class EntityNotFoundError(BaseAppError):
    """Raised when a requested database entity (topic, chapter, etc.) does not exist."""

    status_code = status.HTTP_404_NOT_FOUND


class AlreadyExistsError(BaseAppError):
    """Raised when an entity already exists (e.g., duplicate topic title)."""

    status_code = status.HTTP_400_BAD_REQUEST


class ValidationError(BaseAppError):
    """Raised when input data fails validation checks."""

    status_code = status.HTTP_400_BAD_REQUEST


class LLMToolError(BaseAppError):
    """Raised when an internal LLM tool fails or provides invalid output."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class DatabaseError(BaseAppError):
    """Raised when a database transaction or operation fails."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
