from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from shared.auth.user_is_admin_or_error import user_is_admin_or_error
from shared.dto.response.api_responseDto import SuccessResponseDto
from shared.functions.generate_otp import generate_otp
from shared.functions.convert_phoneNumbser import ensure_phone_number
from redis_handler.redis import *
from users.dto.createUser import (
    CreateUserDto,
    SendOTPDto,
    ForgetPasswordDto,
    captchaDto,
    deleteUserDto,
    updateUserDto,
    userListDto,
)
from db.database import conn as DbConnection
from db.database import dbData
from shared.functions.uid_generator import generate_uid
from shared.functions.uid_generator import generate_password
from shared.functions.sendSMS import sendSMS
from shared.functions.sendSMS import smsTemplate, otpSmsTemplate
from users.functions.expiration_handler import (
    add_user_to_redis_sessions,
    get_user_session_key,
    remove_user_from_redis_sessions,
)
from users.functions.get_groups_of_user import get_group_of_user
from users.functions.userInfo import get_oauth_token
from users.functions.userInfo import get_user_info
from users.functions.userInfo import find_user_by_national_code
from db.database import create_ssha_password
from ldap3 import SUBTREE, MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE
import jwt
from starlette.responses import RedirectResponse
import configparser
import requests
import json
import uuid
from shared.functions.calculate_remaining_redis_ttl import seconds_until_midnight
from shared.functions.capchaGenerator import (
    generate_captcha_text,
    generate_captcha_image,
)
from users.functions.userInfo import add_user_to_group, add_user, update_cn
from shared.functions.getDNs import getUserDN, getGroupDN

config = configparser.ConfigParser()
router = APIRouter()

# ----------------------- SSO CONFIG -----------------------
config.read("config.ini")
# OAUTH_URL = config.get("mycao", "OAUTH_URL")
# CLIENT_ID = config.get("mycao", "CLIENT_ID")
# CLIENT_SECRET = config.get("mycao", "CLIENT_SECRET")
# # REDIRECT_URI = config.get("mycao", "REDIRECT_URI")
# # SSO_LOGIN_URL = config.get("mycao", "SSO_LOGIN_URL")
# USER_INFO_URL = config.get("mycao", "USER_INFO_URL")
# ----------------------- REDIS PREFIX KEYS -----------------------
CREATE_USER_REQUEST_LIMIT_KEY_PREFIX = "CREATE_USER_REQUEST_LIMIT_KEY:"
GUEST_USER_EXISTS_KEY_PREFIX = "GUEST_USER_EXISTS_KEY:"
GET_USER_INFO_KEY_PREFIX = "GET_USER_INFO_KEY:"
OTP_PREFIX = "OTP_KEY:"
EACH_USER_SESSION_EXP_KEY = "USER_EXP:"


# @router.get("/sso_login")
# def login_redirect():
#     login_url = (
#         f"{SSO_LOGIN_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=openid profile&response_type=code&claims="
#         + '{"id_token":{"phone_number":null}}"'
#     )
#     return RedirectResponse(login_url, status_code=302)


# @router.get("/sso_redirect")
# def redirect(request: Request):
#     code = request.query_params.get("code")
#     if not code:
#         return {"error": "No code provided"}
#     token_url = f"{OAUTH_URL}/api/v1/oauth/token?grant_type=authorization_code&code={code}&redirect_uri={REDIRECT_URI}&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}"

#     token_response = requests.post(
#         token_url,
#         headers={"Content-Type": "application/x-www-form-urlencoded"},
#     )

#     token_data = token_response.json()
#     if "access_token" not in token_data:
#         return {"error": "Failed to get access token"}

#     access_token = token_data.get("access_token")

#     id_token = token_data.get("id_token")
#     decodedTokenId = jwt.decode(id_token, options={"verify_signature": False})

#     if decodedTokenId.get("aud") == CLIENT_ID:
#         phone_number = decodedTokenId.get("phone_number")
#     else:
#         return

#     userinfo_response = requests.get(
#         USER_INFO_URL, headers={"Authorization": f"Bearer {access_token}"}, verify=False
#     )
#     userinfo = userinfo_response.json()

#     redis_set_value(
#         GET_USER_INFO_KEY_PREFIX + phone_number,
#         json.dumps(
#             {
#                 "first_name": userinfo.get("given_name"),
#                 "last_name": userinfo.get("family_name"),
#             }
#         ),
#         60 * 30,
#     )

#     national_code = userinfo.get("preferred_username")

#     if not national_code:
#         raise HTTPException(404, "کد ملی یافت نشد")

#     return RedirectResponse("http://localhost:5173", 302)


