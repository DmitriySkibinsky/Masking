from consistency import consistency
import pandas as pd
import asyncio

from detect.detect_columns import get_list_result

from detect.correlation import analyze_correlations


async def generate_fake_data(data_type, count):
    generator = consistency.get(data_type)
    if generator is None:
        return [None] * count

    results = []
    for _ in range(count):
        result = generator()
        if asyncio.iscoroutine(result):
            results.append(result)
        else:
            results.append(asyncio.sleep(0, result))  # Оборачиваем обычные значения в "awaitable"

    return await asyncio.gather(*results)



async def fake_confident_columns(csv_path, output_path="fake_data.csv"):
    # Получаем список конфиденциальных колонок
    confidential_columns, _ = get_list_result(csv_path)

    # Загружаем данные
    df = pd.read_csv(csv_path)

    # Заменяем данные в каждой конфиденциальной колонке
    for col_type, col_idx, _ in confidential_columns:
        if col_type in consistency:
            # Генерируем фейковые данные того же размера
            fake_data = await generate_fake_data(col_type, len(df))
            df.iloc[:, col_idx] = fake_data

    # Сохраняем результат
    df.to_csv(output_path, index=False)
    return df


async def main():
    csv_path = 'Global_AI_Content_Impact_Dataset.csv'
    fake_df = await fake_confident_columns(csv_path)
    print(f"Фейковые данные сохранены. Обработано {len(fake_df.columns)} колонок.")


if __name__ == "__main__":
    asyncio.run(main())