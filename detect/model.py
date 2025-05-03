import pandas as pd
import numpy as np
import random
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import class_weight
from sklearn.metrics import classification_report
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.layers import Input, Embedding, Conv1D, GlobalMaxPooling1D, Dense, Dropout
from tensorflow.keras.models import Model
import os
import pickle

# Создание папки для результатов
os.makedirs("./res", exist_ok=True)

# Аугментация текста
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

# Препроцессинг
def preprocess_text(text):
    return f'^{str(text).lower().strip()}$'

# Загрузка/генерация данных
try:
    df = pd.read_csv("./res/synthetic_columns.csv")
except FileNotFoundError:
    from dataset import generate_dataset
    df = generate_dataset(size_per_class=1000)
    df.to_csv("./res/synthetic_columns.csv", index=False)

df['column_name'] = df['column_name'].apply(preprocess_text).apply(augment_text)

# Кодировка меток
le = LabelEncoder()
df['label_enc'] = le.fit_transform(df['label'])

# Токенизация
tokenizer = Tokenizer(char_level=True, oov_token='<OOV>')
tokenizer.fit_on_texts(df['column_name'])
X_seq = tokenizer.texts_to_sequences(df['column_name'])
max_len = 15
X_pad = pad_sequences(X_seq, maxlen=max_len, padding='post', truncating='post')

# Разделение
X_train, X_test, y_train, y_test = train_test_split(X_pad, df['label_enc'], test_size=0.2, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_test, y_test, test_size=0.5, random_state=42)

# Веса классов
class_weights = class_weight.compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
class_weights = dict(enumerate(class_weights))

# === Новая модель без кастомных слоев ===
vocab_size = len(tokenizer.word_index) + 1
num_classes = len(le.classes_)

inputs = Input(shape=(max_len,))
x = Embedding(input_dim=vocab_size, output_dim=128, mask_zero=True)(inputs)
x = Conv1D(128, 3, activation='relu', padding='same')(x)
x = GlobalMaxPooling1D()(x)
x = Dropout(0.4)(x)
x = Dense(128, activation='relu')(x)
x = Dropout(0.3)(x)
x = Dense(64, activation='relu')(x)
x = Dropout(0.2)(x)
outputs = Dense(num_classes, activation='softmax')(x)

model = Model(inputs=inputs, outputs=outputs)
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Колбэки
callbacks = [
    EarlyStopping(monitor='val_accuracy', patience=10, restore_best_weights=True, mode='max'),
    ModelCheckpoint(filepath='./res/best_model.h5', monitor='val_accuracy', mode='max', save_best_only=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=1e-6, verbose=1)
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

# Предсказания
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

# Сохранение тестовых и тренировочных данных
pd.to_pickle(X_test, "./res/X_test.pkl")
pd.to_pickle(y_test, "./res/y_test.pkl")
pd.to_pickle(X_train, "./res/X_train.pkl")
pd.to_pickle(X_val, "./res/X_val.pkl")
pd.to_pickle(y_train, "./res/y_train.pkl")
pd.to_pickle(y_val, "./res/y_val.pkl")

print("Модель и вспомогательные файлы сохранены в папке ./res")
