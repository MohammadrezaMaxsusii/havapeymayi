import random

def generate_otp() -> str:
    return str( random.randint(1000, 9999))