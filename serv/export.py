import csv
from datetime import datetime
import openpyxl

def detect_column_type(values):
    """
    Определяет тип столбца на основе значений
    Возвращает: 'INTEGER', 'REAL', 'DATE', 'BOOLEAN' или 'TEXT'
    """
    int_count = date_count = bool_count = float_count = 0
    sample_size = min(100, len(values))  # Проверяем первые 100 значений

    for value in values[:sample_size]:
        if not value.strip():
            continue

        # Проверка на boolean (true/false, yes/no)
        lower_val = value.lower()
        if lower_val in ('true', 'false', 'yes', 'no', '1', '0'):
            bool_count += 1

        # Проверка на целое число
        try:
            int(value)
            int_count += 1
            continue
        except ValueError:
            pass

        # Проверка на дату
        for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S'):
            try:
                datetime.strptime(value, fmt)
                date_count += 1
                break
            except ValueError:
                pass
        else:
            # Проверка на дробное число
            try:
                float(value)
                float_count += 1
            except ValueError:
                pass

    # Определяем тип по наибольшему совпадению
    if date_count / sample_size > 0.8:
        return 'DATE'
    elif bool_count / sample_size > 0.8:
        return 'BOOLEAN'
    elif int_count / sample_size > 0.8:
        return 'INTEGER'
    elif float_count / sample_size > 0.8:
        return 'REAL'
    else:
        return 'TEXT'


def csv_to_xlsx(csv_file, xlsx_file=None):
    """
    Конвертирует CSV файл в XLSX (Excel) формат

    :param csv_file: Путь к исходному CSV файлу
    :param xlsx_file: Путь для сохранения XLSX файла (если None, заменяет расширение csv на xlsx)
    :return: Путь к сохраненному XLSX файлу
    """
    if xlsx_file is None:
        if csv_file.endswith('.csv'):
            xlsx_file = csv_file[:-4] + '.xlsx'
        else:
            xlsx_file = csv_file + '.xlsx'

    wb = openpyxl.Workbook()
    ws = wb.active

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row_idx, row in enumerate(reader, 1):
            for col_idx, value in enumerate(row, 1):
                ws.cell(row=row_idx, column=col_idx, value=value)

    # Автонастройка ширины столбцов
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Получаем букву столбца
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    wb.save(xlsx_file)
    print(f"Файл успешно конвертирован в XLSX: {xlsx_file}")
    return xlsx_file


def csv_to_smart_sql(csv_file, table_name):
    # Генерируем имя файла дампа
    sql_file = f"{table_name}_dump.sql"

    with open(csv_file, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        columns = next(csvreader)  # Заголовки столбцов

        # Собираем данные по строкам для анализа типов
        rows = list(csvreader)
        transposed = list(zip(*rows)) if rows else []

        # Определяем типы для каждого столбца
        col_types = []
        for i, col_data in enumerate(transposed):
            col_type = detect_column_type(col_data)
            col_types.append(col_type)

        with open(sql_file, 'w', encoding='utf-8') as sqlfile:
            # Создание таблицы с умными типами
            sqlfile.write(f"DROP TABLE IF EXISTS `{table_name}`;\n")
            sqlfile.write(f"CREATE TABLE `{table_name}` (\n")

            column_defs = []
            for col_name, col_type in zip(columns, col_types):
                # Для TEXT указываем максимальную длину
                if col_type == 'TEXT':
                    max_len = max((len(str(x)) for x in transposed[i] if x), default=255)
                    col_def = f"    `{col_name.strip()}` VARCHAR({min(max_len, 2000)})"
                else:
                    col_def = f"    `{col_name.strip()}` {col_type}"
                column_defs.append(col_def)

            sqlfile.write(",\n".join(column_defs))
            sqlfile.write("\n);\n\n")

            # Вставка данных с правильным форматированием
            sqlfile.write("INSERT INTO `{}` ({}) VALUES\n".format(
                table_name,
                ", ".join([f"`{col.strip()}`" for col in columns])
            ))

            for row_idx, row in enumerate(rows):
                if row_idx > 0:
                    sqlfile.write(",\n")

                values = []
                for i, value in enumerate(row):
                    if not value.strip():
                        values.append("NULL")
                        continue

                    col_type = col_types[i]

                    if col_type == 'INTEGER':
                        values.append(value)
                    elif col_type == 'REAL':
                        values.append(value.replace(',', '.'))  # Для чисел с запятой
                    elif col_type == 'DATE':
                        # Приводим дату к SQL формату
                        for fmt in ('%d.%m.%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S'):
                            try:
                                dt = datetime.strptime(value, fmt)
                                values.append(f"'{dt.strftime('%Y-%m-%d')}'")
                                break
                            except ValueError:
                                pass
                        else:
                            values.append(f"'{value}'")  # Оставляем как есть, если формат не распознан
                    elif col_type == 'BOOLEAN':
                        lower_val = value.lower()
                        if lower_val in ('true', 'yes', '1'):
                            values.append("TRUE")
                        else:
                            values.append("FALSE")
                    else:  # TEXT и другие
                        value = value.replace("'", "''")
                        values.append(f"'{value}'")

                sqlfile.write(f"({', '.join(values)})")

            sqlfile.write(";\n")

    print(f"SQL дамп успешно создан: {sql_file}")


# Использование (теперь указываем только CSV и имя таблицы)
# csv_to_smart_sql('soil_pollution_diseases.csv', 'smart_table')
csv_to_xlsx('soil_pollution_diseases.csv')