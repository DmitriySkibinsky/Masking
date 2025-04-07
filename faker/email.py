from faker import Faker
import asyncio

async def generate_email(locale='en_US', personalized=False):
    try:
        fake = Faker(locale)
        if personalized:
            first = fake.first_name().lower()
            last = fake.last_name().lower()
            domain = fake.free_email_domain()
            return f"{first}.{last}@{domain}"
        else:
            return fake.free_email()
    except Exception as e:
        return f"Ошибка: {e}"
    
#async def main():
#    print(await generate_email())                        # случайный email
#    print(await generate_email(personalized=True))       # персонализированный
#    
#asyncio.run(main())