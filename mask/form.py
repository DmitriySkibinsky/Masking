import numpy as np
import pandas as pd
import chardet

def form(csv, data):
    try:
        with open(csv, 'rb') as f:
            rawdata = f.read(10000)
            encoding = chardet.detect(rawdata)['encoding']
        print(f"Определена кодировка файла: {encoding}")

        df = pd.read_csv(csv, encoding=encoding)

        all_columns = df.columns.tolist()
        present_columns = [item[0] for item in data]

        missing_columns = [col for col in all_columns if col not in present_columns]

        missing_indices = [all_columns.index(col) + 1 for col in missing_columns]
        used_indices = [item[1] + 1 for item in data]  # Увеличиваем на 1, чтобы индексы начинались с 1
        unused_indices = [index for index in range(1, len(all_columns) + 1) if index not in used_indices]

        print("Индексы отсутствующих колонок:", missing_indices)
        print("Индексы неиспользуемых колонок:", unused_indices)
        return unused_indices
    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Ваш список колонок
data = [['first_name', 0, np.float32(0.8004)], ['last_name', 1, np.float32(0.6042)]]
form("Книга1.csv", data)
