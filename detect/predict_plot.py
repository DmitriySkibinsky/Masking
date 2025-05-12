import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report


def load_artifacts():
    """Загрузка всех сохраненных артефактов модели"""
    return {
        'model': load_model("./res/best_model.h5"),
        'tokenizer': pd.read_pickle("./res/tokenizer.pkl"),
        'le': pd.read_pickle("./res/label_encoder.pkl"),
        'history': pd.read_pickle("./res/training_history.pkl"),
        'X_test': pd.read_pickle("./res/X_test.pkl"),
        'y_test': pd.read_pickle("./res/y_test.pkl")
    }


def predict_column_type(text, artifacts, confidence_threshold=0.5):
    """
    Предсказание типа колонки с проверкой уверенности
    Возвращает "не определено" если уверенность < confidence_threshold
    """
    seq = artifacts['tokenizer'].texts_to_sequences([text])
    pad = pad_sequences(seq, maxlen=15)
    pred_proba = artifacts['model'].predict(pad, verbose=0)[0]

    max_proba = np.max(pred_proba)
    if max_proba < confidence_threshold:
        return "не определено", max_proba
    else:
        return artifacts['le'].classes_[np.argmax(pred_proba)], max_proba


def save_plot_and_report(artifacts):
    """Сохранение графиков и отчетов"""
    y_pred_proba = artifacts['model'].predict(artifacts['X_test'])
    y_pred = np.argmax(y_pred_proba, axis=1)
    y_pred_labels = artifacts['le'].inverse_transform(y_pred)
    y_true_labels = artifacts['le'].inverse_transform(artifacts['y_test'])

    # Графики обучения
    plt.figure(figsize=(14, 6))
    plt.subplot(1, 2, 1)
    plt.plot(artifacts['history']['accuracy'], label='Training Accuracy')
    plt.plot(artifacts['history']['val_accuracy'], label='Validation Accuracy')
    plt.title('Model Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(artifacts['history']['loss'], label='Training Loss')
    plt.plot(artifacts['history']['val_loss'], label='Validation Loss')
    plt.title('Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend()
    plt.savefig('./res/training_metrics.png')
    plt.close()

    # Матрица ошибок
    plt.figure(figsize=(10, 8))
    cm = confusion_matrix(y_true_labels, y_pred_labels)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=artifacts['le'].classes_,
                yticklabels=artifacts['le'].classes_)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig('./res/confusion_matrix.png')
    plt.close()

    # Отчет о классификации
    report = classification_report(y_true_labels, y_pred_labels,
                                   target_names=artifacts['le'].classes_)
    with open('./res/classification_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)


def run_and_save_test_cases(artifacts, confidence_threshold=0.5):
    """Запуск и сохранение тестовых случаев с проверкой уверенности"""
    test_cases = [
        "user_inn", "client_inn", "inn_number", "tax_id", "inn_code",
        "first_name", "user_name", "name", "given_name", "clientname",
        "lastname", "family_name", "surname", "user_surname", "second_name",
        "phone", "mobile", "telephone", "contact_number", "phone_num", "user_phone", "client_tel", "cellphone", "phone_code", "whatsapp_num",
        "middle_name", "отчество", "отчество клиента", "отч.",
        "fullname", "Фамилия имя отчество", "ФИО", "ФИО клиента",
        "birth_date", "дата рождения", "date of birth", "др", "birth day", "день рождения", "birthdate", "birth date", "дата_рождения", "birthdata", "день роджения", "birth",
        "СНИЛС", "snils", "номер снилс", "страховой номер",
        "kpp", "КПП", "код причины постановки", "kpp_code", "налоговый кпп", "кпп организации", "kpp_number", "кпп юрлица", "причина постановки", "kpp_id"
        "огрн", "ogrn", "ОГРН", "основной гос номер", "ogrn_number", "регистрационный номер","номер огрн", "гос номер юрлица", "ogrn_code", "единый госреестр", "ogrn_id",
        "okpo", "окпо", "okpo", "ОКПО", "общероссийский классификатор", "okpo_code", "номер окпо", "классификатор предприятий", "okpo_id",
        "огрнип", "ogrnip", "ОГРНИП", "огрн ип", "ogrnip_number", "огрн индивидуального предпринимателя", "огрнип код", "ogrnip_code",
        "email", "почта", "e-mail", "почта пользователя", "mail",
        "Номер паспорта", "passport num", "паспорт", "паспортные данные", "паспорт клиента",
        "Серия паспорта", "Серия", "Series", "ser", "passport_ser",
        "Загран паспорт", "foreign passport number", "загранпаспорт", "загран", "загран номер",
        "Номер военного билета", "Военник", "Military ticket", "военник номер", "military ID",
        "билет моряка", "паспорт моряка", "морской паспорт", "seaman's passport","документ моряка", "морской билет",
        "свидетельство о рождении", "номер свидетельства о рождении", "документ о рождении", "birthday record",
        "трудовая книга", "номер трудовой книги", "номер трудовой", "трудовая кн",
        "гос номер", "номер автомобиля", "номер автомобиля", "car number", "автомобильный номер", "автомобиль",
        "ненужная информация", "неподходящая  информация", "идентификатор"
    ]

    results = []
    for case in test_cases:
        pred, proba = predict_column_type(case, artifacts, confidence_threshold)
        results.append(f"{case.ljust(20)} -> {pred} (уверенность: {proba:.2f})")

    with open('./res/test_cases_results.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(results))

    # Вывод в консоль с группировкой
    print("\nINN Predictions:")
    print("\n".join(results[:5]))
    print("\nFirst Name Predictions:")
    print("\n".join(results[5:10]))
    print("\nLast Name Predictions:")
    print("\n".join(results[10:15]))
    print("\nPhone Predictions:")
    print("\n".join(results[15:25]))
    print("\nOther Predictions:")
    print("\n".join(results[25:]))


if __name__ == "__main__":
    artifacts = load_artifacts()
    save_plot_and_report(artifacts)

    # Устанавливаем порог уверенности
    CONFIDENCE_THRESHOLD = 0.5
    print(f"\nИспользуется порог уверенности: {CONFIDENCE_THRESHOLD}")

    run_and_save_test_cases(artifacts, confidence_threshold=CONFIDENCE_THRESHOLD)

    print("\nEvaluation results saved in ./res directory:")
    print("- training_metrics.png")
    print("- confusion_matrix.png")
    print("- classification_report.txt")
    print("- test_cases_results.txt")