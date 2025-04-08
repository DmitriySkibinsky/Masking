import asyncio
from faker import Faker
import random
import string

fake = Faker('ru_RU')

async def generate_passport_number():
    try:
        series = random.randint(1000, 9999)
        number = random.randint(100000, 999999)
        
        # Формирование номера паспорта с дефисом
        passport = f"{str(series)[:2]} {str(series)[2:]} {number}"
        
        return passport
    
    except Exception as e:
        print(f"Произошла ошибка при генерации номера паспорта: {e}")

async def generate_interpass_series_number():
    try:
        # Генерация серии: 2 случайные буквы с помощью Faker
        series_letters = fake.bothify(text="??", letters=string.ascii_uppercase)  # 2 случайные буквы
        
        # Генерация номера загранпаспорта: 7 случайных цифр
        number = random.randint(1000000, 9999999)
        
        # Формирование номера загранпаспорта в формате "XX№YYYYYYY"
        interpass_series_number = f"{series_letters}№{number}"
        
        return interpass_series_number
    
    except Exception as e:
        print(f"Произошла ошибка при генерации номера загранпаспорта: {e}")
        
async def generate_military_ticket_number():
    try:
        # Генерация серии: две случайные буквы русского алфавита
        series = fake.bothify(text="??", letters="АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ")
        
        # Генерация номера военного билета: 7 цифр
        number = f"{fake.random_number(digits=7):07d}"  # 7 цифр с ведущими нулями
        
        # Формирование номера военного билета в формате "XX 0999999"
        military_ticket = f"{series} {number}"
        
        return military_ticket
    
    except Exception as e:
        print(f"Произошла ошибка при генерации номера военного билета: {e}")

# Массив римских цифр от II до X
roman_numerals = ['II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']

async def generate_birth_certificate_number():
    try:
        # Генерация римской цифры от II до X
        series = random.choice(roman_numerals)
        
        # Генерация двух случайных букв русского алфавита
        letter_series = fake.bothify(text="??", letters="АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ")
        
        # Генерация уникального номера из 6 цифр
        number = f"{random.randint(0, 999999):06d}"  # 6 цифр с ведущими нулями
        
        # Формирование полного номера свидетельства о рождении
        certificate_number = f"{series}-{letter_series} № {number}"
        
        return certificate_number
    
    except Exception as e:
        print(f"Произошла ошибка при генерации номера свидетельства о рождении: {e}")

async def generate_work_book_number():
    try:
        # Генерация римской цифры от II до X
        series = random.choice(roman_numerals)

        # Генерация уникального номера из 6 цифр
        number = f"{random.randint(0, 999999):06d}"  # 6 цифр с ведущими нулями
        
        # Формирование полного номера свидетельства о рождении
        certificate_number = f"ТК-{series} № {number}"
        
        return certificate_number
    
    except Exception as e:
        print(f"Произошла ошибка при генерации номера свидетельства о рождении: {e}")

async def generate_car_license(local='ru_RU'):
    try:
        fake = Faker(local)
        license_plate = fake.license_plate()
        return license_plate
    except Exception as e:
        print(f"Произошла ошибка при генерации номера автомобиля: {e}")

# Пример использования
async def main():
    passport = await generate_passport_number()
    print(f"Номер паспорта: {passport}")
    interpass_series_number = await generate_interpass_series_number()
    print(f"Номер загранпаспорта: {interpass_series_number}")
    military_ticket = await generate_military_ticket_number()
    print(f"Номер военного билета: {military_ticket}")
    certificate_number = await generate_birth_certificate_number()
    print(f"Номер свидетельства о рождении: {certificate_number}")
    work_book = await generate_work_book_number()
    print(f"Номер трудовой книги: {work_book}")
    

# Запуск основной функции
if __name__ == "__main__":
    asyncio.run(main())
