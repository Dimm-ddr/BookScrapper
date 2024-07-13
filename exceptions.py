# exceptions.py


class NotionAPIError(Exception):
    """Base exception for Notion API related errors."""

    pass


class NotionResponseTypeError(NotionAPIError, TypeError):
    """Raised when the response from Notion API is not of the expected type."""

    def __init__(self, response: object, extra_data: str | None = None) -> None:
        super().__init__(
            f"Unexpected response type from Notion API: {response!r}{extra_data}"
        )


class NotionResponseValueError(NotionAPIError, ValueError):
    """Raised when the response from Notion API has an unexpected value."""

    def __init__(self, message: object, extra_data: str | None = None) -> None:
        super().__init__(f"Invalid response from Notion API: {message!r}{extra_data}")


class NotionOperationError(NotionAPIError):
    """Raised when a Notion operation fails."""

    pass
