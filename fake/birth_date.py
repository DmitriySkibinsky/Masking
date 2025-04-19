from faker import Faker
import asyncio
from datetime import date

async def generate_birth_date(locale='ru_RU', min_age=18, max_age=60, as_string=True):
    try:
        fake = Faker(locale)
        birth_date = fake.date_of_birth(minimum_age=min_age, maximum_age=max_age)
        
        if as_string:
            return birth_date.strftime('%Y-%m-%d')  # строка в формате ГГГГ-ММ-ДД
        else:
            return birth_date  # объект datetime.date

    except Exception as e:
        return f"Ошибка: {e}"

#
# async def main():
#     print(await generate_birth_date())
#     print(await generate_birth_date(min_age=25, max_age=30))
#     print(await generate_birth_date(locale='en_US', as_string=False))
#
# asyncio.run(main())
