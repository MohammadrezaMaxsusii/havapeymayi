
import requests
from shared.functions.shareConfFile import getConfigFile
from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_REPLACE , MODIFY_ADD
import hashlib
import base64
DB_HOST = getConfigFile("database", "DB_HOST")

DB_PORT = getConfigFile("database", "DB_PORT")

DB_NAME = getConfigFile("database", "DB_NAME")

DB_USER = getConfigFile("database", "DB_USER")

DB_PASSWORD = getConfigFile("database", "DB_PASSWORD")

OAUTH_URL = getConfigFile("mycao", "OAUTH_URL")
CLIENT_ID = getConfigFile("mycao", "CLIENT_ID")
CLIENT_SECRET = getConfigFile("mycao", "CLIENT_SECRET")
REDIRECT_URI = getConfigFile("mycao", "REDIRECT_URI")
DAP_SERVER = f"ldap://{DB_HOST}:{DB_PORT}"
ADMIN_DN = f"cn=admin,dc={DB_USER},dc=com"
ADMIN_PASSWORD = DB_PASSWORD
BASE_DN = f"dc={DB_USER},dc=com"

LDAP_SERVER = f"ldap://{DB_HOST}:{DB_PORT}"
ADMIN_DN = f"cn=admin,dc={DB_USER},dc=com"
ADMIN_PASSWORD = DB_PASSWORD
BASE_DN = f"dc={DB_USER},dc=com"
server = Server(LDAP_SERVER, get_info=ALL)
conn = Connection(server, ADMIN_DN, ADMIN_PASSWORD, auto_bind=True)


def create_ssha_password(password):
    salt = b"randomsalt"  # Use a random salt in production
    hashed = hashlib.sha1(password.encode("utf-8") + salt).digest()
    return "{SSHA}" + base64.b64encode(hashed + salt).decode("utf-8")
def get_oauth_token(code: str):
    token_url = f"{OAUTH_URL}/api/v1/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(token_url, data=data, headers=headers, verify=True)
    return response.json()

def get_user_info(access_token: str):
    userinfo_url = f"{OAUTH_URL}/api/v1/oauth/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(userinfo_url, headers=headers, verify=True)
    return response.json()

def find_user_by_national_code(national_code: str):

    return {"national_code": national_code, "name": "Test User"}


def add_user(uid,  password,  groupName , groupId , this_uid  , phone):
    print(groupName)
    group_dn = f"cn={groupName},ou=users,{BASE_DN}"
    user_dn = f"uid={uid},ou=users,{BASE_DN}"
    if not conn.search(user_dn, "(objectclass=*)", SUBTREE):
        user_attributes = {
            "objectClass": ["inetOrgPerson", "posixAccount", "top"],
            "uid": uid,
            "userPassword": create_ssha_password(password),
            "cn": this_uid,
            "sn": this_uid,
            "uidNumber": groupId, 
            "gidNumber": groupId,  
            "homeDirectory": f"/home/{uid}",
            "telephoneNumber" : phone
        }
        conn.add(user_dn, attributes=user_attributes)
        print("user Added successfully")
        add_user_to_group(group_dn , uid )
        return True
    else:
        print(f"User {uid} already exists.")
        return False

        
        
def add_user_to_group( group_dn, user_uid ):

    if conn.modify(
        group_dn,
        {'memberUid': [(MODIFY_ADD, [user_uid])]}  # Add the user's UID to the group's memberUid
    ):
        print(f"User '{user_uid}' added to group '{group_dn}' successfully!")
        return True
    else:
        print(f"Failed to add user to group ")
        return False
        
        

