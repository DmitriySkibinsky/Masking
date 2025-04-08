from faker import Faker
import asyncio
import random

def calculate_snils_control(digits):
    total = sum((9 - i) * d for i, d in enumerate(digits))
    if total < 100:
        return total
    elif total in (100, 101):
        return 0
    else:
        remainder = total % 101
        return 0 if remainder in (100, 101) else remainder

def generate_snils():
    while True:
        digits = [random.randint(0, 9) for _ in range(9)]
        control = calculate_snils_control(digits)
        if control is not None:
            snils_num = ''.join(map(str, digits))
            return f"{snils_num[:3]}-{snils_num[3:6]}-{snils_num[6:9]} {control:02d}"

def generate_inn(is_legal_entity):
    if is_legal_entity:
        digits = [random.randint(0, 9) for _ in range(9)]
        control = (sum([v * k for v, k in zip(digits, [2, 4, 10, 3, 5, 9, 4, 6, 8])]) % 11) % 10
        digits.append(control)
        return ''.join(map(str, digits))
    else:
        digits = [random.randint(0, 9) for _ in range(10)]
        n11 = (sum([v * k for v, k in zip(digits, [7, 2, 4, 10, 3, 5, 9, 4, 6, 8])]) % 11) % 10
        digits.append(n11)
        n12 = (sum([v * k for v, k in zip(digits, [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8, 0])]) % 11) % 10
        digits.append(n12)
        return ''.join(map(str, digits))

def generate_ogrn(is_legal_entity):
    if is_legal_entity:
        digits = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(12)]
        num = int(''.join(map(str, digits)))
        control = num % 11 % 10
        return ''.join(map(str, digits)) + str(control)
    else:
        digits = [3] + [random.randint(0, 9) for _ in range(13)]
        num = int(''.join(map(str, digits)))
        control = num % 13 % 10
        return ''.join(map(str, digits)) + str(control)

def generate_kpp(region_code="77"):
    region = region_code.zfill(2)
    inspectorate = str(random.randint(1, 99)).zfill(2)
    reason = random.choice(["010", "002", "250"])
    """ 010 — основное место учета,
        002 — обособленное подразделение,
        250 — иностранная организация без филиала, и т.д.
    """
    suffix = str(random.randint(0, 9))
    return f"{region}{inspectorate}{reason}{suffix}"

async def generate_identifiers(mode='inn', is_legal_entity=False):
    try:
        fake = Faker()

        if mode == 'inn':
            return generate_inn(is_legal_entity)

        elif mode == 'okpo':
            return fake.numerify("########")

        elif mode == 'ogrn':
            return generate_ogrn(True) if is_legal_entity else None

        elif mode == 'ogrnip':
            return generate_ogrn(False) if not is_legal_entity else None

        elif mode == 'snils':
            return generate_snils()

        elif mode == 'kpp':
            return generate_kpp()

        else:
            raise ValueError("Invalid mode. Choose from 'inn', 'okpo', 'ogrn', 'ogrnip', 'snils', 'kpp'.")

    except Exception as e:
        return f"Ошибка: {e}"


# async def test():
#     print("ИНН ЮЛ:", await generate_identifiers('inn', True))
#     print("ИНН ФЛ:", await generate_identifiers('inn', False))
#     print("ОГРН:", await generate_identifiers('ogrn', True))
#     print("ОГРНИП:", await generate_identifiers('ogrnip', False))
#     print("СНИЛС:", await generate_identifiers('snils'))
#     print("КПП:", await generate_identifiers('kpp'))

# asyncio.run(test())