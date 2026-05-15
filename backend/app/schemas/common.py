from typing import Any

from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: str | None = None


class MessageResponse(BaseModel):
    message: str


class GenericResponse(BaseModel):
    data: Any
