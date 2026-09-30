from typing import Any


class ApplicationError(Exception):
    status_code = 500
    error_code = "application_error"
    default_message = "An application error occurred."

    def __init__(self, message: str | None = None, details: Any = None) -> None:
        self.message = message or self.default_message
        self.details = details
        super().__init__(self.message)