from fastapi import APIRouter, HTTPException, Request
from shared.dto.response.api_responseDto import SuccessResponseDto
from shared.functions.generate_otp import generate_otp
from shared.functions.convert_phoneNumbser import ensure_phone_number
from redis_handler.redis import *
from users.dto.createUser import CreateUserDto, SendOTPDto, ForgetPasswordDto
from db.database import conn as DbConnection
from db.database import dbData
from shared.functions.uid_generator import generate_uid
from shared.functions.uid_generator import generate_password
from shared.functions.sendSMS import sendSMS
from shared.functions.sendSMS import smsTemplate, otpSmsTemplate
from users.functions.userInfo import get_oauth_token
from users.functions.userInfo import get_user_info
from users.functions.userInfo import find_user_by_national_code
from db.database import create_ssha_password
from ldap3 import SUBTREE, MODIFY_ADD
import jwt
from starlette.responses import RedirectResponse
import configparser
import requests
import json
from shared.functions.calculate_remaining_redis_ttl import seconds_until_midnight

config = configparser.ConfigParser()
router = APIRouter()

#----------------------- SSO CONFIG -----------------------
config.read("config.ini")
OAUTH_URL = config.get("mycao", "OAUTH_URL")
CLIENT_ID = config.get("mycao", "CLIENT_ID")
CLIENT_SECRET = config.get("mycao", "CLIENT_SECRET")
REDIRECT_URI = config.get("mycao", "REDIRECT_URI")
SSO_LOGIN_URL = config.get("mycao", "SSO_LOGIN_URL")
USER_INFO_URL = config.get("mycao", "USER_INFO_URL")

#----------------------- REDIS PREFIX KEYS -----------------------
CREATE_USER_REQUEST_LIMIT_KEY_PREFIX = "CREATE_USER_REQUEST_LIMIT_KEY:"
GUEST_USER_EXISTS_KEY_PREFIX = "GUEST_USER_EXISTS_KEY:"
GET_USER_INFO_KEY_PREFIX = "GET_USER_INFO_KEY:"
OTP_PREFIX = "OTP_KEY:"

@router.get("/sso_login")
def login_redirect():
    login_url = (f"{SSO_LOGIN_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=openid profile&response_type=code&claims="+'{"id_token":{"phone_number":null}}"')
    return RedirectResponse(login_url , status_code=302)

@router.get("/sso_redirect")
def redirect(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "No code provided"}
    token_url = f"{OAUTH_URL}/api/v1/oauth/token?grant_type=authorization_code&code={code}&redirect_uri={REDIRECT_URI}&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}"


   
    token_response = requests.post(
        token_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        )


    token_data = token_response.json()
    if "access_token" not in token_data:
        return {"error": "Failed to get access token"}

    access_token = token_data.get("access_token")
   
    id_token = token_data.get("id_token")
    decodedTokenId = jwt.decode(id_token, options={"verify_signature": False})
    
    if decodedTokenId.get("aud") == CLIENT_ID:
        phone_number = decodedTokenId.get("phone_number")
    else :
        return

    userinfo_response = requests.get(
        USER_INFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        verify=False
    )
    userinfo = userinfo_response.json()

    redis_set_value(GET_USER_INFO_KEY_PREFIX + phone_number, json.dumps({
        "first_name": userinfo.get("given_name"),
        "last_name": userinfo.get("family_name"),
    }), 60*30)
    
    national_code = userinfo.get("preferred_username")
    
    if not national_code:
        raise HTTPException (404, 'کد ملی یافت نشد')

    return RedirectResponse("http://localhost:5173" , 302)


