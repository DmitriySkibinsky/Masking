from faker import Faker
import asyncio

async def generate_phone_number(locale='ru_RU', numerify=False, ex='79'):
    try:
        fake = Faker(locale)
        
        if numerify:
            # Кастомный шаблон с переданным префиксом (ex)
            # Например: ex='79' => '790' => +7 90# ### ## ##
            template = ex + '#########'
            phone = fake.numerify(template)
        else:
            # Стандартный формат из локали
            phone = fake.phone_number()
        
        return phone

    except Exception as e:
        return f"Ошибка: {e}"

# async def main():
#     print(await generate_phone_number())  # Стандартный номер ru_RU
#     print(await generate_phone_number(numerify=True, ex='78'))  # Кастомный номер с шаблоном
#     print(await generate_phone_number(locale='en_US'))  # США
#     print(await generate_phone_number(numerify=True, ex='38099'))  # Украина, пример

# asyncio.run(main())
