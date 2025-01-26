from fastapi import APIRouter, HTTPException
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
from shared.functions.sendSMS import sendSMS 
from shared.functions.sendSMS import smsTemplate
router = APIRouter()
# userRepo = UserRepository()
from db.database import create_ssha_password
from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_REPLACE
import hashlib
import base64
@router.post("/create", response_model=SuccessResponseDto)
def createUser(data: CreateUserDto):

    this_uid = generate_uid()
    search_filter=f"(&(objectClass=person)(|(uid={this_uid})(telephoneNumber={data.phoneNumber})))"  

    search = DbConnection.search(dbData.get('BASE_DN'), search_filter, SUBTREE, attributes=['cn', 'uid',  'telephoneNumber'])  

    # for entry in search:
    #     print(entry['telephoneNumber'])
    if  search:
        raise HTTPException(400, detail="نام کاربری تکراری است")
    else:
        user_dn = f"uid={this_uid},ou=users,{dbData.get('BASE_DN')}"
        user_attributes = {
            "objectClass": ["inetOrgPerson", "posixAccount", "top"],
            "cn": data.name,
            "sn": data.lastName,
            "uid":this_uid,
            "userPassword": create_ssha_password(data.password),
            "telephoneNumber" : data.phoneNumber,
            "uidNumber": "1000",  # Use a unique number for each user
            "gidNumber": "1000",  # Group ID (default group)
            "homeDirectory": f"/home/{this_uid}",
        }
        sendSMS(data.phoneNumber,smsTemplate(this_uid,data.password))
        DbConnection.add(user_dn, attributes=user_attributes)
        
        return{
            "data": True,
            "message": "کاربر با موفقیت ایجاد شد"
        }


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
