import pandas as pd
import numpy as np
from typing import List, Union
import asyncio
import aiofiles
import io

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

# Кодирование строковых данных
def encode_strings(df: pd.DataFrame) -> pd.DataFrame:
    df_encoded = df.copy()
    for col in df.columns:
        if df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
            le = LabelEncoder()
            df_encoded[col] = le.fit_transform(df[col].astype(str))
    return df_encoded

# Генерация числовых данных через регрессию
def generate_numeric_via_regression(df: pd.DataFrame, target_columns: List[str]) -> pd.DataFrame:
    df_encoded = encode_strings(df)
    df_result = df.copy()

    for target_col in target_columns:
        if pd.api.types.is_numeric_dtype(df[target_col]):
            features = df_encoded.drop(columns=[target_col])
            target = df_encoded[target_col]

            if features.shape[1] == 0:
                continue

            model = LinearRegression()
            model.fit(features, target)

            predicted = model.predict(features)
            noise = np.random.normal(scale=np.std(target) * 0.1, size=len(predicted))
            generated = predicted + noise
            df_result[target_col] = np.clip(np.round(generated), df[target_col].min(), df[target_col].max())

    return df_result

# Загрузка данных асинхронно
async def load_data(csv_file: str) -> pd.DataFrame:
    try:
        async with aiofiles.open(csv_file, mode='r') as f:
            content = await f.read()
        return pd.read_csv(io.StringIO(content))
    except Exception as e:
        raise Exception(f"Ошибка загрузки файла {csv_file}: {str(e)}")

# Проверка на целочисленные данные
async def is_integer_column(series: pd.Series) -> bool:
    try:
        return pd.api.types.is_integer_dtype(series)
    except Exception as e:
        print(f"Ошибка проверки целочисленного типа: {str(e)}")
        return False

# Проверка на дробные числа
async def is_float_column(series: pd.Series) -> bool:
    try:
        return pd.api.types.is_float_dtype(series)
    except Exception as e:
        print(f"Ошибка проверки дробного типа: {str(e)}")
        return False

# Проверка на строковые данные
async def is_string_column(series: pd.Series) -> bool:
    try:
        return pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series)
    except Exception as e:
        print(f"Ошибка проверки строкового типа: {str(e)}")
        return False

# Маскировка строковых данных
async def mask_string_data(series: pd.Series) -> pd.Series:
    try:
        value_counts = series.value_counts(normalize=True)

        # Если все строки одинаковые, возвращаем их как есть
        if len(value_counts) == 1:
            return series

        # Если строк много уникальных, маскируем их случайным образом
        unique_values = value_counts.index.tolist()
        print(unique_values)

        probabilities = value_counts.values.tolist()
        print(probabilities)
        # Маскируем, используя вероятности
        masked_values = np.random.choice(unique_values, size=len(series), p=probabilities)
        masked_values = np.random.permutation(masked_values)  # перемешиваем значения для разнообразия
        print(masked_values)
        return pd.Series(masked_values, index=series.index, name=series.name)
    except Exception as e:
        print(f"Ошибка маскировки строковых данных: {str(e)}")
        return series


# Маскировка целочисленных данных
async def mask_integer_data(series: pd.Series) -> pd.Series:
    try:
        col_min = series.min()
        col_max = series.max()
        col_median = series.median()

        random_ints = np.random.randint(col_min, col_max + 1, size=len(series))
        current_median = np.median(random_ints)
        adjustment = int(col_median - current_median)
        masked_data = random_ints + adjustment
        return pd.Series(np.clip(masked_data, col_min, col_max), name=series.name)
    except Exception as e:
        print(f"Ошибка маскировки целых чисел: {str(e)}")
        return series

