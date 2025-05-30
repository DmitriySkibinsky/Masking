import re
from pandas.api.types import is_numeric_dtype
from email_validator import validate_email, EmailNotValidError

TOP_FIELD = 20

from natasha import (
    NamesExtractor,
    MorphVocab,
    AddrExtractor
)

morph_vocab = MorphVocab()
extractor = NamesExtractor(morph_vocab)


def is_name(text, key):
    """
    Проверяет, является ли строка именем указанного типа.

    Параметры:
        text (str): Строка для проверки
        key (str): Тип имени ('first_name', 'last_name', 'middle_name', 'full_name')

    Возвращает:
        bool: True если строка соответствует указанному типу имени
    """
    matches = list(extractor(text))
    if not matches:
        return False

    # Берем первое совпадение
    match = matches[0].fact

    if key == 'first_name':
        return bool(match.first)
    elif key == 'last_name':
        return bool(match.last)
    elif key == 'middle_name':
        return bool(match.middle)
    elif key == 'full_name':
        return bool(match.first and match.last)
    else:
        raise ValueError("Неподдерживаемый ключ. Используйте: 'first_name', 'last_name', 'middle_name', 'full_name'")

def validate_inn(inn_str):
    """Проверка ИНН по контрольным суммам согласно правилам РФ"""
    inn = inn_str.strip()

    # Проверка длины и цифрового содержания
    if not re.fullmatch(r'^\d{10,12}$', inn):
        return False

    # Преобразуем строку в список цифр
    try:
        digits = [int(c) for c in inn]
    except ValueError:
        return False

    # Проверка 10-значного ИНН (для юридических лиц)
    if len(digits) == 10:
        # Коэффициенты для проверки контрольной цифры (10-й цифры)
        coefficients = [2, 4, 10, 3, 5, 9, 4, 6, 8]
        # Вычисляем контрольную сумму
        control_sum = sum([a * b for a, b in zip(digits[:-1], coefficients)]) % 11 % 10
        return control_sum == digits[-1]

    # Проверка 12-значного ИНН (для физических лиц и ИП)
    elif len(digits) == 12:
        # Коэффициенты для проверки первой контрольной цифры (11-й цифры)
        coefficients_11 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        control_sum_11 = sum([a * b for a, b in zip(digits[:-2], coefficients_11)]) % 11 % 10

        # Коэффициенты для проверки второй контрольной цифры (12-й цифры)
        coefficients_12 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        control_sum_12 = sum([a * b for a, b in zip(digits[:-1], coefficients_12)]) % 11 % 10

        return control_sum_11 == digits[-2] and control_sum_12 == digits[-1]

    return False


def validate_ogrn(ogrn_str):
    """Проверка ОГРН (Основной государственный регистрационный номер)"""
    ogrn = re.sub(r'[^\d]', '', ogrn_str)

    if len(ogrn) != 13 or not ogrn.isdigit():
        return False

    num = int(ogrn[:-1])
    control = int(ogrn[-1])
    return num % 11 % 10 == control


def validate_ogrnip(ogrnip_str):
    """Проверка ОГРНИП (ОГРН для ИП)"""
    ogrnip = re.sub(r'[^\d]', '', ogrnip_str)

    if len(ogrnip) != 15 or not ogrnip.isdigit():
        return False

    num = int(ogrnip[:-1])
    control = int(ogrnip[-1])
    return num % 13 % 10 == control


def validate_kpp(kpp_str):
    """Проверка КПП (Код причины постановки на учет)"""
    kpp = re.sub(r'[^\d]', '', kpp_str)

    if len(kpp) != 9 or not kpp.isdigit():
        return False

    # Первые 4 цифры - код налогового органа
    # 5-6 цифры - причина постановки (должны быть в допустимом диапазоне)
    reason_code = int(kpp[4:6])
    valid_reasons = [1, 2, 3, 4, 5, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
                     52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76,
                     77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]

    return reason_code in valid_reasons


def validate_okpo(okpo_str):
    """Проверка ОКПО (Общероссийский классификатор предприятий и организаций)"""
    okpo = re.sub(r'[^\d]', '', okpo_str)

    if len(okpo) not in (8, 10) or not okpo.isdigit():
        return False

    digits = [int(c) for c in okpo]

    # Для 8-значных номеров (юридические лица)
    if len(digits) == 8:
        weights = [1, 2, 3, 4, 5, 6, 7]
        control_sum = sum(d * w for d, w in zip(digits[:-1], weights)) % 11 % 10
        return control_sum == digits[-1]

    # Для 10-значных номеров (ИП)
    elif len(digits) == 10:
        weights = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        control_sum = sum(d * w for d, w in zip(digits[:-1], weights)) % 11 % 10
        return control_sum == digits[-1]

    return False

