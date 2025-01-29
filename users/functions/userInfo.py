
import configparser
import requests
config = configparser.ConfigParser()
config.read("config.ini")
OAUTH_URL = config.get("mycao", "OAUTH_URL")
CLIENT_ID = config.get("mycao", "CLIENT_ID")
CLIENT_SECRET = config.get("mycao", "CLIENT_SECRET")
REDIRECT_URI = config.get("mycao", "REDIRECT_URI")


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