from fake import *

# Словарь генераторов, где каждый генератор - это функция
consistency = {
    "first_name": lambda: generate_full_name(mode="first_name"),
    "last_name": lambda: generate_full_name(mode="last_name"),
    "middle_name": lambda: generate_full_name(mode="middle_name"),
    "full_name": lambda: generate_full_name(mode="all"),
    "inn": generate_inn,
    "phone": generate_phone_number,
    "birth_date": generate_birth_date,
    "year": lambda: str(generate_birth_date().year)
}

def get_generator(data_type):
    """Возвращает функцию-генератор для указанного типа данных"""
    return consistency.get(data_type)