def validate_email_address(email_str):
    """
    Проверяет валидность email адреса с помощью email-validator
    и предоставляет альтернативную проверку через regex
    """
    email = email_str.strip()

    # Проверка через email-validator (более строгая)
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        pass

    # Альтернативная проверка через regex (менее строгая)
    regex_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.fullmatch(regex_pattern, email) is not None

def validate_snils(snils_str):
    """
    Проверка СНИЛС по контрольной сумме согласно правилам РФ.
    Правила:
    1. Должно быть 11 цифр (формат: XXX-XXX-XXX YY, но проверяем только цифры)
    2. Контрольное число (2 последние цифры) вычисляется по специальному алгоритму:
       - Первые 9 цифр умножаются на коэффициенты от 9 до 1 соответственно
       - Сумма произведений вычисляется
       - Если сумма < 100, контрольное число должно равняться этой сумме
       - Если сумма == 100 или 101, контрольное число должно быть 00
       - Если сумма > 101, вычисляется остаток от деления на 101
         (если остаток < 100, он становится контрольным числом, иначе 00)
    """
    snils = re.sub(r'[^\d]', '', snils_str)

    if len(snils) != 11 or not snils.isdigit():
        return False

    digits = [int(c) for c in snils]
    base = digits[:9]
    control = digits[-2] * 10 + digits[-1]

    # Проверка на все одинаковые цифры (недопустимо)
    if len(set(base)) == 1:
        return False

    # Вычисление контрольной суммы
    coefficients = list(range(9, 0, -1))
    weighted_sum = sum(a * b for a, b in zip(base, coefficients))

    if weighted_sum < 100:
        computed_control = weighted_sum
    elif weighted_sum in (100, 101):
        computed_control = 0
    else:
        remainder = weighted_sum % 101
        computed_control = remainder if remainder < 100 else 0

    return computed_control == control

def validate_passport_number(passport_str: str) -> bool:
    """
    Проверка номера паспорта РФ
    Должен содержать минимум 6 цифр (может быть с разделителями)
    """
    cleaned = re.sub(r'[^\d]', '', passport_str)
    return len(cleaned) >= 6 and cleaned.isdigit()

def validate_passport_series(series_str: str) -> bool:
    """
    Проверка серии паспорта РФ
    Должна содержать ровно 4 цифры (может быть с разделителями)
    """
    cleaned = re.sub(r'[^\d]', '', series_str)
    return len(cleaned) == 4 and cleaned.isdigit()

def validate_international_passport_number(passport_str: str) -> bool:
    """
    Проверка номера загранпаспорта РФ
    Должен содержать 2 буквы и 6 цифр (может быть с разделителями)
    """
    cleaned = re.sub(r'[^\w]', '', passport_str).upper()
    if len(cleaned) != 8:
        return False

    letters_part = cleaned[:2]
    digits_part = cleaned[2:]

    # Проверяем что первые 2 символа - русские буквы из допустимого набора
    valid_letters = {'А', 'В', 'Е', 'К', 'М', 'Н', 'О', 'Р', 'С', 'Т', 'У', 'Х'}
    if not all(c in valid_letters for c in letters_part):
        return False

    return digits_part.isdigit() and len(digits_part) == 6


def validate_military_ticket_number(ticket_str):
    """
    Простая проверка номера военного билета
    Формат: 2 любые русские буквы + 7 цифр (пробелы не учитываются)
    """
    if not isinstance(ticket_str, str):
        return False

    # Удаляем все пробелы и приводим к верхнему регистру
    cleaned = re.sub(r'\s', '', ticket_str).upper()

    # Проверяем формат: 2 буквы + 7 цифр
    return bool(re.fullmatch(r'^[А-ЯЁ]{2}\d{7}$', cleaned))

def validate_birth_certificate_number_simple(value: str) -> bool:
    """
    Возвращает True, если строка содержит 2 заглавные кириллические буквы и 6 цифр.
    Иначе — False.
    """
    pattern = r'[А-ЯЁ]{2}.*\d{6}'
    return bool(re.search(pattern, value.strip()))

def validate_work_book_number(value: str) -> bool:
    """
    Возвращает True, если строка содержит 6 цифр подряд.
    Иначе — False.
    """
    pattern = r'\d{6}'
    return bool(re.search(pattern, value.strip()))

def validate_vehicle_number(value: str) -> bool:
    """
    Возвращает True, если строка содержит хотя бы 3 цифры и 2 кириллические буквы.
    Иначе — False.
    """
    has_digits = re.search(r'\d{3}', value)
    has_letters = re.search(r'[А-ЯЁ]{2}', value.upper())
    return bool(has_digits and has_letters)

