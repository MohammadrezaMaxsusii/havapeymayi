
import configparser
from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_REPLACE , MODIFY_ADD
import hashlib
import base64

config = configparser.ConfigParser()
config.read("config.ini")
DB_HOST = config.get("database", "DB_HOST")

DB_PORT = config.get("database", "DB_PORT")

DB_NAME = config.get("database", "DB_NAME")

DB_USER = config.get("database", "DB_USER")

DB_PASSWORD = config.get("database", "DB_PASSWORD")

LDAP_SERVER = f"ldap://{DB_HOST}:{DB_PORT}"
ADMIN_DN = f"cn=admin,dc={DB_USER},dc=com"
ADMIN_PASSWORD = DB_PASSWORD
BASE_DN = f"dc={DB_USER},dc=com"
GROUP_NAME = "netUser"
server = Server(LDAP_SERVER, get_info=ALL)
conn = Connection(server, ADMIN_DN, ADMIN_PASSWORD, auto_bind=True)

dbData = {
    'LDAP_SERVER':LDAP_SERVER,
    'ADMIN_DN':ADMIN_DN,
    'ADMIN_PASSWORD':ADMIN_PASSWORD,
    'BASE_DN':BASE_DN
}
def create_ssha_password(password):
    salt = b"randomsalt"  # Use a random salt in production
    hashed = hashlib.sha1(password.encode("utf-8") + salt).digest()
    return "{SSHA}" + base64.b64encode(hashed + salt).decode("utf-8")


def add_base_dn():
    print (BASE_DN)
    if not conn.search(BASE_DN, "(objectclass=*)", SUBTREE):
        conn.add(BASE_DN, ["top", "domain"], {"dc": "douran"})
        print(f"Base DN {BASE_DN} added.")
    else:
        print(f"Base DN {BASE_DN} already exists.")

def add_organizational_unit(ou_name):
    ou_dn = f"ou={ou_name},{BASE_DN}"
    if not conn.search(ou_dn, "(objectclass=*)", SUBTREE):
        conn.add(ou_dn, ["top", "organizationalUnit"], {"ou": ou_name})
        print(f"Organizational Unit {ou_name} added.")
    else:
        print(f"Organizational Unit {ou_name} already exists.")


def add_user(uid, first_name, last_name, password, email , phone):
    group_dn = f"cn={GROUP_NAME},ou=users,{BASE_DN}"
    user_dn = f"uid={uid},ou=users,{BASE_DN}"
    if not conn.search(user_dn, "(objectclass=*)", SUBTREE):
        user_attributes = {
            "objectClass": ["inetOrgPerson", "posixAccount", "top"],
            "cn": first_name,
            "sn": last_name,
            "uid": uid,
            "mail": email,
            "userPassword": create_ssha_password(password),
            "uidNumber": "1000",  # Use a unique number for each user
            "gidNumber": "1000",  # Group ID (default group)
            "homeDirectory": f"/home/{uid}",
            "telephoneNumber" : phone
        }
        print("user Added successfully")
        add_user_to_group(group_dn , uid)
    else:
        print(f"User {uid} already exists.")
def add_user_to_group( group_dn, user_uid):
    """
    Add a user to a group in LDAP by modifying the memberUid attribute.
    """
    if conn.modify(
        group_dn,
        {'memberUid': [(MODIFY_ADD, [user_uid])]}  # Add the user's UID to the group's memberUid
    ):
        print(f"User '{user_uid}' added to group '{group_dn}' successfully!")
    else:
        print(f"Failed to add user to group ")
def add_group():
    group_dn = f"cn={GROUP_NAME},ou=users,{BASE_DN}"
    group_attributes = {
        'objectClass': ["top" , "posixGroup"],  # Use 'posixGroup' if required
        'cn': GROUP_NAME,
        'gidNumber' : '500'
    }
    if conn.add(group_dn, attributes=group_attributes):
        print(f"Group '{GROUP_NAME}' added successfully!")
    else:
        print(f"group already exist ")
def createOpenLdapSchema():
    print("createOpenLdapSchema is running:")
    add_base_dn()
    
    add_organizational_unit("users")
    add_group()
    # add_user("0001", "محمدرضا", "مخصوصی", "1234", "jdoe@example.com" , "09123456788")
    # conn.unbind()