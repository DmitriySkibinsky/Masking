import pandas as pd
import random

column_types = {
    "first_name": ["имя", "firstname", "first name", "имя клиента", "имя_пользователя", "client_firstname"],
    "last_name": ["фамилия", "lastname", "last name", "фамилия клиента", "user_lastname", "фамилия_пользователя"],
    "inn": ["инн", "inn", "ИНН", "user_inn", "инн_клиента", "client_inn"],
    "phone": ["телефон", "phone", "тел.", "номер телефона", "user_phone", "тел_клиента"]
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
    df.to_csv("./res/synthetic_columns.csv", index=False)
    print("Сгенерирован и сохранён: synthetic_columns.csv")