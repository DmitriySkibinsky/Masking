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
        'model': load_model("./res/column_classifier_model.h5"),
        'tokenizer': pd.read_pickle("./res/tokenizer.pkl"),
        'le': pd.read_pickle("./res/label_encoder.pkl"),
        'history': pd.read_pickle("./res/training_history.pkl"),
        'X_test': pd.read_pickle("./res/X_test.pkl"),
        'y_test': pd.read_pickle("./res/y_test.pkl")
    }


def predict_column_type(text, artifacts):
    """Предсказание типа колонки для одного значения"""
    seq = artifacts['tokenizer'].texts_to_sequences([text])
    pad = pad_sequences(seq, maxlen=20)
    pred = artifacts['model'].predict(pad, verbose=0)
    return artifacts['le'].classes_[pred.argmax()]


def save_plot_and_report(artifacts):
    """Сохранение графиков и отчетов с указанием кодировки UTF-8"""
    y_pred = artifacts['model'].predict(artifacts['X_test'])
    y_pred_labels = artifacts['le'].inverse_transform(y_pred.argmax(axis=1))
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

    # Отчет о классификации (с явным указанием кодировки UTF-8)
    report = classification_report(y_true_labels, y_pred_labels,
                                   target_names=artifacts['le'].classes_)
    with open('./res/classification_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)


def run_and_save_test_cases(artifacts):
    """Запуск и сохранение тестовых случаев с ASCII-стрелкой"""
    test_cases = [
        "user_inn", "client_inn", "inn_number", "tax_id", "inn_code", "ИНН", "Инн клиента",
        "first_name", "user_name", "name", "given_name", "clientname", "имя", "Имя клиента",
        "lastname", "family_name", "surname", "user_surname", "second_name", "Фамилия", "Фамилия клиента",
        "phone", "mobile", "telephone", "contact_number", "phone_num", "тел.", "Телефон", "Мобильный тел", "Моб. тел.",
        "user_phone", "client_tel", "cellphone", "phone_code", "whatsapp_num"
    ]

    # Используем ASCII-стрелку '->' вместо Unicode '→'
    results = []
    for case in test_cases:
        pred = predict_column_type(case, artifacts)
        results.append(f"{case.ljust(20)} -> {pred}")  # Заменяем → на ->

    with open('./res/test_cases_results.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(results))

    # Вывод в консоль с группировкой
    print("\n".join(results[:]))


if __name__ == "__main__":
    artifacts = load_artifacts()
    save_plot_and_report(artifacts)
    run_and_save_test_cases(artifacts)

    print("\nEvaluation results saved in ./res directory:")
    print("- training_metrics.png")
    print("- confusion_matrix.png")
    print("- classification_report.txt")
    print("- test_cases_results.txt")