def validate_credit_agreement(value: str) -> bool:
    """
    Возвращает True, если строка содержит хотя бы 6 цифры и 2 кириллические буквы.
    Иначе — False.
    """
    has_digits = re.search(r'\d{6}', value)
    has_letters = re.search(r'[А-ЯЁ]{2}', value.upper())
    return bool(has_digits and has_letters)

def validate_card_number(value: str) -> bool:
    """
    Проверяет, содержит ли строка номер карты (16+ цифр).
    Возвращает True если условие выполняется, иначе False.
    """
    # Ищем последовательность из 16+ цифр, возможно с разделителями
    pattern = r'(?:\d[ -]?){16,}'
    return bool(re.fullmatch(pattern, value))

def validate_account_number(value: str) -> bool:
    """
    Проверяет, содержит ли строка номер счета (20+ цифр).
    Возвращает True если условие выполняется, иначе False.
    """
    # Ищем последовательность из 20+ цифр, возможно с разделителями
    pattern = r'(?:\d[ -]?){16,}'
    return bool(re.fullmatch(pattern, value))

def validate_investor_code(value: str) -> bool:
    """
    Проверяет, содержит ли строка код инвестора (6+ цифр).
    Возвращает True если условие выполняется, иначе False.
    """
    pattern = r'(?:\d[ -]?{6,})'
    return bool(re.fullmatch(pattern, value))


def validate_address(text: str) -> bool:
    """
    Проверяет, содержит ли строка адрес (возвращает True/False)

    Args:
        text: строка для анализа

    Returns:
        bool: True если строка содержит адрес, иначе False
    """
    morph_vocab = MorphVocab()
    addr_extractor = AddrExtractor(morph_vocab)

    matches = list(addr_extractor(text))
    return len(matches) > 0

def validate_login(value: str) -> bool:
    """
    Проверяет, соответствует ли строка формату логина (3+ символов: буквы, цифры, _-.).
    Возвращает True, если условие выполняется, иначе False.
    """
    pattern = r'^[a-zA-Z0-9_\-.]{3,}$'
    return bool(re.fullmatch(pattern, value))


def validate_ip(value: str) -> bool:
    """
    Проверяет, является ли строка IPv4 или IPv6 адресом.
    Возвращает True, если условие выполняется, иначе False.
    """
    # IPv4 (e.g., 192.168.1.1)
    ipv4_pattern = r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$'
    # IPv6 (упрощенная проверка)
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'

    return bool(re.fullmatch(ipv4_pattern, value) or re.fullmatch(ipv6_pattern, value))


def validate_domain(value: str) -> bool:
    """
    Проверяет, является ли строка корректным доменным именем (с точкой и зоной).
    Примеры валидных:
    - example.ru
    - sub.domain.com
    - site.ua
    - localhost.local

    Возвращает True, если соответствует формату, иначе False.
    """
    pattern = r'^[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)+$'
    return bool(re.fullmatch(pattern, value))

