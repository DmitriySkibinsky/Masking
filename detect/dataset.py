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
    ],
    "nr_credit_account": [
        "номер кредитного договора", "номер кредитного счета", "кредитный договор номер",
        "кредитный договор №", "номер договора кредита", "кредитный аккаунт номер",
        "credit account number", "credit contract number", "номер кредита",
        "кредитный номер", "кредитный договор", "credit agreement number",
        "номер кредитного соглашения", "кредитный договор ФЛ", "кредитный договор ЮЛ",
        "номер кредитного договора ФЛ", "номер кредитного договора ЮЛ", "credit account no", "номер кредитного контракта",
        "кредитный контракт номер", "кредит договор номер", "кредит номер договора"
    ],
    "nr_bank_contract": [
        "номер банковского договора", "номер договора с банком", "банковский договор номер",
        "банковский договор №", "номер договора банка", "банковский контракт номер",
        "bank contract number", "bank agreement number", "номер банковского соглашения",
        "банковский номер договора", "договор банковского обслуживания номер",
        "номер договора обслуживания", "банковский договор ФЛ", "банковский договор ЮЛ",
        "номер банковского договора ФЛ", "номер банковского договора ЮЛ", "bank contract no",
        "bank account contract", "номер банковского контракта", "банковский контракт №",
        "договор с банком номер", "банк договор номер",
    ],
    "nr_dep_contract": [
        "номер депозитарного договора", "номер договора депозита", "депозитарный договор номер",
        "депозитарный договор №", "номер депозитного договора", "депозитный договор номер",
        "deposit contract number", "deposit agreement number", "номер депозитного соглашения",
        "депозитный номер договора", "депозитарный договор ФЛ", "deposit contract no",
        "deposit account contract", "номер депозитного контракта", "депозитный контракт номер",
        "договор депозита номер", "депозит договор номер", "депозитарный номер", "номер депозита",
        "депозитный аккаунт номер"
    ],
    "card_number": [
        "номер карты", "card number", "номер кредитки", "credit card number",
        "номер банковской карты", "card no", "card #", "cc-number", "card_num",
        "номер карточки", "дебетовая карта номер", "card digits", "payment card number",
        "cc num", "creditcard", "номер пластиковой карты", "card information",
        "card details", "номер вашей карты", "card", "cc number", "card-number",
        "bank card number", "card data", "card code", "card value", "карты", "карты банка", "дебетовые карты"
    ],
    "bank_account_number": [
        "номер счета", "account number", "номер банковского счета", "bank account number",
        "номер расчетного счета", "счет номер", "account no", "acc number", "account #",
        "bank account", "номер вашего счета", "счет", "banking account number",
        "счет в банке", "номер счета в банке", "account details", "account info",
        "номер счета клиента", "счет клиента", "номер счета карты", "banking details",
        "account digits", "account data", "bank account details", "счет для перевода",
        "номер расчетного счета", "номер счета для платежа", "счет для получения"
    ],
    "investor_code": [
        "код инвестора", "инвестиционный код", "код клиента", "инвестор ID",
        "инвестиционный идентификатор", "код участника", "код акционера",
        "инвесторский код", "идентификатор инвестора", "инвестиционный номер",
        "код для инвестирования", "инвесторский идентификатор", "номер инвестора",
        "код для клиента", "идентификационный код инвестора", "инвесторский номер"
    ]

}

def generate_dataset(size_per_class=500):
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