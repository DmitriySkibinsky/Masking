import asyncio
import os
from mask.generate_fake import fake_confident_columns
from mask.form import forma
from mask.noise import add_noise_to_csv
from mask.unconfident_type_mask import process_masking_and_regression


async def router(csv_path, mode):
    # Извлекаем имя файла и расширение
    filename = os.path.basename(csv_path)
    name, ext = os.path.splitext(filename)

    fake_filename = f'./serv/uploads/fake_{name}{ext}'
    mixed_filename = f'./serv/uploads/fake_mix_{name}{ext}'
    noised_filename = f'./serv/uploads/fake_noised_{name}{ext}'

    fake_df, conf = await fake_confident_columns(csv_path, fake_filename)
    unconf_column = forma(csv_path, conf)

    if mode == 'no':
        return  # ничего не делаем

    if mode == 'fake':
        await process_masking_and_regression(fake_filename, mixed_filename, unconf_column)

    elif mode == 'noise':
        await add_noise_to_csv(fake_filename, noised_filename, unconf_column)
