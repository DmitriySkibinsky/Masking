import pandas as pd
import numpy as np
from typing import List, Union
import asyncio
import aiofiles


async def load_data(csv_file: str) -> pd.DataFrame:
    """Асинхронно загружает данные из CSV файла."""
    try:
        async with aiofiles.open(csv_file, mode='r') as f:
            content = await f.read()
        return pd.read_csv(pd.compat.StringIO(content))
    except Exception as e:
        raise Exception(f"Ошибка загрузки файла {csv_file}: {str(e)}")


async def is_integer_column(series: pd.Series) -> bool:
    """Проверяет, содержит ли колонка только целые числа."""
    try:
        return pd.api.types.is_integer_dtype(series)
    except Exception as e:
        print(f"Ошибка проверки целочисленного типа: {str(e)}")
        return False


async def is_float_column(series: pd.Series) -> bool:
    """Проверяет, содержит ли колонка дробные числа."""
    try:
        return pd.api.types.is_float_dtype(series)
    except Exception as e:
        print(f"Ошибка проверки дробного типа: {str(e)}")
        return False


async def is_string_column(series: pd.Series) -> bool:
    """Проверяет, содержит ли колонка строковые значения."""
    try:
        return pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series)
    except Exception as e:
        print(f"Ошибка проверки строкового типа: {str(e)}")
        return False


async def detect_number_scale(series: pd.Series) -> int:
    """Определяет характерный масштаб чисел (количество нулей в конце)."""
    try:
        non_zero = series[series != 0].dropna()
        if len(non_zero) == 0:
            return 0

        def count_trailing_zeros(x):
            s = str(int(x))
            return len(s) - len(s.rstrip('0'))

        trailing_zeros = non_zero.apply(count_trailing_zeros)
        return int(trailing_zeros.mode()[0]) if len(trailing_zeros.mode()) > 0 else 0
    except Exception as e:
        print(f"Ошибка определения масштаба чисел: {str(e)}")
        return 0


async def is_round_number(n: Union[int, float]) -> bool:
    """Проверяет, является ли число круглым (оканчивается на 0 или 5)."""
    try:
        return n % 5 == 0
    except Exception as e:
        print(f"Ошибка проверки круглого числа: {str(e)}")
        return False


async def detect_round_numbers(series: pd.Series) -> bool:
    """Определяет, содержит ли серия преимущественно круглые числа."""
    try:
        if not await is_integer_column(series):
            return False

        non_na = series.dropna()
        if len(non_na) == 0:
            return False

        round_count = sum(await is_round_number(x) for x in non_na)
        return (round_count / len(non_na)) > 0.7
    except Exception as e:
        print(f"Ошибка определения круглых чисел: {str(e)}")
        return False


async def mask_round_integer_data(series: pd.Series) -> pd.Series:
    """Маскирует целочисленные данные с сохранением 'круглости' чисел."""
    try:
        col_min = series.min()
        col_max = series.max()
        col_median = series.median()

        base_values = np.arange(col_min, col_max + 1)
        round_values = [x for x in base_values if await is_round_number(x)]

        if not round_values:
            round_values = [x for x in range(col_min, col_max + 1, 5)]

        random_round = np.random.choice(round_values, size=len(series))

        current_median = np.median(random_round)
        adjustment = int(round((col_median - current_median) / 5) * 5)
        masked_data = random_round + adjustment

        masked_data = np.clip(masked_data, col_min, col_max)
        masked_data = (masked_data // 5) * 5

        return pd.Series(masked_data, name=series.name)
    except Exception as e:
        print(f"Ошибка маскировки круглых чисел: {str(e)}")
        return series


async def mask_scaled_integer_data(series: pd.Series) -> pd.Series:
    """Маскирует числа с сохранением их масштаба (количества нулей в конце)."""
    try:
        scale = await detect_number_scale(series)
        base_series = series // (10 ** scale)

        masked_base = await mask_integer_data(base_series)
        masked_data = masked_base * (10 ** scale)

        return masked_data.astype(series.dtype)
    except Exception as e:
        print(f"Ошибка маскировки масштабированных чисел: {str(e)}")
        return series


async def mask_float_data(series: pd.Series) -> pd.Series:
    """Маскирует дробные числовые данные."""
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


async def mask_string_data(series: pd.Series) -> pd.Series:
    """Маскирует строковые данные."""
    try:
        pass
    except Exception as e:
        print(f"Ошибка маскировки строковых данных: {str(e)}")
        return series


async def mask_integer_data(series: pd.Series) -> pd.Series:
    """Выбирает подходящий метод маскировки для целых чисел."""
    try:
        scale = await detect_number_scale(series)

        if scale >= 2:
            return await mask_scaled_integer_data(series)
        elif await detect_round_numbers(series):
            return await mask_round_integer_data(series)

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


async def mask_column(series: pd.Series) -> pd.Series:
    """Выбирает подходящую функцию маскировки в зависимости от типа данных."""
    try:
        if await is_integer_column(series):
            return await mask_integer_data(series)
        elif await is_float_column(series):
            return await mask_float_data(series)
        elif await is_string_column(series):
            return await mask_string_data(series)
        else:
            print(f"Предупреждение: неизвестный тип данных для колонки '{series.name}', пропускаем")
            return series
    except Exception as e:
        print(f"Ошибка при маскировке колонки '{series.name}': {str(e)}")
        return series


async def mask_data_in_csv(csv_file: str, columns_to_mask: List[int]) -> pd.DataFrame:
    """
    Основная асинхронная функция для маскировки данных в CSV файле.

    Параметры:
    - csv_file: путь к CSV файлу
    - columns_to_mask: список номеров колонок для маскировки (начиная с 1)

    Возвращает:
    - DataFrame с замаскированными данными
    """
    try:
        df = await load_data(csv_file)

        if not df.columns.any():
            raise ValueError("Файл не содержит колонок с данными")

        tasks = []
        for col_num in sorted(set(columns_to_mask)):
            if col_num < 1 or col_num > len(df.columns):
                print(f"Предупреждение: номер столбца {col_num} вне диапазона (1-{len(df.columns)}), пропускаем")
                continue

            col_idx = col_num - 1
            column_name = df.columns[col_idx]

            print(f"Обработка колонки #{col_num} ('{column_name}')...")
            tasks.append(mask_column(df[column_name]))

        # Запускаем все задачи маскировки параллельно
        masked_columns = await asyncio.gather(*tasks)

        # Обновляем DataFrame с замаскированными данными
        for col_num, masked_series in zip(sorted(set(columns_to_mask)), masked_columns):
            if col_num < 1 or col_num > len(df.columns):
                continue
            col_idx = col_num - 1
            df.iloc[:, col_idx] = masked_series

        return df

    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        raise


async def main():
    # Пример использования:
    try:
        masked_df = await mask_data_in_csv('salaries.csv', [2])  # Маскируем столбец 2 (зарплаты)
        masked_df.to_csv('masked_salaries.csv', index=False)
    except Exception as e:
        print(f"Ошибка в основном потоке: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())