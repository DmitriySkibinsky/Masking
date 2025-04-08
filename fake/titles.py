from logging import raiseExceptions

from faker import Faker
import asyncio
import string

async def generate_login(local='ru_RU'):
    try:
        fake = Faker(local)
        login = fake.user_name()
        return login
    except Exception as e:
        print(f"Произошла ошибка при генерации логина: {e}")

async def generate_legal_entity(local='ru_RU', opfs=None):
    try:
        fake = Faker(local)
        if opfs is None:
            company_name = fake.company()
            return company_name
        else:
            if isinstance(opfs, list):
                company_name = f"{fake.random_element(opfs)} {fake.company().split(" ",1)[1]}"
                return company_name
            elif isinstance(opfs, str):
                company_name = f"{opfs} '{fake.company()}'"
                return company_name
    except Exception as e:
        print(f"Произошла ошибка при генерации имя ЮЛ: {e}")

async def generate_address(local='ru_RU', mode='all'):
    try:
        fake = Faker(local)
        if mode == 'all':
            address = fake.address()
            return address
        elif mode == 'city':
            city = fake.city()
            return city
        elif mode == 'state':
            state = fake.state()
            return state
        elif mode == 'zip':
            zip = fake.zip()
            return zip
        elif mode == 'country':
            country = fake.country()
            return country
        elif mode == 'administrative':
            unit = fake.administrative_unit
            return unit
    except Exception as e:
        print(f"Произошла ошибка при генерации адреса: {e}")

async def generate_geografic_coordinates():
    try:
        fake = Faker('ru_RU')
        latitude = fake.latitude()
        longitude = fake.longitude()
        return latitude, longitude
    except Exception as e:
        print(f"Произошла ошибка при генерации координат: {e}")

async def generate_uri():
    try:
        fake = Faker()
        uri = fake.uri()
        return uri
    except Exception as e:
        print(f"Произошла ошибка при генерации URI: {e}")

async def generate_ip(mode='v4'):
    try:
        fake = Faker('ru_RU')
        if mode == 'v4':
            ipv4 = fake.ipv4()
        elif mode == 'v6':
            ipv6 = fake.ipv6()
        else:
            print("Неверный режим для генерации IP")
    except Exception as e:
        print(f"Произошла ошибка при генерации IP: {e}")


async def main():
    print(await generate_login())
    print(await generate_legal_entity())
    print(await generate_legal_entity(local='ru_RU', opfs=['OOO', 'ОА']))
    print(await generate_address())
    print(await generate_address(mode='city'))

asyncio.run(main())


