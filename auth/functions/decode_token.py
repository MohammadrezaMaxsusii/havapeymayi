import jwt
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

JWT_SECRET = config.get("jwt", "JWT_SECRET")

JWT_ALGORITHM = config.get("jwt", "JWT_ALGORITHM")


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception as e:
        return None
