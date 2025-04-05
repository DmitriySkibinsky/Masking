import asyncio
from faker import Faker

fake = Faker('ru_RU')

async def generate_full_name(mode='all', gender='male'):
    try:
        if gender not in ('male', 'female'):
            raise ValueError("Пол должен быть 'male' или 'female'")

        if mode == 'all':
            first_name = fake.first_name_male() if gender == 'male' else fake.first_name_female()
            middle_name = fake.middle_name_male() if gender == 'male' else fake.middle_name_female()
            last_name = fake.last_name_male() if gender == 'male' else fake.last_name_female()
            return f"{last_name} {first_name} {middle_name}"
        
        # Имя
        elif mode == 'first_name':
            return fake.first_name_male() if gender == 'male' else fake.first_name_female()
        
        # Фамилия
        elif mode == 'last_name':
            return fake.last_name_male() if gender == 'male' else fake.last_name_female()
        
        # Отчество
        elif mode == 'middle_name':
            return fake.middle_name_male() if gender == 'male' else fake.middle_name_female()

        else:
            raise ValueError("Неверный режим. Допустимые значения: 'all', 'first_name', 'last_name', 'middle_name'")

    except Exception as e:
        return f"Ошибка: {e}"

async def main():
    print(await generate_full_name(mode='all', gender='male'))
    print(await generate_full_name(mode='all', gender='female'))
    print(await generate_full_name(mode='first_name', gender='female'))
    
asyncio.run(main())
