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
            'check': lambda x: re.fullmatch(r'^\d{10,12}$', x.strip()) is not None,
            'description': '10 или 12 цифр'
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