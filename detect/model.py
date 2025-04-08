import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.models import Sequential
from keras.layers import Embedding, Dense, GlobalAveragePooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Загрузка данных
df = pd.read_csv("synthetic_columns.csv")

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
model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test))

# Сохранение
model.save("column_classifier_model.h5")
print("Модель обучена и сохранена: column_classifier_model.h5")

# Функция предсказания
def predict_column_type(column_name):
    seq = tokenizer.texts_to_sequences([column_name])
    pad = pad_sequences(seq, maxlen=20)
    pred = model.predict(pad)
    return le.classes_[pred.argmax()]

# Пример
print("Пример предсказания: 'user_inn' →", predict_column_type("user_inn"))