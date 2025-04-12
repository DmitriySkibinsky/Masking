import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

# Загрузка модели и вспомогательных объектов
model = load_model("./res/column_classifier_model.h5")
tokenizer = pd.read_pickle("./res/tokenizer.pkl")
le = pd.read_pickle("./res/label_encoder.pkl")
history = pd.read_pickle("./res/training_history.pkl")

# Функция предсказания
def predict_column_type(column_name):
    seq = tokenizer.texts_to_sequences([column_name])
    pad = pad_sequences(seq, maxlen=20)
    pred = model.predict(pad, verbose=0)
    return le.classes_[pred.argmax()]

# Загрузка тестовых данных для оценки
df = pd.read_csv("./res/synthetic_columns.csv")
X_seq = tokenizer.texts_to_sequences(df['column_name'])
X_pad = pad_sequences(X_seq, maxlen=20)
y_true = le.transform(df['label'])

# Получение предсказаний
y_pred = model.predict(X_pad)
y_pred_labels = le.classes_[y_pred.argmax(axis=1)]

# Построение графиков обучения
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(history['accuracy'], label='Точность на обучении')
plt.plot(history['val_accuracy'], label='Точность на валидации')
plt.title('Точность модели')
plt.ylabel('Точность')
plt.xlabel('Эпоха')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history['loss'], label='Ошибка на обучении')
plt.plot(history['val_loss'], label='Ошибка на валидации')
plt.title('Ошибка модели')
plt.ylabel('Ошибка')
plt.xlabel('Эпоха')
plt.legend()

plt.tight_layout()
plt.savefig('./res/training_history.png')
plt.close()

# Матрица ошибок
cm = confusion_matrix(df['label'], y_pred_labels)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=le.classes_,
            yticklabels=le.classes_)
plt.title('Матрица ошибок')
plt.ylabel('Истинные значения')
plt.xlabel('Предсказанные значения')
plt.tight_layout()
plt.savefig('./res/confusion_matrix.png')
plt.close()

print("Графики сохранены в папке ./res:")
print("- training_history.png")
print("- confusion_matrix.png")

# Примеры предсказаний
test_cases = [
    "user_inn",
    "client_firstname",
    "user_lastname",
    "phone_number",
    "inn_client"
]

print("\nПримеры предсказаний:")
for case in test_cases:
    prediction = predict_column_type(case)
    print(f"'{case}' → {prediction}")