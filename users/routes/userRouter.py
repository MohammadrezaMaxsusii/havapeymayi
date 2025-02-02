from fastapi import APIRouter, HTTPException , Request, Depends
from auth.dto.request.login import LoginDto
from auth.dto.request.register import RegisterDto
from auth.functions.create_token import create_access_token
from auth.functions.hash_user_password import hash_password
from shared.dto.response.api_responseDto import SuccessResponseDto
# from users.repository import UserRepository
from auth.functions.verify_user_password import verify_password
from users.dto.createUser import CreateUserDto
from db.database import conn as DbConnection
from db.database import dbData
from shared.functions.uid_generator import generate_uid
from shared.functions.uid_generator import generate_password
from shared.functions.sendSMS import sendSMS 
from shared.functions.sendSMS import smsTemplate
from users.functions.userInfo import get_oauth_token
from users.functions.userInfo import get_user_info
from users.functions.userInfo import find_user_by_national_code
router = APIRouter()
# userRepo = UserRepository()
from db.database import create_ssha_password
from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_REPLACE ,MODIFY_ADD
import hashlib
import base64
import jwt 
from pydantic import BaseModel
from starlette.responses import RedirectResponse
import configparser
import requests
import urllib.parse
import jwt
config = configparser.ConfigParser()

config.read("config.ini")
OAUTH_URL = config.get("mycao", "OAUTH_URL")
CLIENT_ID = config.get("mycao", "CLIENT_ID")
CLIENT_SECRET = config.get("mycao", "CLIENT_SECRET")
REDIRECT_URI = config.get("mycao", "REDIRECT_URI")
SSO_LOGIN_URL = config.get("mycao", "SSO_LOGIN_URL")
USER_INFO_URL = config.get("mycao", "USER_INFO_URL")
@router.get("/sso_login")
def login_redirect():
    login_url = (f"{SSO_LOGIN_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=openid profile&response_type=code&claims="+'{"id_token":{"phone_number":null}}"')
    # login_url = REDIRECT_URI
    result = RedirectResponse(login_url , status_code=302)

    return RedirectResponse(login_url , status_code=302)

@router.get("/sso_redirect")
def redirect(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "No code provided"}
    token_url = f"{OAUTH_URL}/api/v1/oauth/token?grant_type=authorization_code&code={code}&redirect_uri={REDIRECT_URI}&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}"


   
    token_response = requests.post(
        token_url,
            # data={
            #     "grant_type": "authorization_code",
            #     "code": code,
            #     "redirect_uri": REDIRECT_URI,
            #     "client_id": CLIENT_ID,
            #     "client_secret": CLIENT_SECRET,
            # },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
       
        )


    token_data = token_response.json()
    # print(token_data)
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
    print(userinfo_response.json())
    national_code = userinfo.get("preferred_username")
    
    if not national_code:
        return {"error": "No national_code found in userinfo"}

    # بررسی کاربر در دیتابیس
    return{
            "data": phone_number,
            "message": "کاربر با موفقیت ایجاد شد"
}
@router.post("/create", response_model=SuccessResponseDto)
def createUser(data: CreateUserDto):

    this_uid = generate_uid()
    this_password = generate_password()
    search_filter=f"(&(objectClass=person)(|(uid={this_uid})(telephoneNumber={data.phoneNumber})))"  
    search = DbConnection.search(dbData.get('BASE_DN'), search_filter, SUBTREE, attributes=['cn', 'uid',  'telephoneNumber'])  

    if  search:
        raise HTTPException(400, detail="نام کاربری تکراری است")
    else:
        user_dn = f"uid={this_uid},ou=users,{dbData.get('BASE_DN')}"
        user_attributes = {
            "objectClass": ["inetOrgPerson", "posixAccount", "top"],
            "cn": data.name,
            "sn": data.lastName,
            "uid":this_uid,
            "userPassword": create_ssha_password(this_password),
            "telephoneNumber" : data.phoneNumber,
            "uidNumber": str(this_uid),  
            "gidNumber": "500",  
            "homeDirectory": f"/home/{this_uid}",
        }
        DbConnection.add(user_dn, attributes=user_attributes)
        group_dn = f"cn=netUsers,ou=users,{dbData.get('BASE_DN')}"
        DbConnection.modify(group_dn ,{'memberUid': [(MODIFY_ADD, [this_uid])]})
        sendSMS(data.phoneNumber,smsTemplate(this_uid,this_password))


        return{
            "data": True,
            "message": "کاربر با موفقیت ایجاد شد"
        }
    


# @router.post("/forgaetPassword", response_model=SuccessResponseDto)
# def forgetPassword(username: str):
#     search_filter=f"(&(objectClass=person)(|(uid={username})))"
#     search = DbConnection.search(dbData.get('BASE_DN'), search_filter, SUBTREE, attributes=['cn', 'uid',  'telephoneNumber'])  

#     if  search:
        


    # if user is None:
    #     raise HTTPException(400, detail="نام کاربری یا رمز عبور اشتباه است")

    # if verify_password(data.password, user["password"]) is False:
    #     raise HTTPException(400, detail="نام کاربری یا رمز عبور اشتباه است")

    # token = create_access_token({"id": user["id"], "username": user["username"]})

    # del user["password"]




    # search_filter=f"(&(objectClass=person)(uid=0001))"  # AND filter

    # search = DbConnection.search(dbData.get('BASE_DN'), search_filter, SUBTREE, attributes=['cn', 'uid',  'telephoneNumber']),   
    # if search:
    #     # Iterate through the results
    #     print("Found matching entries:")
    #     for entry in DbConnection.entries:
    #         # Print the DN (Distinguished Name) and the attributes you requested
    #         print(f"DN: {entry.entry_dn}")
    #         print(f"CN: {entry.cn}")
    #         print(f"UID: {entry.uid}")
    #         print("---")
    # else:
    #     print("Search failed or no entries found.")

    return {
        "data": True,
        "message": "ورود با موفقیت انجام شد",
    }


# @router.post("/register", response_model=SuccessResponseDto)
# def register(data: RegisterDto):
#     user = userRepo.findByUsername(data.username)

#     if user:
#         raise HTTPException(400, detail="نام کاربری تکراری است")

#     if len(data.password) < 4:
#         raise HTTPException(400, detail="رمز عبور باید حداقل 4 کاراکتر باشد")

#     data.password = hash_password(data.password)

#     user = userRepo.createOne(data)

#     del user["password"]

#     return {
#         "data": user,
#         "message": "ثبت نام با موفقیت انجام شد",
#     }
