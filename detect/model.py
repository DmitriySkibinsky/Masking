import pandas as pd
import numpy as np
import random
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import class_weight
from sklearn.metrics import classification_report
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import os
import pickle

# Создание папки для результатов
os.makedirs("./res", exist_ok=True)

# Функция аугментации данных
def augment_text(text):
    if len(text) < 5:
        variants = [
            text,
            f' {text}',
            f'{text} ',
            f' {text} ',
            f'__{text}__'
        ]
        return random.choice(variants)
    return text

# Препроцессинг текста
def preprocess_text(text):
    text = str(text).lower().strip()
    return f'^{text}$'

# Загрузка или генерация данных
try:
    df = pd.read_csv("./res/synthetic_columns.csv")
except FileNotFoundError:
    from dataset import generate_dataset
    df = generate_dataset(size_per_class=1000)
    df.to_csv("./res/synthetic_columns.csv", index=False)

# Применяем препроцессинг и аугментацию
df['column_name'] = df['column_name'].apply(preprocess_text).apply(augment_text)

# Кодирование меток
le = LabelEncoder()
df['label_enc'] = le.fit_transform(df['label'])

# Токенизация
tokenizer = Tokenizer(char_level=True, oov_token='<OOV>')
tokenizer.fit_on_texts(df['column_name'])
X_seq = tokenizer.texts_to_sequences(df['column_name'])

# Параметры последовательности
max_len = 15
X_pad = pad_sequences(X_seq, maxlen=max_len, padding='post', truncating='post')

# Разделение на train/test/validation
X_train, X_test, y_train, y_test = train_test_split(
    X_pad, df['label_enc'], test_size=0.2, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(
    X_test, y_test, test_size=0.5, random_state=42)

# Вычисление весов классов
class_weights = class_weight.compute_class_weight(
    'balanced',
    classes=np.unique(y_train),
    y=y_train
)
class_weights = dict(enumerate(class_weights))

# Улучшенная модель
model = Sequential([
    Embedding(
        input_dim=len(tokenizer.word_index) + 1,
        output_dim=128,
        input_length=max_len,
        mask_zero=True
    ),
    Conv1D(128, 3, activation='relu', padding='same'),
    GlobalMaxPooling1D(),
    Dropout(0.4),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(64, activation='relu'),
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
        monitor='val_accuracy',
        patience=10,
        restore_best_weights=True,
        mode='max'
    ),
    ModelCheckpoint(
        filepath='./res/best_model.h5',
        monitor='val_accuracy',
        mode='max',
        save_best_only=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.2,
        patience=3,
        min_lr=1e-6,
        verbose=1
    )
]

# Обучение
history = model.fit(
    X_train,
    y_train,
    epochs=50,
    batch_size=32,
    validation_data=(X_val, y_val),
    callbacks=callbacks,
    class_weight=class_weights
)

# Оценка
y_pred = model.predict(X_test)
y_pred_classes = y_pred.argmax(axis=-1)

print("Classification Report:")
print(classification_report(y_test, y_pred_classes, target_names=le.classes_))

# Сохранение
model.save("./res/column_classifier_model.h5")
with open("./res/tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)
with open("./res/label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)
pd.to_pickle(history.history, "./res/training_history.pkl")

print("Модель и вспомогательные файлы сохранены в папке ./res")