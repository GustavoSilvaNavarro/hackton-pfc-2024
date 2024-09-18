from abc import ABC, abstractmethod
from typing import List

from .error_message import ErrorMessage


class CustomError(ABC, Exception):
    """Custom errors."""

    message: str
    status_code: int

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    @abstractmethod
    def serialize_error(self) -> List[ErrorMessage]:
        """Serialize different type of errors."""
        raise NotImplementedError("Implement method")
