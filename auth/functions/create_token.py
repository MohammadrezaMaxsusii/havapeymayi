import jwt
from datetime import datetime, timedelta
from typing import Optional
import configparser


config = configparser.ConfigParser()
config.read("config.ini")

JWT_SECRET = config.get("jwt", "JWT_SECRET")

JWT_ALGORITHM = config.get("jwt", "JWT_ALGORITHM")

JWT_ACCESS_TOKEN_EXPIRE_IN_SECONDS = config.get(
    "jwt", "JWT_ACCESS_TOKEN_EXPIRE_IN_SECONDS"
)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        seconds=int(JWT_ACCESS_TOKEN_EXPIRE_IN_SECONDS)
    )

    to_encode.update({"exp": expire})

    acess_token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return acess_token