def validate_column_data(column_data, column_type):
    samples = column_data.head(TOP_FIELD).dropna().astype(str).tolist()

    validation_rules = {
        'birth_date': {
            'check': lambda x: (
                    re.fullmatch(r'^\d{4}-\d{2}-\d{2}$', x.strip()) or
                    re.fullmatch(r'^\d{2}\.\d{2}\.\d{4}$', x.strip()) or
                    re.fullmatch(r'^\d{4}/\d{2}/\d{2}$', x.strip()) or
                    re.fullmatch(r'^\d{8}$', x.strip()) or
                    re.fullmatch(r'^\d{4} год$', x.strip()) or
                    is_name(x, 'birth_date')
            ),
            'description': 'дата в формате ГГГГ-ММ-ДД, ДД.ММ.ГГГГ, YYYYMMDD или текст (например, "12 мая 1990")'
        },
        'phone': {
            'check': lambda x: re.fullmatch(r'^[\d\+\(\)\s\-]{7,20}$', x.strip()) is not None,
            'description': '7-20 цифр с возможными +, (), -'
        },
        'first_name': {
            'check': lambda x: is_name(x, 'first_name'),
            'description': 'корректное имя (например, "Иван")'
        },
        'last_name': {
            'check': lambda x: is_name(x, 'last_name'),
            'description': 'корректная фамилия (например, "Иванов")'
        },
        'middle_name': {
            'check': lambda x: is_name(x, 'middle_name'),
            'description': 'корректное отчество (например, "Иванович")'
        },
        'full_name': {
            'check': lambda x: is_name(x, 'full_name'),
            'description': 'полное ФИО (например, "Иванов Иван Иванович")'
        },
        'inn': {
            'check': lambda x: validate_inn(x),
            'description': '10 или 12 цифр с корректными контрольными суммами'
        },
        'snils': {
            'check': lambda x: validate_snils(x),
            'description': '11 цифр (формат XXX-XXX-XXX YY) с корректной контрольной суммой'
        },
        'ogrn': {
            'check': lambda x: validate_ogrn(x),
            'description': '13 цифр с корректной контрольной суммой (для юр. лиц)'
        },
        'ogrnip': {
            'check': lambda x: validate_ogrnip(x),
            'description': '15 цифр с корректной контрольной суммой (для ИП)'
        },
        'kpp': {
            'check': lambda x: validate_kpp(x),
            'description': '9 цифр с корректным кодом причины постановки'
        },
        'okpo': {
            'check': lambda x: validate_okpo(x),
            'description': '8 цифр (юр. лица) или 10 цифр (ИП) с контрольной суммой'
        },
        'passport_number': {
            'check': lambda x: validate_passport_number(x),
            'description': 'корректный номер паспорта (содержит от 6 цифр)'
        },
        'passport_series': {
            'check': lambda x: validate_passport_series(x),
            'description': 'корректный серия паспорта (4 цифры)'
        },
        'international_passport_number':{
            'check': lambda x: validate_international_passport_number(x),
            'description': 'корректный номер загран. паспорта (содержит 2 буквы и 6 цифр)'
        },
        'military_ticket_num':{
            'check': lambda x: validate_military_ticket_number(x),
            'description': 'корректный номер военного билета (содержит 2 буквы и 7 цифр)'
        },
        'sailor_ticket_num':{
            'check': lambda x: validate_military_ticket_number(x),
            'description': 'корректный номер билета моряка (содержит 2 буквы и 7 цифр)'
        },
        'birth_certificate_num':{
            'check': lambda x: validate_birth_certificate_number_simple(x),
            'description': 'корректное свидетельство о рождении (содержит 2 буквы и 6 цифр)'
        },
        'work_book_num':{
            'check': lambda x: validate_work_book_number(x),
            'description': 'корректная трудовая книга (содержит 6 цифр)'
        },
        'vehicle_number':{
            'check': lambda x: validate_vehicle_number(x),
            'description': 'корректный номер автомобиля (3 цифры и хотя бы 2 буквы)'
        },
        'email': {
            'check': lambda x: validate_email_address(x),
            'description': 'корректный email адрес (например, user@example.com)'
        },
        'nr_credit_account': {
            'check': lambda x: validate_credit_agreement(x),
            'description': 'корректный номер кредитного договора (2 буквы, 6 цифр)'
        },
        'nr_bank_contract': {
            'check': lambda x: validate_credit_agreement(x),
            'description': 'корректный номер банковского договора (2 буквы, 6 цифр)'
        },
        'nr_dep_contract': {
            'check': lambda x: validate_credit_agreement(x),
            'description': 'корректный номер депозитарного договора (2 буквы, 6 цифр)'
        },
        'card_number': {
            'check': lambda x: validate_card_number(x),
            'description': 'корректный номер карты (от 16 цифр)'
        },
        'bank_account_number': {
            'check': lambda x: validate_account_number(x),
            'description': 'корректный номер банковского счета (от 20 цифр)'
        },
        'investor_code': {
            'check': lambda x: validate_investor_code(x),
            'description': 'корректный код инвестора (от 6 цифр)'
        },
        'address': {
            'check': lambda x: validate_address(x),
            'description': 'корректный адрес'
        },
        'login': {
            'check': lambda x: validate_login(x),
            'description': 'корректный логин'
        },
        'ip': {
            'check': lambda x: validate_ip(x),
            'description': 'корректный IP (является IPv4 или IPv6)'
        },
        'uri': {
            'check': lambda x: validate_domain(x),
            'description': 'корректный домен (в конце точка и символы)'
        }
    }

    if column_type not in validation_rules:
        return {
            'is_valid': None,
            'description': f'Нет правил валидации для типа {column_type}',
            'sample_data': samples
        }

    # Проверяем каждое значение
    passed = 0
    for value in samples:
        try:
            if validation_rules[column_type]['check'](value):
                passed += 1
        except:
            continue

    pass_rate = passed / len(samples) if samples else 0

    return {
        'is_valid': pass_rate >= 0.6,  # 60% должны соответствовать
        'pass_rate': f"{pass_rate:.0%}",
        'description': validation_rules[column_type]['description'],
        'sample_data': samples,
        'expected_format': validation_rules[column_type]['description']
    }