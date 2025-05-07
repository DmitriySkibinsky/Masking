import csv
import numpy as np
import chardet
from natasha import MorphVocab, NamesExtractor

# Глобальные переменные с результатами анализа
analysis_results = {}  # Будет хранить результаты в формате {row_num: {'type': result}}

# Глобальные переменные с окончаниями
MALE_NAME_ENDS = ('й', 'н', 'р', 'с', 'т', 'в', 'д', 'л', 'г', 'к')
FEMALE_NAME_ENDS = ('а', 'я', 'ь', 'ия')
NAME_MALE_EXCEPTIONS = ('ника', 'саша', 'жулиа', 'витали', 'евгени', "игорь", "дима", "леша", "вася", "петя", "костя", )

MALE_SURNAME_ENDS = ('ов', 'ев', 'ин', 'ын', 'ский', 'цкий', 'ой', 'ий')
FEMALE_SURNAME_ENDS = ('ова', 'ева', 'ина', 'ына', 'ская', 'цкая', 'ая', 'яя', 'a')

MALE_MIDDLE_NAME_ENDS = ('ович', 'евич', 'ич', 'ыч')
FEMALE_MIDDLE_NAME_ENDS = ('овна', 'евна', 'ична', 'инична')

# Веса по умолчанию
DEFAULT_WEIGHTS = {
    'first_name': 0.3,
    'last_name': 0.4,
    'middle_name': 0.3
}


class GenderAnalyzer:
    def __init__(self):
        self.morph_vocab = MorphVocab()
        self.names_extractor = NamesExtractor(self.morph_vocab)

    def _get_gender_from_natasha(self, text):
        """Определение пола через Natasha"""
        try:
            matches = list(self.names_extractor(text))
            if matches:
                fact = matches[0].fact
                if hasattr(fact, 'first') and fact.first:
                    return fact.first.gender
        except Exception:
            pass
        return None

    def _get_gender_heuristic(self, text, mode):
        """Эвристические правила для определения пола"""
        if not text:
            return None

        text_lower = text.lower()

        if mode == 'first_name':
            if text_lower in NAME_MALE_EXCEPTIONS:
                return 'male'
            if any(text_lower.endswith(end) for end in MALE_NAME_ENDS):
                return 'male'
            if any(text_lower.endswith(end) for end in FEMALE_NAME_ENDS):
                return 'female'

        elif mode == 'last_name':
            if any(text_lower.endswith(end) for end in MALE_SURNAME_ENDS):
                return 'male'
            if any(text_lower.endswith(end) for end in FEMALE_SURNAME_ENDS):
                return 'female'

        elif mode == 'middle_name':
            if any(text_lower.endswith(end) for end in MALE_MIDDLE_NAME_ENDS):
                return 'male'
            if any(text_lower.endswith(end) for end in FEMALE_MIDDLE_NAME_ENDS):
                return 'female'
            if text_lower.endswith('на'):
                return 'female'
            if text_lower.endswith('ич') or text_lower.endswith('ыч'):
                return 'male'

        return None

    def detect_gender(self, text, mode):
        """Определение пола с приоритетом Natasha для имен и фамилий"""
        if not text or not isinstance(text, str):
            return 'invalid_input'

        text = text.strip().split()[0]

        if mode in ['first_name', 'last_name']:
            gender = self._get_gender_from_natasha(text)
            if gender:
                return gender

        gender = self._get_gender_heuristic(text, mode)
        if gender:
            return gender

        return 'unknown'


def parse_analysis_config(config):
    """Парсинг конфигурации анализа"""
    analysis_commands = []
    weights = DEFAULT_WEIGHTS.copy()

    for item in config:
        if len(item) >= 3:
            field_type = item[0]
            column_idx = item[1]
            weight = float(item[2])  # Конвертируем np.float32 в обычный float

            analysis_commands.append((field_type, column_idx))
            weights[field_type] = weight

    return analysis_commands, weights


def detect_file_encoding(file_path):
    """Определение кодировки файла"""
    with open(file_path, 'rb') as f:
        rawdata = f.read(10000)
        result = chardet.detect(rawdata)
        return result['encoding'] if result['confidence'] > 0.7 else 'utf-8'


def analyze_file(file_path, analysis_commands, skip_header=True):
    """Анализ файла по заданным командам"""
    analyzer = GenderAnalyzer()
    global analysis_results

    try:
        encoding = detect_file_encoding(file_path)

        with open(file_path, 'r', encoding=encoding) as file:
            reader = csv.reader(file)
            for row_num, row in enumerate(reader):
                if skip_header and row_num == 0:
                    continue

                if row_num not in analysis_results:
                    analysis_results[row_num] = {}

                for field_type, column_idx in analysis_commands:
                    if column_idx < len(row):
                        text = row[column_idx].strip()
                        if text:
                            result = analyzer.detect_gender(text, field_type)
                        else:
                            result = 'empty'
                    else:
                        result = 'no_column'

                    analysis_results[row_num][field_type] = result

    except Exception as e:
        analysis_results['error'] = str(e)


def get_final_verdicts(weights):
    """Возвращает словарь с финальными вердиктами для всех строк"""
    global analysis_results
    final_results = {}
    has_definite_results = False

    for row_num, results in analysis_results.items():
        if isinstance(row_num, int):  # Пропускаем записи об ошибках
            male_score = 0
            female_score = 0

            for field_type, result in results.items():
                weight = weights.get(field_type, 0)

                if result == 'male':
                    male_score += weight
                    has_definite_results = True
                elif result == 'female':
                    female_score += weight
                    has_definite_results = True

            if male_score > female_score:
                final_results[row_num] = 'male'
            elif female_score > male_score:
                final_results[row_num] = 'female'
            else:
                final_results[row_num] = 'unknown'

    return final_results if has_definite_results else {}


def detect_gender(config, file_path):
    """Основная функция для определения пола"""
    global analysis_results
    analysis_results = {}  # Очищаем предыдущие результаты

    analysis_commands, weights = parse_analysis_config(config)
    analyze_file(file_path, analysis_commands)
    final_verdicts = get_final_verdicts(weights)

    return final_verdicts


if __name__ == "__main__":
    # Пример конфигурации анализа
    config = [
        ['first_name', 0, np.float32(0.5)],
        ['last_name', 1, np.float32(0.3)],
        ['middle_name', 2, np.float32(0.2)]
    ]

    result = detect_gender(config, '../mask/fake_data.csv')
    print("Результаты анализа:", result)