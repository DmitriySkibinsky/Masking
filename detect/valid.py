import re
from pandas.api.types import is_numeric_dtype

from natasha import (
    NamesExtractor,
    MorphVocab,
    DatesExtractor,
    Doc
)

morph_vocab = MorphVocab()
names_extractor = NamesExtractor(morph_vocab)
dates_extractor = DatesExtractor(morph_vocab)


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

def validate_with_natasha(text, field_type):
    doc = Doc(text)

    if field_type in ['first_name', 'last_name', 'middle_name', 'full_name']:
        doc.segment(names_extractor)
        if not doc.spans:
            return False

        span = doc.spans[0]
        if field_type == 'full_name':
            # Проверяем, что извлечено полное имя (хотя бы имя и фамилия)
            return hasattr(span, 'first') and hasattr(span, 'last')
        elif field_type == 'first_name':
            return hasattr(span, 'first')
        elif field_type == 'last_name':
            return hasattr(span, 'last')
        elif field_type == 'middle_name':
            return hasattr(span, 'middle')

    elif field_type == 'birth_date':
        doc.segment(dates_extractor)
        return len(doc.spans) > 0  # Дата успешно распознана

    return False


def validate_column_data(column_data, column_type):
    samples = column_data.head(5).dropna().astype(str).tolist()

    validation_rules = {
        'year': {
            'check': lambda x: re.fullmatch(r'^\d{4}$', x.strip()) is not None,
            'description': '4 цифры (например: 2023)'
        },
        'birth_date': {
            'check': lambda x: (
                    re.fullmatch(r'^\d{4}-\d{2}-\d{2}$', x.strip()) or
                    re.fullmatch(r'^\d{2}\.\d{2}\.\d{4}$', x.strip()) or
                    re.fullmatch(r'^\d{4}/\d{2}/\d{2}$', x.strip()) or
                    re.fullmatch(r'^\d{8}$', x.strip()) or
                    re.fullmatch(r'^\d{4} год$', x.strip()) or
                    validate_with_natasha(x, 'birth_date')
            ),
            'description': 'дата в формате ГГГГ-ММ-ДД, ДД.ММ.ГГГГ, YYYYMMDD или текст (например, "12 мая 1990")'
        },
        'inn': {
            'check': lambda x: validate_inn(x),
            'description': '10 или 12 цифр с корректными контрольными суммами'
        },
        'snils': {
            'check': lambda x: validate_snils(x),
            'description': '11 цифр (формат XXX-XXX-XXX YY) с корректной контрольной суммой'
        },
        'phone': {
            'check': lambda x: re.fullmatch(r'^[\d\+\(\)\s\-]{7,20}$', x.strip()) is not None,
            'description': '7-20 цифр с возможными +, (), -'
        },
        'first_name': {
            'check': lambda x: validate_with_natasha(x, 'first_name'),
            'description': 'корректное имя (например, "Иван")'
        },
        'last_name': {
            'check': lambda x: validate_with_natasha(x, 'last_name'),
            'description': 'корректная фамилия (например, "Иванов")'
        },
        'middle_name': {
            'check': lambda x: validate_with_natasha(x, 'middle_name'),
            'description': 'корректное отчество (например, "Иванович")'
        },
        'full_name': {
            'check': lambda x: validate_with_natasha(x, 'full_name'),
            'description': 'полное ФИО (например, "Иванов Иван Иванович")'
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