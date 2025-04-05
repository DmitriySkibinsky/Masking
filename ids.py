from faker import Faker
import asyncio

async def generate_identifiers(mode='inn', is_legal_entity=False):
    try:
        fake = Faker()

        if mode == 'inn':
            inn_length = 12 if is_legal_entity else 10
            return fake.numerify("############"[:inn_length])

        elif mode == 'okpo':
            return fake.numerify("########")

        elif mode == 'ogrn':
            if not is_legal_entity:
                return fake.numerify("#############")
            else:
                return None

        elif mode == 'ogrnip':
            if is_legal_entity:
                return None
            else:
                return fake.numerify("###############")

        elif mode == 'snils':
            return fake.numerify("###-###-### ##")

        elif mode == 'kpp':
            return fake.numerify("##########")
            
        else:
            raise ValueError("Invalid mode. Choose from 'inn', 'okpo', 'ogrn', 'ogrnip', 'snils', 'kpp'.")

    except Exception as e:
        return f"Ошибка: {e}"

# async def main():
#     print(await generate_identifiers(mode='inn'))
#     print(await generate_identifiers(mode='okpo'))
#     print(await generate_identifiers(mode='ogrn'))
#     print(await generate_identifiers(mode='ogrnip', is_legal_entity=False))
#     print(await generate_identifiers(mode='snils'))
#     print(await generate_identifiers(mode='kpp'))

# asyncio.run(main())
