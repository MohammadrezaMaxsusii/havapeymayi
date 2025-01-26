from dataclasses import dataclass
from pydantic import BaseModel


@dataclass(frozen=True)
class LoginDto(BaseModel):
    username: str
    password: str
