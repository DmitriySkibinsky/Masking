import asyncio
from faker import Faker
import random
import datetime

fake = Faker()

async def validate_agreement_type(agreement_type):
    """Проверка типа договора"""
    if agreement_type not in ['ФЛ', 'ЮЛ']:
        raise ValueError("Тип договора должен быть 'ФЛ' или 'ЮЛ'")

async def generate_contract_number(prefix, agreement_type):
    """Общая логика генерации номера договора"""
    await validate_agreement_type(agreement_type)

    unique_number = fake.random_number(digits=6)  # 6 цифр для уникальности
    current_year = datetime.datetime.now().year
    year = random.choice(range(current_year - 5, current_year + 1))

    return f"{prefix}-{unique_number}-{agreement_type}-{year}"

async def generate_credit_agreement_number(agreement_type='ФЛ'):
    """Генерация номера кредитного договора"""
    try:
        return generate_contract_number('КД', agreement_type)
    except Exception as e:
        print(f"Произошла ошибка при генерации номера кредитного договора: {e}")

async def generate_bank_contract_number(agreement_type='ФЛ'):
    """Генерация номера договора банковского обслуживания"""
    try:
        return generate_contract_number('НБ', agreement_type)
    except Exception as e:
        print(f"Произошла ошибка при генерации номера банковского договора: {e}")

async def generate_depository_contract_number(agreement_type='ФЛ'):
    """Генерация номера депозитарного договора"""
    try:
        return generate_contract_number('НД', agreement_type)
    except Exception as e:
        print(f"Произошла ошибка при генерации номера депозитарного договора: {e}")

async def generate_valid_card_number(bin: str = "4", length: int = 16) -> str:
    """Генерация валидного номера карты"""
    try:
        if not bin.isdigit():
            raise ValueError("БИН должен состоять только из цифр")
        if length not in (13, 16, 19):
            raise ValueError("Длина номера карты должна быть 13, 16 или 19")

        card_number = bin
        remaining_length = length - len(bin) - 1  # -1 для контрольной цифры
        card_number += fake.numerify(text="%" * remaining_length)

        total = 0
        for i, char in enumerate(card_number):
            digit = int(char)
            if i % 2 == 0:  # Удваиваем каждую вторую цифру (начиная с 0)
                doubled = digit * 2
                total += doubled if doubled < 10 else doubled - 9
            else:
                total += digit

        check_digit = (10 - (total % 10)) % 10
        card_number += str(check_digit)

        formatted_number = " ".join([card_number[i:i+4] for i in range(0, len(card_number), 4)])

        return formatted_number

    except Exception as e:
        raise ValueError(f"Ошибка генерации номера карты: {e}")

def generate_bank_account_number(agreement_type='ФЛ') -> str:
    """Генерация номера банковского счета в формате IBAN (по законам РФ)"""
    try:
        validate_agreement_type(agreement_type)

        # Код страны
        country_code = "RU"

        # Генерация контрольных цифр (в реальной жизни это вычисляется по алгоритму, но мы генерируем случайно)
        control_digits = random.randint(10, 99)

        # Генерация БИК банка (8 цифр)
        bank_bik = fake.random_number(digits=8)

        # Генерация номера счета (для ФЛ 20 цифр, для ЮЛ 20-25)
        account_number_length = 20 if agreement_type == 'ФЛ' else random.choice([20, 22, 25])
        account_number = fake.numerify(text="%" * account_number_length)

        # Формирование номера счета
        bank_account_number = f"{country_code}{control_digits:02d} {bank_bik} {account_number}"

        return bank_account_number

    except Exception as e:
        raise ValueError(f"Ошибка генерации номера банковского счета: {e}")

def generate_investor_code() -> str:
    """Генерация кода инвестора для физического лица"""
    try:
        # Код страны
        country_code = "RU"

        # Генерация кода региона (3 цифры)
        region_code = fake.random_number(digits=3)

        # Генерация уникального кода инвестора (6 цифр)
        unique_code = fake.random_number(digits=6)

        # Формирование кода инвестора
        investor_code = f"{country_code}-{region_code}-{unique_code}"

        return investor_code

    except Exception as e:
        raise ValueError(f"Ошибка генерации кода инвестора: {e}")

# async def main():
#     """Основная функция для демонстрации генерации номеров"""
#     credit_number = await generate_credit_agreement_number('ФЛ')
#     print(f"Номер кредитного договора: {credit_number}")
    
#     bank_contract_number = await generate_bank_contract_number('ЮЛ')
#     print(f"Номер банковского договора: {bank_contract_number}")
    
#     depository_contract_number = await generate_depository_contract_number('ФЛ')
#     print(f"Номер депозитарного договора: {depository_contract_number}")
    
#     card_number = await generate_valid_card_number(bin="4", length=16)
#     print(f"Номер карты: {card_number}")
    
#     bank_account_number = generate_bank_account_number('ФЛ')
#     print(f"Номер банковского счета (ФЛ): {bank_account_number}")
    
#     bank_account_number_yl = generate_bank_account_number('ЮЛ')
#     print(f"Номер банковского счета (ЮЛ): {bank_account_number_yl}")
    
#     investor_code = generate_investor_code()
#     print(f"Код инвестора (ФЛ): {investor_code}")

# # Запуск основной функции
# if __name__ == "__main__":
#     asyncio.run(main())
