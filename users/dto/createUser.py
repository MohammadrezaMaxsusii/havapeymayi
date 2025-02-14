from dataclasses import dataclass
from pydantic import BaseModel


@dataclass(frozen=True)
class CreateUserDto(BaseModel):
    id: str
    expDate: int
    groupName: str
    phoneNumber: str


@dataclass(frozen=True)
class SendOTPDto(BaseModel):
    phoneNumber: str
    username: str


@dataclass(frozen=True)
class ForgetPasswordDto(BaseModel):
    otp: str
    phoneNumber: str


@dataclass(frozen=True)
class captchaDto(BaseModel):
    captchaId: str
    captchaText: str


@dataclass(frozen=True)
class updateUserDto(BaseModel):
    id: str
    expDate: int
    groupName: str
    phoneNumber: str


@dataclass(frozen=True)
class deleteUserDto(BaseModel):
    id: str


@dataclass(frozen=True)
class userListDto(BaseModel):
    groupName: str
