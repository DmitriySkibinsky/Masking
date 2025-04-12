import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Embedding, Dense, GlobalAveragePooling1D
import os

# Создание папки для результатов, если её нет
os.makedirs("./res", exist_ok=True)

# Загрузка или генерация данных
try:
    df = pd.read_csv("./res/synthetic_columns.csv")
except FileNotFoundError:
    from dataset import generate_dataset
    df = generate_dataset()
    df.to_csv("./res/synthetic_columns.csv", index=False)

# Кодирование меток
le = LabelEncoder()
df['label_enc'] = le.fit_transform(df['label'])

# Токенизация
tokenizer = Tokenizer(char_level=True)
tokenizer.fit_on_texts(df['column_name'])
X_seq = tokenizer.texts_to_sequences(df['column_name'])
X_pad = pad_sequences(X_seq, maxlen=20)

# Разделение на train/test
X_train, X_test, y_train, y_test = train_test_split(X_pad, df['label_enc'], test_size=0.2, random_state=42)

# Модель
model = Sequential([
    Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=32, input_length=20),
    GlobalAveragePooling1D(),
    Dense(64, activation='relu'),
    Dense(len(le.classes_), activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Обучение модели
history = model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test))

# Сохранение модели и вспомогательных объектов
model.save("./res/column_classifier_model.h5")
pd.to_pickle(tokenizer, "./res/tokenizer.pkl")
pd.to_pickle(le, "./res/label_encoder.pkl")
pd.to_pickle(history.history, "./res/training_history.pkl")

print("Модель и вспомогательные файлы сохранены в папке ./res")