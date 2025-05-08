import asyncio
from faker import Faker


async def generate_full_name(mode='all', gender=None, locale='ru_RU'):
    try:
        print(gender)
        fake = Faker(locale)
        if gender is None:
            gender = 'male' if fake.random_int(0, 1) == 0 else 'female'

        if gender not in ('male', 'female'):
            raise ValueError("Пол должен быть 'male' или 'female'")

        if mode == 'all':
            first_name = fake.first_name_male() if gender == 'male' else fake.first_name_female()
            middle_name = fake.middle_name_male() if gender == 'male' else fake.middle_name_female()
            last_name = fake.last_name_male() if gender == 'male' else fake.last_name_female()
            return f"{last_name} {first_name} {middle_name}"

        elif mode == 'first_name':

            return fake.first_name_male() if gender == 'male' else fake.first_name_female()

        elif mode == 'last_name':
            return fake.last_name_male() if gender == 'male' else fake.last_name_female()

        elif mode == 'middle_name':
            return fake.middle_name_male() if gender == 'male' else fake.middle_name_female()

        else:
            raise ValueError("Неверный режим. Допустимые значения: 'all', 'first_name', 'last_name', 'middle_name'")
    except Exception as e:
        return f"Ошибка: {e}"

# async def main():
#     print(await generate_full_name(mode='all', gender='male'))  
#     print(await generate_full_name(mode='all', gender='female', locale='ru_RU'))
#     print(await generate_full_name(mode='first_name', gender='female', locale='en_US'))
    
# asyncio.run(main())
