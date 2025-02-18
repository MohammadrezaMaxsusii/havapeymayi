import requests
import json
import configparser
config = configparser.ConfigParser()
config.read("config.ini")
API_URL = config.get("sms", "API_URL")
ORGANIZATION = config.get("sms", "ORGANIZATION")
username = config.get("sms", "USERNAME")
password = config.get("sms", "PASSWORD")
shortNum = config.get("sms"  , "SHORTNUMBER")

from datetime import datetime

def sendSMS( dest_numbers, message):
    dest_numbers = dest_numbers[1:]
    dest_numbers = "98" + dest_numbers
    url = "http://ws.adpdigital.com/url/send"
    params = {
    "username": username,
    "password": password,
    "dstaddress" : dest_numbers,
    "body":message,
    "clientid": dest_numbers,
    "unicode" : 1
    }
    response = requests.get(url, params=params)
    return response.status_code
    



# response = send_sms(username, password, short_number, dest_numbers, message)
# print(response)

# def sendSMS(phone, message):
#     try:
#         print("SMS sent to " + phone + " with message: " + message)
#         return True
#     except Exception as e: 
#         return False
#     return True
    

def smsTemplate(username , password):
    sms_template =  """
    با سلام 
    اطلاعات دسترسی اینترنتی 
    نام کاربری : {username}
    کلمه عبور : {password}
        سازمان هواپیمایی کشور     
    ssids: CAO  **** CAO-2.4
"""
    final_sms = sms_template.format(username=username, password=password)
    return final_sms

def otpSmsTemplate(otp:str):
    sms_template =  """
    هواپیمایی کشور
    کد محرمانه، در اختیار دیگران قرار ندهید:
    {otp}
"""
    return sms_template.format(otp=otp)