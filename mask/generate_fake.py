from consistency import consistency
import pandas as pd

from detect import get_list_result


def fake_confident_columns(csv_path, output_path="fake_data.csv"):
    # Получаем список конфиденциальных колонок
    confidential_columns, _ = get_list_result(csv_path)

    # Загружаем данные
    df = pd.read_csv(csv_path)

    # Заменяем данные в каждой конфиденциальной колонке
    for col_type, col_idx, _ in confidential_columns:
        if col_type in consistency:
            # Генерируем фейковые данные того же размера
            fake_data = [consistency[col_type]() for _ in range(len(df))]
            df.iloc[:, col_idx] = fake_data

    # Сохраняем результат
    df.to_csv(output_path, index=False)
    return df


if __name__ == "__main__":
    csv_path = 'Global_AI_Content_Impact_Dataset.csv'
    fake_df = fake_confident_columns(csv_path)
    print(f"Фейковые данные сохранены. Обработано {len(fake_df.columns)} колонок.")