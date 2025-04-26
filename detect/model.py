import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Bidirectional, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import os

# Создание папки для результатов
os.makedirs("./res", exist_ok=True)

# Загрузка или генерация данных
try:
    df = pd.read_csv("./res/synthetic_columns.csv")
except FileNotFoundError:
    from dataset import generate_dataset
    df = generate_dataset(size_per_class=1000)
    df.to_csv("./res/synthetic_columns.csv", index=False)

# Кодирование меток
le = LabelEncoder()
df['label_enc'] = le.fit_transform(df['label'])

# Токенизация
tokenizer = Tokenizer(char_level=True)
tokenizer.fit_on_texts(df['column_name'])
X_seq = tokenizer.texts_to_sequences(df['column_name'])
X_pad = pad_sequences(X_seq, maxlen=20)

# Разделение на train/test/validation
X_train, X_test, y_train, y_test = train_test_split(
    X_pad, df['label_enc'], test_size=0.9, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(
    X_test, y_test, test_size=0.9, random_state=42)

# Улучшенная модель
model = Sequential([
    Embedding(
        input_dim=len(tokenizer.word_index) + 1,
        output_dim=128,  # Увеличена размерность
        input_length=20,
        mask_zero=True
    ),
    Bidirectional(LSTM(64, return_sequences=True)),  # Двунаправленный LSTM
    Dropout(0.4),
    Bidirectional(LSTM(32)),
    Dropout(0.3),
    Dense(128, activation='relu'),
    Dropout(0.2),
    Dense(len(le.classes_), activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Callbacks
callbacks = [
    EarlyStopping(
        monitor='val_loss',
        patience=5,  # Увеличено терпение
        restore_best_weights=True
    ),
    ModelCheckpoint(
        filepath='./res/best_model.h5',
        monitor='val_accuracy',  # Сохраняем по точности
        mode='max',
        save_best_only=True,
        verbose=1
    )
]

# Обучение
history = model.fit(
    X_train,
    y_train,
    epochs=30,  # Увеличено число эпох
    batch_size=64,
    validation_data=(X_val, y_val),
    callbacks=callbacks
)

# Оценка на тестовых данных
y_pred = model.predict(X_test)
y_pred_classes = y_pred.argmax(axis=-1)

print("Classification Report:")
print(classification_report(y_test, y_pred_classes, target_names=le.classes_))

# Сохранение
model.save("./res/column_classifier_model.h5")
pd.to_pickle(tokenizer, "./res/tokenizer.pkl")
pd.to_pickle(le, "./res/label_encoder.pkl")
pd.to_pickle(history.history, "./res/training_history.pkl")

print("Модель и вспомогательные файлы сохранены в папке ./res")