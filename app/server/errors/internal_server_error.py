from typing import List, Optional

from .custom_error import CustomError
from .error_message import ErrorMessage


class InternalServerError(CustomError):
    """Internal Server Error."""

    details: Optional[str]

    def __init__(self, message: str, status_code=500, details: Optional[str] = None) -> None:
        super().__init__(message, status_code)
        self.details = details

    def serialize_error(self) -> List[ErrorMessage]:
        return [ErrorMessage(message=self.message, field=self.details)]
