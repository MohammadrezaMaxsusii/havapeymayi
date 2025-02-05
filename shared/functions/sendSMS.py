def sendSMS(phone, message):
    try:
        print("SMS sent to " + phone + " with message: " + message)
        return True
    except Exception as e: 
        print(e)
        return False
    

def smsTemplate(username , password):
    sms_template =  """
    با سلام 
    نام کاربری : {username}
    کلمه عبور : {password}
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