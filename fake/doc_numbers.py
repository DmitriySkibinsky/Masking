import asyncio
from faker import Faker
import random
import string

fake = Faker('ru_RU')

# Номер паспорта
async def generate_passport_number() -> str:
    """
    Генерация номера паспорта РФ в формате: 'XX XX XXXXXX'
    где первые 4 цифры - серия, последние 6 - номер
    """
    try:
        series = random.randint(1000, 9999)
        number = random.randint(100000, 999999)
        return f"{series // 100} {series % 100} {number}"
    except Exception as e:
        print(f"Ошибка генерации номера паспорта: {e}")
        return "00 00 000000"

# Серия паспорта
async def generate_passport_series() -> str:
    """
    Генерация серии паспорта (первые 4 цифры)
    """
    try:
        series = random.randint(1000, 9999)
        return f"{series // 100} {series % 100}"
    except Exception as e:
        print(f"Ошибка генерации серии паспорта: {e}")
        return "00 00"

# Номер загран паспорта
async def generate_interpass_series_number():
    try:
        series_letters = fake.bothify(text="??", letters=string.ascii_uppercase)  # 2 случайные буквы
        
        number = random.randint(1000000, 9999999)
        interpass_series_number = f"{series_letters}№{number}"
        
        return interpass_series_number
    
    except Exception as e:
        print(f"Произошла ошибка при генерации номера загранпаспорта: {e}")

# Номер военного билета и билета моряка
async def generate_military_ticket_number():
    try:
        series = fake.bothify(text="??", letters="АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ")
        number = f"{fake.random_number(digits=7):07d}"  # 7 цифр с ведущими нулями
        military_ticket = f"{series} {number}"
        
        return military_ticket
    
    except Exception as e:
        print(f"Произошла ошибка при генерации номера военного билета: {e}")

# Массив римских цифр от II до X
roman_numerals = ['II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']

# Номер свидетельства о рождении
async def generate_birth_certificate_number():
    try:
        # Генерация римской цифры от II до X
        series = random.choice(roman_numerals)
        letter_series = fake.bothify(text="??", letters="АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ")
        number = f"{random.randint(0, 999999):06d}"  # 6 цифр с ведущими нулями
        certificate_number = f"{series}-{letter_series} № {number}"
        
        return certificate_number
    
    except Exception as e:
        print(f"Произошла ошибка при генерации номера свидетельства о рождении: {e}")

# Номер трудовой книжки
async def generate_work_book_number():
    try:
        series = random.choice(roman_numerals)
        number = f"{random.randint(0, 999999):06d}"  # 6 цифр с ведущими нулями
        
        certificate_number = f"ТК-{series} № {number}"
        
        return certificate_number
    
    except Exception as e:
        print(f"Произошла ошибка при генерации номера свидетельства о рождении: {e}")

# Регистрационный номер автомобиля
async def generate_car_license(local='ru_RU'):
    try:
        fake = Faker(local)
        license_plate = fake.license_plate()
        return license_plate
    except Exception as e:
        print(f"Произошла ошибка при генерации номера автомобиля: {e}")

# Серия, номер СТС транспортного средства
async def generate_car_certificate(local='ru_RU'):
    try:
        fake = Faker(local)
        letter_series = fake.bothify(text="??", letters="АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ")
        
        number_1 = f"{random.randint(0, 99):02d}"  
        number_2 = f"{random.randint(0, 999999):06d}"  # 6 цифр с ведущими нулями
        
        certificate_number = f"{number_1} {letter_series} {number_2}"
        
        return certificate_number        
    except Exception as e:
        print(f"Произошла ошибка при генерации СТС автомобиля: {e}")

# Серия, номер ПТС транспортного средства
async def generate_car_passport(local='ru_RU'):
    try:
        fake = Faker(local)
        
        letter_series = fake.bothify(text="??", letters="АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ")
        number_1 = f"{random.randint(0, 99):02d}"
        number_2 = f"{random.randint(0, 999999):06d}"  # 6 цифр с ведущими нулями
        
        # Формирование полного номера свидетельства о рождении
        certificate_number = f"{number_1} {letter_series} {number_2}"
        
        return certificate_number        
    except Exception as e:
        print(f"Произошла ошибка при генерации ПТС автомобиля: {e}")


# # Пример использования
# async def main():
#     passport = await generate_passport_number()
#     print(f"Номер паспорта: {passport}")
#     interpass_series_number = await generate_interpass_series_number()
#     print(f"Номер загранпаспорта: {interpass_series_number}")
#     military_ticket = await generate_military_ticket_number()
#     print(f"Номер военного билета: {military_ticket}")
#     certificate_number = await generate_birth_certificate_number()
#     print(f"Номер свидетельства о рождении: {certificate_number}")
#     work_book = await generate_work_book_number()
#     print(f"Номер трудовой книги: {work_book}")
#     license = await generate_car_license()
#     print(f"Номер автомобиля: {license}")
#     ctc = await generate_car_certificate()
#     print(f"CTC автомобиля: {ctc}")
#
# # Запуск основной функции
# if __name__ == "__main__":
#     asyncio.run(main())
