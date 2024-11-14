import base64
import datetime

import re

from fastapi import HTTPException


def is_valid_phone_number(phone_number: str):

    validate_phone_number_pattern = "^\+?77([0124567][0-8]\d{7})$"
    result = re.match(validate_phone_number_pattern, phone_number)

    return result


def is_owner(user_role: str):
    if user_role != "OWNER":
        raise HTTPException(status_code=403, detail="You don't have permission!")


def is_valid_uuid(uuid_str):
    try:
        uuid_obj = str(uuid_str, version=4)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_str


def convert_str_to_datetime(date: str):
    return datetime.datetime.strptime(date, "%Y-%m-%d")

def correct_base64_padding(data: str) -> str:
    """Добавить padding к строке Base64, если это необходимо."""
    # Удаляем существующий padding
    data = data.rstrip("=")
    # Рассчитываем необходимый padding
    padding_needed = -len(data) % 4
    return data + "=" * padding_needed

def is_valid_base64(data: str) -> bool:
    """Проверить, является ли строка допустимой base64-строкой."""
    try:
        # Если строка является строкой и ее длина кратна 4
        if isinstance(data, str) and len(data) % 4 == 0:
            base64.b64decode(data, validate=True)
            return True
    except (base64.binascii.Error, ValueError):
        return False
    return False
