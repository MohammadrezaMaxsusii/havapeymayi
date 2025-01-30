from dataclasses import dataclass
from pydantic import BaseModel


@dataclass(frozen=True)
class CreateUserDto(BaseModel):
    name: str
    lastName: str
    phoneNumber: str
