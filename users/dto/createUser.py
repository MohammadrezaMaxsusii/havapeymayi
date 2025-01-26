from dataclasses import dataclass
from pydantic import BaseModel


@dataclass(frozen=True)
class CreateUserDto(BaseModel):
    username: str
    password: str
    name: str
    lastName: str
    phoneNumber: str
