import random

def generate_uid():
    return str( random.randint(10000, 99999))
def generate_password():
    return str( random.randint(100000, 999999))