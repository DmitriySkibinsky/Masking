import pandas as pd
import random

column_types = {
    "first_name": [
        "имя","имена", "firstname", "first name", "имя клиента", "имя_пользователя",
        "client_firstname", "name", "client_name", "username", "user_name",
        "given_name", "person_name", "contact_name", "имена"
    ],
    "last_name": [
        "фамилия", "lastname", "last name", "фамилия клиента", "user_lastname",
        "фамилия_пользователя", "surname", "family name", "family", "user_surname",
        "second_name", "family_name", "фамилии"
    ],
    "inn": [
        "инн", "inn", "ИНН", "user_inn", "инн_клиента", "client_inn", "tax",
        "tax_id", "inn_number", "inn_code", "tax_number", "tax_code",
        "identification_number", "taxpayer_id"
    ],
    "phone": [
        "телефон", "phone", "тел.", "номер телефона", "user_phone",
        "тел_клиента", "mobile_phone", "мобильный тел", "Мобильный телефон",
        "contact", "number", "num", "client_tel", "tel", "cellphone",
        "phone_number", "contact_number", "mobile", "phone_num", "whatsapp"
    ],
    "middle_name": [
        "middle_name", "отчество", "Отчество клиента", "Отч.", "middle",
        "user_middle", "user_middlename", "миддлнейм", "отчество покупателя",
        "fathers_name", "patronymic", "отч", "middle name"
    ],
    "full_name": [
        "full", "client", "клиент", "пользователь", "fio", "ФИО",
        "Фамилия Имя Отчество", "fullname", "full_name", "person",
        "contact_person", "customer_name", "complete_name"
    ],
    "snils": [
        "снилс", "snils", "СНИЛС", "номер снилс", "snils_number", "страховой номер",
        "пенсионное страхование", "пфр номер", "pfr", "пфр", "страховое свидетельство",
        "insurance_number", "pension_number", "лицевой счет пфр", "номер пфр"
    ],
    "ogrn": [
        "огрн", "ogrn", "ОГРН", "основной гос номер", "ogrn_number", "регистрационный номер",
        "номер огрн", "гос номер юрлица", "ogrn_code", "номер записи в егрюл", "егрюл номер",
        "единый госреестр", "госрегистрация", "номер регистрации", "ogrn_id"
    ],
    "kpp": [
        "кпп", "kpp", "КПП", "код причины постановки", "kpp_code", "налоговый кпп",
        "код постановки на учет", "кпп организации", "kpp_number", "кпп юрлица",
        "причина постановки", "кпп компании", "кпп фирмы", "kpp_id"
    ],
    "okpo": [
        "окпо", "okpo", "ОКПО", "общероссийский классификатор", "okpo_code", "номер окпо",
        "код окпо", "okpo_number", "классификатор предприятий", "okpo_id",
        "код организации в окпо", "okpo_org", "okpo_company"
    ],
    "ogrnip": [
        "огрнип", "ogrnip", "ОГРНИП", "огрн ип", "ogrnip_number", "огрн индивидуального предпринимателя",
        "номер огрнип", "реестр ип", "огрнип код", "ogrnip_code", "номер записи в егрип",
        "егрип номер", "огрнип ип", "ogrnip_id", "регистрационный номер ип"
    ],
    "email": [
        "email", "e-mail", "email адрес", "email address", "адрес почты", "почта", "mail",
        "электронная почта", "user_email", "email пользователя", "email клиента", "e-mail адрес",
        "contact email", "user_mail", "electronic mail", "email_пользователя", "client_email",
        "email_адрес", "email_contact", "login_email", "personal_email",
        "work_email", "business_email", "corporate_email"
    ],
    "birth_date": [
        "дата рождения", "birthdate", "birth_date", "date of birth", "др",
        "дата роджения", "birth day", "день рождения", "birthdate",
        "birth date", "dob", "дата_рождения", "birthdata", "bdate",
        "день роджения", "датарождения", "birth", "dateofbirth"
    ],
    "passport_number": [
        "номер паспорта", "passport number", "passport_no", "passport num",
        "серия и номер паспорта", "паспортные данные", "passport",
        "passport id", "passport #", "номер_паспорта", "паспорт", "passportid"
    ],
    "passport_series": [
        "серия паспорта", "passport series", "passport_series", "серия", "series", "ser"
        "passport ser", "passportseries", "серия_паспорта", "seria"
    ],
    "international_passport_number": [
        "номер загранпаспорта", "загран номер", "international passport number",
        "passport no", "номер заграничного паспорта", "загранпаспорт",
        "загран номер", "номер паспорта заграничного", "intl passport",
        "foreign passport number", "passport number", "загран"
    ]
}

def generate_dataset(size_per_class=250):
    rows = []
    for label, variations in column_types.items():
        for _ in range(size_per_class):
            value = random.choice(variations)
            noise = random.choice([
                value.lower(),
                value.upper(),
                value.title(),
                value.replace(" ", "_"),
                value.replace(" ", "").lower(),
                value.replace(" ", "-"),
                value.replace("_", ""),
            ])
            rows.append({"column_name": noise, "label": label})
    df = pd.DataFrame(rows)
    df = df.sample(frac=1).reset_index(drop=True)
    return df

if __name__ == "__main__":
    df = generate_dataset()
    df.to_csv("../detect/res/synthetic_columns.csv", index=False)
    print("Сгенерирован и сохранён: synthetic_columns.csv")