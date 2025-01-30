from fastapi import HTTPException

persian_to_english = {
    "۰": "0",
    "۱": "1",
    "۲": "2",
    "۳": "3",
    "۴": "4",
    "۵": "5",
    "۶": "6",
    "۷": "7",
    "۸": "8",
    "۹": "9",
}


def persianDigitToEnglish(digit: str) -> str:
    return persian_to_english.get(digit, None)


def ensure_phone_number(phone_number: str) -> str:
    good_number = ""

    for char in phone_number:
        if char.isdigit():
            good_number += char

        elif char not in persian_to_english:
            raise HTTPException(400, "شماره تلفن وارد شده صحیح نیست")

        good_number += persianDigitToEnglish(char)

    return good_number
