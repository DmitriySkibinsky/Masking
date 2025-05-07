from consistency import consistency
import pandas as pd
import asyncio
import chardet
from detect.detect_columns import column_detect


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
            results.append(asyncio.sleep(0, result))

    return await asyncio.gather(*results)


def detect_file_encoding(csv_path):
    with open(csv_path, 'rb') as f:
        rawdata = f.read(10000)
        return chardet.detect(rawdata)['encoding']


async def fake_confident_columns(csv_path, output_path="fake_data5.csv"):
    try:
        encoding = detect_file_encoding(csv_path)
        print(f"Определена кодировка файла: {encoding}")

        df = pd.read_csv(csv_path, encoding=encoding)
        print(f"Успешно прочитано {len(df)} строк")

        confidential_columns, _ , gender_rel = column_detect(csv_path, encoding=encoding)
        #print(gender_rel)
        print(f"Найдено конфиденциальных колонок: {len(confidential_columns)}")

        if not confidential_columns:
            print("Конфиденциальные данные не обнаружены")
            df.to_csv(output_path, index=False, encoding='utf-8')
            return df

        for col_type, col_idx, _ in confidential_columns:
            if col_type in consistency:
                print(f"Обработка колонки {col_idx} ({col_type})...")
                fake_data = await generate_fake_data(col_type, len(df))
                df.iloc[:, col_idx] = fake_data

        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"Файл успешно сохранен: {output_path}")
        return df

    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        return None


async def main():
    csv_path = 'Книга1.csv'
    print(f"Начало обработки файла: {csv_path}")
    fake_df = await fake_confident_columns(csv_path)
    if fake_df is not None:
        print("Обработка завершена успешно")
    else:
        print("Обработка завершена с ошибками")


if __name__ == "__main__":
    asyncio.run(main())
