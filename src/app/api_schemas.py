from typing import Generic, Literal, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessOut(BaseModel, Generic[T]):
    status: Literal["success"] = "success"
    data: T


class ErrorOut(BaseModel):
    status: Literal["error"] = "error"
    code: str
    message: str
