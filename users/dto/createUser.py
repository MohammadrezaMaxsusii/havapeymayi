from dataclasses import dataclass
from pydantic import BaseModel


@dataclass(frozen=True)
class CreateUserDto(BaseModel):
    phoneNumber: str
