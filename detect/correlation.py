import pandas as pd
import numpy as np

def analyze_correlations(df, column_indices):
    """
    Анализ корреляций между указанными столбцами

    Параметры:
    - df: исходный DataFrame
    - column_indices: список индексов столбцов для анализа

    Возвращает:
    - DataFrame с матрицей корреляций
    """
    # Выбираем только неконфиденциальные столбцы
    columns_to_analyze = df.iloc[:, column_indices]

    # Для числовых столбцов считаем корреляцию Пирсона
    numeric_cols = columns_to_analyze.select_dtypes(include=[np.number])
    if not numeric_cols.empty:
        corr_matrix = numeric_cols.corr()
    else:
        corr_matrix = pd.DataFrame()

    return corr_matrix