@router.post("/create", response_model=SuccessResponseDto)
def createUser(data: CreateUserDto, payload: dict = Depends(user_is_admin_or_error)):
    # 1 ساخت یوزر در ldap

    #     #1.1 بررسی داپلیکت کاربر
    search_filter = f"(&(objectClass=person)(|(uid={data.id})))"
    search = DbConnection.search(
        dbData.get("BASE_DN"),
        search_filter,
        SUBTREE,
        attributes=["uid"],
    )
    if search:
        raise HTTPException(400, "E2")
    #مستند : کاربری با این مشخصات قبلا ثبت شده است 
        # raise HTTPException(400, "کاربری با این مشخصات قبلا ثبت شده است")
    search_filter_template = "(cn={})"
    search_filter = search_filter_template.format(data.groupName)
    search = DbConnection.search(
        dbData.get("BASE_DN"),
        search_filter,
        SUBTREE,
        attributes=["gidNumber"],
    )
    gid_number = DbConnection.entries[0].gidNumber.value
    this_password = generate_password()
    this_uid = generate_uid()
    add_user(
        data.id,
        create_ssha_password(this_password),
        data.groupName,
        gid_number,
        this_uid,
        data.phoneNumber,
    )

    # 2 ذخیره کاربر در reddis
    if data.expDate < 1 or data.expDate > 365:
        raise HTTPException(400, "E3")
    #"زمان انقضا باید بین 1 تا 365 باشد" مستند :

    EXP_KEY = get_user_session_key(data.id)
    redis_set_value(EXP_KEY, data.expDate , data.expDate * 60 * 60 * 24)
    add_user_to_redis_sessions(EXP_KEY)
    # 3 ارسال پیامک به کاربر
    try:
        sendSMS(data.phoneNumber, smsTemplate(data.id, this_password))
    except:
        raise HTTPException(400, "E4")
    #  در  ساخت یوزر مستند : عدم توانایی در ارسال اس ام اس
    return {"data": True,
            "message": "کاربر با موفقیت ایجاد شد"
            }


    # try:
    #     user_info_from_sso = json.loads(redis_get_value(GET_USER_INFO_KEY)["value"])

    # except:
    #     raise HTTPException(404, detail="شماره تلفن وارد شده تطابق ندارد")

    # if redis_get_value(REQUEST_LIMIT_KEY)["status"]:
    #     raise HTTPException(429, detail="لطفا کمی صبر کنید")
    # else:
    #     redis_set_value(REQUEST_LIMIT_KEY, 1, 5)

    # this_uid = generate_uid()
    # this_password = generate_password()
    # this_phoneNumber = ensure_phone_number(data.phoneNumber)

    # search_filter = f"(&(objectClass=person)(|(uid={this_uid})(telephoneNumber={this_phoneNumber})))"

    # search = DbConnection.search(
    #     dbData.get("BASE_DN"),
    #     search_filter,
    #     SUBTREE,
    #     attributes=["cn", "uid", "telephoneNumber"],
    # )

    # if search and redis_get_value(GUEST_USER_EXISTS_KEY)["status"]:
    #     user_data = redis_get_value(GUEST_USER_EXISTS_KEY)["value"]
    #     user_data = json.loads(user_data)
    #     sendSMS(
    #         this_phoneNumber,
    #         smsTemplate(user_data.get("username"), user_data.get("password")),
    #     )
    # else:
    #     user_info_from_sso = json.loads(redis_get_value(GET_USER_INFO_KEY)["value"])

    #     user_dn = f"uid={this_uid},ou=users,{dbData.get('BASE_DN')}"
    #     user_attributes = {
    #         "objectClass": ["inetOrgPerson", "posixAccount", "top"],
    #         "cn": this_uid,
    #         "sn": user_info_from_sso.get("last_name")
    #         + " "
    #         + user_info_from_sso.get("first_name"),
    #         "uid": this_uid,
    #         "userPassword": create_ssha_password(this_password),
    #         "telephoneNumber": this_phoneNumber,
    #         "uidNumber": str(this_uid),
    #         "gidNumber": "500",
    #         "homeDirectory": f"/home/{this_uid}",
    #     }
    #     DbConnection.add(user_dn, attributes=user_attributes)
    #     group_dn = f"cn=netUsers,ou=users,{dbData.get('BASE_DN')}"
    #     DbConnection.modify(group_dn, {"memberUid": [(MODIFY_ADD, [this_uid])]})
    #     redis_set_value(
    #         GUEST_USER_EXISTS_KEY,
    #         json.dumps({"username": this_uid, "password": this_password}),
    #         seconds_until_midnight(),
    #     )
    #     sendSMS(this_phoneNumber, smsTemplate(this_uid, this_password))
    #     return {"data": True, "message": "کاربر با موفقیت ایجاد شد"}
    # return {"data": True, "message": "کاربر با موفقیت ایجاد شد"}


