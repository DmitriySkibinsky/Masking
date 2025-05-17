from fake import *
import asyncio

# Словарь генераторов, где каждый генератор - это функция
consistency = {
    "first_name": lambda gender=None: generate_full_name(mode="first_name", gender=gender),
    "last_name": lambda gender=None: generate_full_name(mode="last_name", gender=gender),
    "middle_name": lambda gender=None: generate_full_name(mode="middle_name", gender=gender),
    "full_name": lambda gender=None: generate_full_name(mode="all", gender=gender),

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
    "military_ticket_num": lambda: generate_military_ticket_number(),
    "sailor_ticket_num": lambda: generate_military_ticket_number(),
    "birth_certificate_num": lambda: generate_birth_certificate_number(),
    "work_book_num": lambda: generate_work_book_number(),
    "vehicle_number": lambda: generate_car_license(),

    "nr_credit_account": lambda: generate_credit_agreement_number(),
    "nr_bank_contract": lambda: generate_bank_contract_number(),
    "nr_dep_contract": lambda: generate_depository_contract_number(),
    "card_number": lambda: generate_valid_card_number(),
    "bank_account_number": lambda: generate_bank_account_number(),
    "investor_code": lambda: generate_investor_code(),

    "birth_date": generate_birth_date,
}

def get_generator(data_type):
    """Возвращает функцию-генератор для указанного типа данных"""
    return consistency.get(data_type)