# Маскировка данных с плавающей точкой
async def mask_float_data(series: pd.Series) -> pd.Series:
    try:
        col_min = series.min()
        col_max = series.max()
        col_median = series.median()
        std_dev = series.std()

        if pd.isna(std_dev) or std_dev == 0:
            std_dev = (col_max - col_min) / 4

        random_floats = np.random.normal(loc=col_median, scale=std_dev, size=len(series))
        masked_data = np.clip(random_floats, col_min, col_max)

        decimal_places = max(0, -int(np.floor(np.log10(std_dev)))) if std_dev > 0 else 2
        masked_data = np.round(masked_data, decimal_places)

        return pd.Series(masked_data, name=series.name)
    except Exception as e:
        print(f"Ошибка маскировки дробных чисел: {str(e)}")
        return series

# Основная маскировка данных, выбор метода в зависимости от типа
async def mask_column(series: pd.Series) -> pd.Series:
    if await is_integer_column(series):
        return await mask_integer_data(series)
    elif await is_float_column(series):
        return await mask_float_data(series)
    elif await is_string_column(series):
        return await mask_string_data(series)
    else:
        print(f"Предупреждение: неизвестный тип данных для колонки '{series.name}', пропускаем")
        return series

# Маскировка выбранных столбцов
async def mask_selected_columns(df: pd.DataFrame, columns_to_mask: List[int]) -> pd.DataFrame:
    """Маскирует только указанные колонки в DataFrame."""
    try:
        if not df.columns.any():
            raise ValueError("DataFrame не содержит колонок с данными")

        # Создаем копию DataFrame, чтобы не изменять исходные данные
        masked_df = df.copy()

        tasks = []
        for col_num in sorted(set(columns_to_mask)):
            if col_num < 1 or col_num > len(masked_df.columns):
                print(f"Предупреждение: номер столбца {col_num} вне диапазона (1-{len(masked_df.columns)}), пропускаем")
                continue

            col_idx = col_num - 1
            column_name = masked_df.columns[col_idx]

            print(f"Маскируем колонку #{col_num} ('{column_name}')...")
            tasks.append(mask_string_data(masked_df[column_name]))

        # Запускаем все задачи маскировки параллельно
        masked_columns = await asyncio.gather(*tasks)

        # Обновляем DataFrame с замаскированными данными
        for col_num, masked_series in zip(sorted(set(columns_to_mask)), masked_columns):
            if col_num < 1 or col_num > len(masked_df.columns):
                continue
            col_idx = col_num - 1
            masked_df.iloc[:, col_idx] = masked_series  # Убедитесь, что правильно обновляется колонка

        print("Данные после маскировки:")
        print(masked_df)

        return masked_df

    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        raise

# Основная функция для маскировки данных и сохранения в CSV
async def process_masking_and_regression(input_csv: str, output_csv: str, columns_to_mask: List[int]):
    try:
        df = await load_data(input_csv)
        print(f"Исходные данные:\n{df}\n")

        # Маскировка выбранных колонок
        df_masked = await mask_selected_columns(df, columns_to_mask)
        print(f"Данные после маскировки:\n{df_masked}\n")

        # Генерация численных данных с использованием регрессии
        numeric_columns = [
            df_masked.columns[col_num - 1]
            for col_num in columns_to_mask
            if col_num >= 1 and col_num <= len(df_masked.columns)
            and pd.api.types.is_numeric_dtype(df_masked.iloc[:, col_num - 1])
        ]
        df_final = generate_numeric_via_regression(df_masked, numeric_columns)

        # Сохранение обработанных данных
        df_final.to_csv(output_csv, index=False)
        print(f"Файл сохранён как {output_csv}")
    except Exception as e:
        print(f"Ошибка в основном процессе: {str(e)}")

# Запуск основной функции
async def main():
    input_file = 'Книга1.csv'
    output_file = 'fake_data2.csv'
    columns_to_process = [1, 2]  # только эти столбцы маскируем

    await process_masking_and_regression(input_file, output_file, columns_to_process)

if __name__ == "__main__":
    asyncio.run(main())
