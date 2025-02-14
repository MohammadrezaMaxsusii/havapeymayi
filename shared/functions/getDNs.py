from shared.functions.shareConfFile import getConfigFile
def getUserDN(uid):
    DB_USER = getConfigFile("database", "DB_USER")
    BASE_DN = f"dc={DB_USER},dc=com"
    user_dn = f"uid={uid},ou=users,{BASE_DN}"
    return user_dn

def getGroupDN(groupName):
    DB_USER = getConfigFile("database", "DB_USER")
    BASE_DN = f"dc={DB_USER},dc=com"
    group_dn = f"cn={groupName},ou=users,{BASE_DN}"
    return group_dn