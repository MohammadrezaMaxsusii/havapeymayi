import ipaddress

def isValidIP(ip:str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except:
        return False
    