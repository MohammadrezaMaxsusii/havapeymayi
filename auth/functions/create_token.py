import jwt
from datetime import datetime, timedelta

from shared.functions.shareConfFile import getConfigFile

JWT_SECRET = getConfigFile("jwt", "JWT_SECRET")

JWT_ALGORITHM = getConfigFile("jwt", "JWT_ALGORITHM")

JWT_ACCESS_TOKEN_EXPIRE_IN_SECONDS = getConfigFile(
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