@router.post("/sendOTP", response_model=SuccessResponseDto)
def sendOTP(data: SendOTPDto):
    OTP_KEY = OTP_PREFIX + data.phoneNumber
    GET_USERNAME_BY_CELLPHONE_KEY = "username_of" + data.phoneNumber + ":"
    if redis_get_value(OTP_KEY)["status"]:
        raise HTTPException(400, "لطفا برای درخواست مجدد کد یکبار مصرف کمی صبر کنید")

    search_filter = f"(&(objectClass=person)(&(uid={data.username})(telephoneNumber={data.phoneNumber})))"
    search = DbConnection.search(
        dbData.get("BASE_DN"),
        search_filter,
        SUBTREE,
        attributes=["cn", "uid", "telephoneNumber"],
    )
    redis_set_value(GET_USERNAME_BY_CELLPHONE_KEY, data.username, 120)
    if not "caa" in data.username:
        raise HTTPException(404, "E5")
    #مستند :"مشخصات شما به عنوان کارمند تعریف نشده است"
    if not search:
        raise HTTPException(404, "E6")
# مستند : "مشخصات شما به عنوان کارمند تعریف نشده است"
    this_otp = generate_otp()

    redis_set_value(OTP_KEY, this_otp, 120)
    try :
        
        sendSMS(data.phoneNumber, otpSmsTemplate(this_otp))
    except:
        raise HTTPException(400, "E4")
    #  در  ساخت یوزر مستند : عدم توانایی در ارسال اس ام اس
        

    return {"message": "کد یکبار مصرف برای شما ارسال شد", "data": True}


# @router.post("/forgetPassword", response_model=SuccessResponseDto)
# def forgetPassword(data: ForgetPasswordDto):
#     OTP_KEY = OTP_PREFIX + data.phoneNumber
#     GET_USERNAME_BY_CELLPHONE_KEY = "username_of" + data.phoneNumber + ":"

#     if not redis_get_value(OTP_KEY)["status"]:
#         raise HTTPException(400, "کد معتبر نیست")
#     this_uid = redis_get_value(GET_USERNAME_BY_CELLPHONE_KEY)["value"]
#     print(this_uid)
#     redis_del_value(OTP_KEY)
#     this_password = generate_password()
#     user_dn = f"uid={this_uid},ou=users,{dbData.get('BASE_DN')}"
#     DbConnection.modify(
#         user_dn,
#         {"userPassword": [(MODIFY_REPLACE, [create_ssha_password(this_password)])]},
#     )
#     sendSMS(data.phoneNumber, smsTemplate(this_uid, this_password))
#     return {"message": "نام کاربری و رمز عبور برای شما ارسال گردید"}


# @router.get("/captcha", response_model=SuccessResponseDto)
# def captcha():
#     captcha_text = generate_captcha_text()
#     captcha_id = str(uuid.uuid4())

#     redis_set_value(f"captcha:{captcha_id}", captcha_text, ttl=300)

#     image_io = generate_captcha_image(captcha_text)

#     headers = {"X-Captcha-Id": captcha_id}
#     return Response(
#         content=image_io.getvalue(), media_type="image/png", headers=headers
#     )


# @router.post("/validate_captcha", response_model=SuccessResponseDto)
# def validate_captcha(data: captchaDto):
#     stored_captcha = redis_get_value(f"captcha:{data.captchaId}")
#     print(stored_captcha)
#     print(data.captchaText)
#     if stored_captcha and stored_captcha["value"] == data.captchaText:
#         # redis_del_value(f"captcha:{data.captchaId}")

#         return {"success": True, "message": "کپچا صحیح است!"}
#     raise HTTPException(status_code=400, detail="کپچا اشتباه است یا منقضی شده!")


# @router.put("/test", response_model=SuccessResponseDto)
# def test():
#     return {"success": True, "message": "کپچا صحیح است!"}


