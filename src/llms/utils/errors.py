class LLMError(Exception):
    """Base exception class for LLM-related errors."""


class APIError(LLMError):
    """Raised when an API request fails."""


class ConfigurationError(LLMError):
    """Raised when there's a configuration issue."""


class ResponseError(LLMError):
    """Raised when there's an issue with the API response."""