@router.post("/create", response_model=SuccessResponseDto)
def createUser(data: CreateUserDto):

    REQUEST_LIMIT_KEY = CREATE_USER_REQUEST_LIMIT_KEY_PREFIX + data.phoneNumber
    GUEST_USER_EXISTS_KEY = GUEST_USER_EXISTS_KEY_PREFIX + data.phoneNumber
    GET_USER_INFO_KEY = GET_USER_INFO_KEY_PREFIX + data.phoneNumber
    
    try :
        user_info_from_sso = json.loads(redis_get_value(GET_USER_INFO_KEY)['value'])

    except:
        raise HTTPException(404, detail="شماره تلفن وارد شده تطابق ندارد")

    if redis_get_value(REQUEST_LIMIT_KEY)["status"]:
        raise HTTPException(429, detail="لطفا کمی صبر کنید")
    else:
        redis_set_value(REQUEST_LIMIT_KEY, 1 , 5)

    this_uid = generate_uid()
    this_password = generate_password()
    this_phoneNumber = ensure_phone_number(data.phoneNumber)

    search_filter = f"(&(objectClass=person)(|(uid={this_uid})(telephoneNumber={this_phoneNumber})))"

    search = DbConnection.search(
        dbData.get("BASE_DN"),
        search_filter,
        SUBTREE,
        attributes=["cn", "uid", "telephoneNumber"],
    )   

    if search and redis_get_value(GUEST_USER_EXISTS_KEY)['status']:
        user_data = redis_get_value(GUEST_USER_EXISTS_KEY)['value']
        user_data = json.loads(user_data)
        sendSMS(this_phoneNumber, smsTemplate(user_data.get('username'), user_data.get('password')))
    else:
        user_info_from_sso = json.loads(redis_get_value(GET_USER_INFO_KEY)['value'])
      

        user_dn = f"uid={this_uid},ou=users,{dbData.get('BASE_DN')}"
        user_attributes = {
            "objectClass": ["inetOrgPerson", "posixAccount", "top"],
            "cn": this_uid, 
            "sn": user_info_from_sso.get("last_name") +" "+ user_info_from_sso.get("first_name"), 
            "uid": this_uid,
            "userPassword": create_ssha_password(this_password),
            "telephoneNumber": this_phoneNumber,
            "uidNumber": str(this_uid),
            "gidNumber": "500",
            "homeDirectory": f"/home/{this_uid}",
        }
        DbConnection.add(user_dn, attributes=user_attributes)
        group_dn = f"cn=netUsers,ou=users,{dbData.get('BASE_DN')}"
        DbConnection.modify(group_dn, {"memberUid": [(MODIFY_ADD, [this_uid])]})
        redis_set_value(GUEST_USER_EXISTS_KEY, json.dumps({"username": this_uid, "password": this_password}), seconds_until_midnight())
        sendSMS(this_phoneNumber, smsTemplate(this_uid, this_password))
        return {"data": True, "message": "کاربر با موفقیت ایجاد شد"}

@router.post("/sendOTP", response_model=SuccessResponseDto)
def sendOTP(data: SendOTPDto):
    OTP_KEY = OTP_PREFIX + data.phoneNumber

    if redis_get_value(OTP_KEY)['status']:
        raise HTTPException(400, "لطفا برای درخواست مجدد کد یکبار مصرف کمی صبر کنید")
    
    search_filter = f"(&(objectClass=person)(|(uid={data.username})(telephoneNumber={data.phoneNumber})))"
    search = DbConnection.search(
        dbData.get("BASE_DN"),
        search_filter,
        SUBTREE,
        attributes=["cn", "uid", "telephoneNumber"],
    )   
    # if not "caa" in data.username:
    #     raise HTTPException (404 , "مشخصات شما به عنوان کارمند تعریف نشده است")
    if  not search:
        raise HTTPException (404 , "مشخصات شما به عنوان کارمند تعریف نشده است")

    this_otp = generate_otp()
    
    redis_set_value(OTP_KEY, this_otp, 120)
    sendSMS(data.phoneNumber, otpSmsTemplate(this_otp))
    
    return {
        "message": "کد یکبار مصرف برای شما ارسال شد",
        "data": True
    }
    
@router.post("/forgetPassword", response_model=SuccessResponseDto)
def sendOTP(data: ForgetPasswordDto):
    OTP_KEY = OTP_PREFIX + data.phoneNumber

    if redis_get_value(OTP_KEY)['status']:
        raise HTTPException(400, "لطفا برای درخواست مجدد کد یکبار مصرف کمی صبر کنید")
    
    search_filter = f"(&(objectClass=person)(|(uid={data.username})(telephoneNumber={data.phoneNumber})))"
    search = DbConnection.search(
        dbData.get("BASE_DN"),
        search_filter,
        SUBTREE,
        attributes=["cn", "uid", "telephoneNumber"],
    )
    
    if not "caa" in data.username:
        raise HTTPException (404 , "مشخصات شما به عنوان کارمند تعریف نشده است")
    
    if  not search:
        raise HTTPException (404 , "مشخصات شما به عنوان کارمند تعریف نشده است")

    this_otp = generate_otp()
    
    redis_set_value(OTP_KEY, this_otp, 120)
    sendSMS(data.phoneNumber, otpSmsTemplate(this_otp))
    
    return {
        "message": "کد یکبار مصرف برای شما ارسال شد",
        "data": True
    }
    
