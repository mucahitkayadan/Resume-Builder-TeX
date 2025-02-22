class LLMError(Exception):
    """Base exception class for LLM-related errors."""

    pass


class APIError(LLMError):
    """Raised when an API request fails."""

    pass


class ConfigurationError(LLMError):
    """Raised when there's a configuration issue."""

    pass


class ResponseError(LLMError):
    """Raised when there's an issue with the API response."""

    pass
