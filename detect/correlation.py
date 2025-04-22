import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


def analyze_correlations(df, column_indices, save_path='../detect/res/correlation_heatmap.png'):
    """
    Анализ корреляций и сохранение тепловой карты

    Параметры:
    - df: исходный DataFrame
    - column_indices: список индексов столбцов для анализа
    - save_path: путь для сохранения heatmap (по умолчанию 'correlation_heatmap.png')

    Возвращает:
    - DataFrame с матрицей корреляций
    - Сохраняет тепловую карту в файл
    """
    # Выбираем указанные столбцы
    columns_to_analyze = df.iloc[:, column_indices]

    # Для числовых столбцов считаем корреляцию Пирсона
    numeric_cols = columns_to_analyze.select_dtypes(include=[np.number])

    if not numeric_cols.empty:
        corr_matrix = numeric_cols.corr()

        # Создаем и сохраняем heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix,
                    annot=True,
                    fmt=".2f",
                    cmap='coolwarm',
                    center=0,
                    linewidths=.5)
        plt.title('Матрица корреляций')
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

        print(f'Тепловая карта сохранена в: {save_path}')
    else:
        corr_matrix = pd.DataFrame()
        print('Нет числовых столбцов для анализа корреляций')

    return corr_matrix