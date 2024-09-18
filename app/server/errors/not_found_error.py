from typing import List

from .custom_error import CustomError
from .error_message import ErrorMessage


class NotFoundError(CustomError):
    """Not Found error."""

    def __init__(self, message: str) -> None:
        super().__init__(message, 404)

    def serialize_error(self) -> List[ErrorMessage]:
        return [ErrorMessage(message=self.message)]
