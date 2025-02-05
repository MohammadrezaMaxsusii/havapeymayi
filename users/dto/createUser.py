from dataclasses import dataclass
from pydantic import BaseModel


@dataclass(frozen=True)
class CreateUserDto(BaseModel):
    phoneNumber: str
@dataclass(frozen=True)
class SendOTPDto(BaseModel):
    phoneNumber: str
    username : str
@dataclass(frozen=True)
class ForgetPasswordDto(BaseModel):
    otp:str