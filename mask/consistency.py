from fake import *
import asyncio

# Словарь генераторов, где каждый генератор - это функция
consistency = {
    "first_name": lambda: generate_full_name(mode="first_name"),
    "last_name": lambda: generate_full_name(mode="last_name"),
    "middle_name": lambda: generate_full_name(mode="middle_name"),
    "full_name": lambda: generate_full_name(mode="all"),

    "snils": lambda: generate_identifiers(mode="snils"),
    "inn": lambda: generate_identifiers(mode="inn"),
    "ogrn": lambda: generate_identifiers(mode="ogrn"),
    "kpp": lambda: generate_identifiers(mode="kpp"),
    "okpo": lambda: generate_identifiers(mode="okpo"),
    "ogrnip": lambda: generate_identifiers(mode="ogrnip"),

    "phone": lambda: generate_phone_number(),

    "email": lambda: generate_email(),

    "passport_number": lambda: generate_passport_number(),
    "passport_series": lambda: generate_passport_series(),
    "international_passport_number": lambda: generate_interpass_series_number(),

    "birth_date": generate_birth_date,
}

def get_generator(data_type):
    """Возвращает функцию-генератор для указанного типа данных"""
    return consistency.get(data_type)