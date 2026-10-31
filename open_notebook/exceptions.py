class DocIntelError(Exception):
    """Base exception class for DocIntel errors."""

    pass


class DatabaseOperationError(DocIntelError):
    """Raised when a database operation fails."""

    pass


class UnsupportedTypeException(DocIntelError):
    """Raised when an unsupported type is provided."""

    pass


class InvalidInputError(DocIntelError):
    """Raised when invalid input is provided."""

    pass


class NotFoundError(DocIntelError):
    """Raised when a requested resource is not found."""

    pass


class AuthenticationError(DocIntelError):
    """Raised when there's an authentication problem."""

    pass


class ConfigurationError(DocIntelError):
    """Raised when there's a configuration problem."""

    pass


class ExternalServiceError(DocIntelError):
    """Raised when an external service (e.g., AI model) fails."""

    pass


class IncompleteGenerationError(ExternalServiceError):
    """The model returned truncated or empty output; do not retry automatically."""

    pass


class ContextLengthExceededError(ExternalServiceError):
    """Content exceeds the model's context window. Retrying sends the same
    oversized payload, so background commands must not retry this."""

    pass


class RateLimitError(DocIntelError):
    """Raised when a rate limit is exceeded."""

    pass


class FileOperationError(DocIntelError):
    """Raised when a file operation fails."""

    pass


class NetworkError(DocIntelError):
    """Raised when a network operation fails."""

    pass


class NoTranscriptFound(DocIntelError):
    """Raised when no transcript is found for a video."""

    pass
