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


async def generate_address(mode='all', local='ru_RU'):
    """
    Генерирует фейковые адресные данные с поддержкой регионов и населенных пунктов

    Параметры:
    - local: локаль (по умолчанию 'ru_RU')
    - mode: тип данных:
      'all' - полный адрес
      'city' - город
      'state' - регион/область
      'postcode' - почтовый индекс
      'country' - страна
      'administrative' - административная единица
      'street' - улица с номером дома
      'region' - регион (область, край, республика)
      'settlement' - населенный пункт (посёлок, деревня, село)
    """
    try:
        fake = Faker(local)

        if mode == 'all':
            return fake.address()
        elif mode == 'city':
            return fake.city()
        elif mode == 'state':
            return fake.state()
        elif mode == 'postcode':
            return fake.postcode()
        elif mode == 'country':
            return fake.country()
        elif mode == 'administrative':
            return fake.administrative_unit()
        elif mode == 'street':
            return fake.street_address()
        elif mode == 'region':
            # Для России возвращает области/края/республики
            return fake.region() if hasattr(fake, 'region') else fake.administrative_unit()
        elif mode == 'settlement':
            # Для населенных пунктов (не городов)
            if local == 'ru_RU':
                return fake.military_ship() if hasattr(fake, 'military_ship') else fake.small_community()
            return fake.city()  # Для других локалей просто город
    except Exception as e:
        print(f"Произошла ошибка при генерации адреса: {e}")
        return None

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


# async def main():
#     print(await generate_login())
#     print(await generate_legal_entity())
#     print(await generate_legal_entity(local='ru_RU', opfs=['OOO', 'ОА']))
#     print(await generate_address())
#     print(await generate_address(mode='administrative'))
#
# asyncio.run(main())


