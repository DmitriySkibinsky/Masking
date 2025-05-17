import aiofiles
import asyncio
import csv
import random
from collections import defaultdict

# Глобальные параметры шума
NOISE_LEVEL = 0.05
BASE_INTEGER_NOISE = 1
ROUND_NOISE_BASE = 1


async def analyze_columns(csv_path, column_indices):
    result = {
        'numeric_columns': [],
        'integer_columns': [],
        'trailing_zeros': defaultdict(list),
        'decimal_places': defaultdict(int)
    }

    async with aiofiles.open(csv_path, 'r', encoding='utf-8') as file:
        reader = await file.readlines()
        rows = [line.strip().split(',') for line in reader]
        rows = rows[1:]  # Пропускаем заголовки

    for row in rows:
        for col_idx in column_indices:
            if col_idx >= len(row):
                continue

            value = row[col_idx].strip()
            if not value:
                continue

            try:
                num = float(value.replace(',', '.'))
            except ValueError:
                continue

            if col_idx not in result['numeric_columns']:
                result['numeric_columns'].append(col_idx)

            if num.is_integer():
                if col_idx not in result['integer_columns']:
                    result['integer_columns'].append(col_idx)

                str_num = value.split('.')[0].split(',')[0]
                trailing_zeros = len(str_num) - len(str_num.rstrip('0'))
                result['trailing_zeros'][col_idx].append(trailing_zeros)
            else:
                parts = value.replace(',', '.').split('.')
                if len(parts) > 1:
                    current_places = len(parts[1])
                    if current_places > result['decimal_places'][col_idx]:
                        result['decimal_places'][col_idx] = current_places

    for col_idx in result['trailing_zeros']:
        result['trailing_zeros'][col_idx] = min(result['trailing_zeros'][col_idx])

    return result


async def process_row(row, column_indices, analysis):
    new_row = row.copy()

    for col_idx in column_indices:
        if col_idx >= len(new_row):
            continue

        value = new_row[col_idx].strip()
        if not value:
            continue

        try:
            decimal_sep = ',' if ',' in value else '.'
            num = float(value.replace(',', '.'))
        except ValueError:
            continue

        decimal_places = 0
        if col_idx not in analysis['integer_columns']:
            parts = value.replace(',', '.').split('.')
            if len(parts) > 1:
                decimal_places = len(parts[1])

        if col_idx in analysis['integer_columns']:
            if col_idx in analysis['trailing_zeros']:
                zeros = analysis['trailing_zeros'][col_idx]
                noise_magnitude = 10 ** zeros
                noise = random.choice([-1, 1]) * noise_magnitude * random.randint(1, ROUND_NOISE_BASE)
            else:
                noise = random.choice([-1, 1]) * random.randint(1, BASE_INTEGER_NOISE)
        else:
            noise = random.uniform(-1, 1) * abs(num) * NOISE_LEVEL

        noisy_num = num + noise

        if col_idx in analysis['integer_columns']:
            new_value = str(int(noisy_num))
        else:
            fmt = f"%.{decimal_places}f" % noisy_num
            new_value = fmt.replace('.', decimal_sep)

        new_row[col_idx] = new_value

    return new_row


async def add_noise_to_csv(input_path, output_path, column_indices):
    analysis = await analyze_columns(input_path, column_indices)

    async with aiofiles.open(input_path, 'r', encoding='utf-8') as infile:
        content = await infile.readlines()

    reader = [line.strip().split(',') for line in content]
    header, rows = reader[0], reader[1:]

    tasks = [process_row(row, column_indices, analysis) for row in rows]
    processed_rows = await asyncio.gather(*tasks)

    async with aiofiles.open(output_path, 'w', encoding='utf-8') as outfile:
        await outfile.write(','.join(header) + '\n')
        for row in processed_rows:
            await outfile.write(','.join(row) + '\n')


# Пример вызова:
#asyncio.run(add_noise_to_csv('fake_data.csv', 'output.csv', [2, 3]))


# Добавляем шум к столбцам 0, 1, 2 и сохраняем в новый файл
#add_noise_to_csv('fake_data.csv', 'output.csv', [2,3])