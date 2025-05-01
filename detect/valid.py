import re
from pandas.api.types import is_numeric_dtype
from email_validator import validate_email, EmailNotValidError

TOP_FIELD = 5

from natasha import (
    NamesExtractor,
    MorphVocab
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
        'email': {
            'check': lambda x: validate_email_address(x),
            'description': 'корректный email адрес (например, user@example.com)'
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