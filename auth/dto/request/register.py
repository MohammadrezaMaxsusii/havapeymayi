from dataclasses import dataclass
from pydantic import BaseModel


class RegisterDto(BaseModel):
    name: str
    username: str
    password: str
