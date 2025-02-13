from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.functions.decode_token import decode_access_token
from shared.functions.shareConfFile import getConfigFile

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

admin_username = getConfigFile("admin_user", "USERNAME")


async def user_is_admin_or_error(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    if payload.get("username") != admin_username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permission",
        )
    return payload
