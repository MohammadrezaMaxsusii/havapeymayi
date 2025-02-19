from fastapi import APIRouter, HTTPException

from auth.dto.request.login import LoginDto
from auth.functions.create_token import create_access_token
from shared.dto.response.api_responseDto import SuccessResponseDto
from shared.functions.shareConfFile import getConfigFile


router = APIRouter()


@router.post("/login", response_model=SuccessResponseDto)
def login(data: LoginDto):
    admin_username = getConfigFile("admin_user", "USERNAME")
    admin_password = getConfigFile("admin_user", "PASSWORD")

    if data.username != admin_username or data.password != admin_password:
        # raise HTTPException(400, detail="نام کاربری یا رمز عبور اشتباه است")
        # مستند : نام کاربری یا رمز عبور برای دریافت توکن اشتباه میباشد
        raise HTTPException(400, detail="E1")
    

    token = create_access_token({"role": admin_username})

    return {
        "data": {
            "token": token,
        },
        "message": "توکن ارسال شد",
    }
