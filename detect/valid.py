# valid.py
import re
from pandas.api.types import is_numeric_dtype


def validate_column_data(column_data, column_type):
    """
    Улучшенная валидация данных столбца с учетом различных форматов

    Параметры:
    - column_data: pandas Series с данными столбца
    - column_type: предполагаемый тип данных (year, birth_date и т.д.)

    Возвращает:
    - Словарь с результатами проверки
    """
    # Берем первые 5 непустых значений, преобразуем в строки
    samples = column_data.head(5).dropna().astype(str).tolist()

    # Правила валидации для каждого типа
    validation_rules = {
        'year': {
            'check': lambda x: re.fullmatch(r'^\d{4}$', x.strip()) is not None,
            'description': '4 цифры (например: 2023)'
        },
        'birth_date': {
            'check': lambda x: any(re.fullmatch(p, x.strip()) for p in [
                r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
                r'^\d{2}\.\d{2}\.\d{4}$',  # DD.MM.YYYY
                r'^\d{4}/\d{2}/\d{2}$',  # YYYY/MM/DD
                r'^\d{8}$',  # YYYYMMDD
                r'^\d{4} год$'  # 1990 год
            ]),
            'description': 'дата в формате ГГГГ-ММ-ДД, ДД.ММ.ГГГГ или YYYYMMDD'
        },
        'inn': {
            'check': lambda x: re.fullmatch(r'^\d{10,12}$', x.strip()) is not None,
            'description': '10 или 12 цифр'
        },
        'phone': {
            'check': lambda x: re.fullmatch(r'^[\d\+\(\)\s\-]{7,20}$', x.strip()) is not None,
            'description': '7-20 цифр с возможными +, (), -'
        },
        'first_name': {
            'check': lambda x: (x.strip().isalpha() and
                                len(x.strip()) >= 2 and
                                x == x.capitalize()),
            'description': 'только буквы, минимум 2 символа, первая заглавная'
        },
        'last_name': {
            'check': lambda x: (x.strip().isalpha() and
                                len(x.strip()) >= 2 and
                                x == x.capitalize()),
            'description': 'только буквы, минимум 2 символа, первая заглавная'
        },
        'middle_name': {
            'check': lambda x: (x.strip().isalpha() and
                                len(x.strip()) >= 2 and
                                x == x.capitalize()),
            'description': 'только буквы, минимум 2 символа, первая заглавная'
        },
        'full_name': {
            'check': lambda x: (all(part.isalpha() for part in x.strip().split()) and
                                len(x.strip().split()) >= 2 and
                                x == x.title()),
            'description': 'минимум 2 слова из букв, каждое с заглавной буквы'
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