import jwt
from shared.functions.shareConfFile import getConfigFile


JWT_SECRET = getConfigFile("jwt", "JWT_SECRET")

JWT_ALGORITHM = getConfigFile("jwt", "JWT_ALGORITHM")


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception as e:
        return None
