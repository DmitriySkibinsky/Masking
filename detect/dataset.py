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
        "contact_person", "customer_name", "complete_name", "ФИО"
    ],
    "snils": [
        "снилс", "snils", "СНИЛС", "номер снилс", "snils_number", "страховой номер",
        "пенсионное страхование", "пфр номер", "pfr", "пфр", "страховое свидетельство",
        "insurance_number", "pension_number", "лицевой счет пфр", "номер пфр"
    ],
    "ogrn": [
        "огрн", "ogrn", "ОГРН", "основной гос номер", "ogrn_number", "регистрационный номер",
        "номер огрн", "гос номер юрлица", "ogrn_code", "номер записи в егрюл", "егрюл номер",
        "единый госреестр", "госрегистрация", "номер регистрации", "ogrn_id", "регистрационный номер"
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
        "work_email", "business_email", "corporate_email", "почта пользователя"
    ],
    "passport_number": [
        "номер паспорта", "passport number", "passport_no", "passport num",
        "серия и номер паспорта", "паспортные данные", "passport",
        "passport id", "passport #", "номер_паспорта", "паспорт", "passportid", "Номер паспорта"
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
    ],
    "military_ticket_num": [
        "номер военного билета", "военный билет", "военник", "номер военника",
        "билет военный", "военный билет номер", "мilitary ticket number",
        "воен. билет", "№ военного билета", "воен. билет номер", "номер в/б", "в/б номер", "воен. билет №",
        "серия номер военного билета", "номер воен. билета", "военбилет", "номер военбилета",
        "военный билет серия", "военник номер", "мilitary ID",
        "военный документ", "документ военнослужащего"
    ],
    "sailor_ticket_num":[
        "паспорт моряка", "морской паспорт", "seaman's passport",
        "удостоверение моряка", "моряцкий паспорт", "sailor passport",
        "морское удостоверение", "паспорт моряка номер", "номер паспорта моряка",
        "seaman ticket", "морской билет", "удостоверение личности моряка",
        "моряцкий билет", "морское свидетельство", "документ моряка"
    ],
    "birth_certificate_num": [
        "свидетельство о рождении", "номер свидетельства о рождении",
        "номер св-ва о рождении", "номер св-во о рождении",
        "серия свидетельства о рождении", "серия и номер свидетельства о рождении",
        "номер св. о рождении", "дата и место рождения (из свидетельства)",
        "birth certificate", "birth cert", "свидетельство о рождении","birth cert number",
        "birth document", "certificate of birth", "birth registration number",
        "birth record", "registration of birth", "birth certificate id",
        "номер акта о рождении", "номер записи акта о рождении"
    ],
    "work_book_num": [
        "трудовая книжка", "номер трудовой книжки", "серия трудовой книжки",
        "трудовая", "трудовая кн", "номер трудовой", "номер трудовой кн",
        "номер и серия трудовой", "трудовая книжка номер", "трудовая кн номер",
        "work book", "labour book", "employment record book", "labor card",
        "work record", "employment book", "employment history", "work book id", "трудовые книги",
        "employment document", "серия и номер трудовой", "номер документа о трудоустройстве"
    ],
    "vehicle_number": [
        "госномер", "гос номер", "номер автомобиля", "регистрационный номер", "автомобиль",
        "номер машины", "гос. номер", "автомобильный номер","номера автомобилей", "госрегномер", "машина"
        "license plate", "car number", "vehicle plate", "plate number",
        "registration number", "vehicle reg. number", "car reg. number"
    ],
    "birth_date": [
        "дата рождения", "birthdate", "birth_date","birth", "date of birth", "др",
        "дата роджения", "birth day", "день рождения", "birthdate",
        "birth date", "dob", "дата_рождения", "birthdata", "bdate",
        "день роджения", "датарождения", "birth", "dateofbirth", "дни рождения"
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