@router.post("/updateUserInfo", response_model=SuccessResponseDto)
def updateUserInfo(
    data: updateUserDto, payload: dict = Depends(user_is_admin_or_error)
):
    # به روز رسانی زمان استفاده کاربر در reddiss mobin
    search_filter_template = "(cn={})"
    search_filter = search_filter_template.format(data.groupName)
    search = DbConnection.search(
        dbData.get("BASE_DN"),
        search_filter,
        SUBTREE,
        attributes=["gidNumber"],
    )
    newGidNumber = DbConnection.entries[0].gidNumber.value
    print(newGidNumber)
    search_filter = f"(uid={data.id})"
    DbConnection.search(
        dbData.get("BASE_DN"),
        search_filter,
        attributes=["telephoneNumber", "cn", "userPassword"],
    )
    if not DbConnection.entries:
        raise HTTPException(status_code=404, detail="E7")
    #مستند "کاربر با این مشخصات یافت نشد"
    user_dn = DbConnection.entries[0].entry_dn
    changes = {}
    if data.phoneNumber:
        changes["telephoneNumber"] = [(MODIFY_REPLACE, [data.phoneNumber])]

    search_filter = f"(memberUid={data.id})"
    DbConnection.search(dbData.get("BASE_DN"), search_filter, attributes=["cn"])
    thisPassword = generate_password()
    changes["userPassword"] = [(MODIFY_REPLACE, [thisPassword])]
    new_group_dn = ""
    for entry in DbConnection.entries:
        old_group_dn = entry.entry_dn
        new_group_dn = update_cn(old_group_dn, data.groupName)

        if DbConnection.modify(
            old_group_dn, {"memberUid": [(MODIFY_DELETE, [data.id])]}
        ):
            user_search_filter = f"(uid={data.id})"
            DbConnection.search(
                dbData.get("BASE_DN"), user_search_filter, attributes=["gidNumber"]
            )
            print(DbConnection.entries)
            if not DbConnection.entries:
                print(f"User '{data.id}' not found!")
            user_dn = DbConnection.entries[0].entry_dn
            print(user_dn)
            if DbConnection.modify(
                user_dn, {"gidNumber": [(MODIFY_REPLACE, [str(newGidNumber)])]}
            ):
                print(
                    f"User '{data.id}' gidNumber changed to '{newGidNumber}' successfully!"
                )

    if DbConnection.modify(new_group_dn, {"memberUid": [(MODIFY_ADD, [data.id])]}):
        print(f"User '{data.id}' moved to group '{new_group_dn}' successfully!")
    if changes:
        DbConnection.modify(user_dn, changes)
        # پس از اتمام از کامنت هارج شود
        # sendSMS(data.phoneNumber, smsTemplate(data.id, thisPassword))
        if DbConnection.result["description"] != "success":
            raise HTTPException(
                status_code=500,
                detail="E8",
            )
            #عدم توانمایی در بروزرسانی اطلاعات کاربر 

    return {"success": True, "message":"اطلاعات کاربر با موفقیت به روز رسانی گردید"}


@router.post("/deleteUser", response_model=SuccessResponseDto)
def deleteUser(data: deleteUserDto, payload: dict = Depends(user_is_admin_or_error)):
    search_filter = f"(&(objectClass=person)(|(uid={data.id})))"
    search = DbConnection.search(
        dbData.get("BASE_DN"),
        search_filter,
        SUBTREE,
        attributes=["uid"],
    )

    if not search:
        raise HTTPException(status_code=404, detail="E7")
    #مستند "کاربر با این مشخصات یافت نشد"

    # now delete user from group
    groupName = get_group_of_user(data.id)

    groupDN = f"cn={groupName},ou=users,{dbData.get('BASE_DN')}"
    changes = {"memberUid": [(MODIFY_DELETE, [data.id])]}
    DbConnection.modify(groupDN, changes)

    # then delete user
    userDN = getUserDN(data.id)
    DbConnection.delete(userDN)

    # handle redis
    EXP_KEY = get_user_session_key(data.id)
    redis_del_value(EXP_KEY)
    remove_user_from_redis_sessions(EXP_KEY)

    return {"data": True, "message": "کاربر با موفقیت حذف شد"}


@router.get("/userList", response_model=SuccessResponseDto)
def userList(data: userListDto, payload: dict = Depends(user_is_admin_or_error)):
    try:
        groupDN = f"cn={data.groupName},ou=users,{dbData.get('BASE_DN')}"
        print(groupDN)
        
        search_filter = f"(cn={data.groupName})"
        DbConnection.search(
            dbData.get("BASE_DN"), 
            search_filter, 
            attributes=["memberUid", "member"]
        )
        
        print(DbConnection.entries)
        if not DbConnection.entries:
            raise HTTPException(status_code=404, detail="E9")
    #مستند "گروه پیدا نشد"
        group_entry = DbConnection.entries[0]
        members = group_entry.entry_attributes_as_dict.get("memberUid") or \
                  group_entry.entry_attributes_as_dict.get("member", [])

        # استفاده از تابع redis_get_value برای دریافت exptime از Redis
        member_details = []
        for member in members:
            redis_response = redis_get_value(f"USER_EXP:{member}")
            member_details.append({
                "user": member,
                "exptime": redis_response.get("value") if redis_response.get("status") and redis_response.get("value") else "زمان به پایان رسیده"
            })
                  
        return {"data": member_details}

    except Exception as e:
        print(f"Error retrieving users: {e}")
        raise HTTPException(status_code=404, detail="E10")
        #مستند : "مشکلی در بازیابی اطلاعات به وجود آمده است"