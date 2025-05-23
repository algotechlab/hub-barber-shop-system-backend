# src/utils/maskphone.py


def mask_phone_number(phone_number):
    phone = (
        phone_number.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
    )
    return phone
