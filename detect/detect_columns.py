import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from correlation import analyze_correlations
from valid import validate_column_data  # Импорт новой функции


def load_model_artifacts(model_path='./res/best_model.h5',
                         tokenizer_path='./res/tokenizer.pkl',
                         encoder_path='./res/label_encoder.pkl'):
    """Загрузка артефактов модели"""
    return {
        'model': load_model(model_path),
        'tokenizer': pd.read_pickle(tokenizer_path),
        'encoder': pd.read_pickle(encoder_path)
    }


def predict_column_type(column_name, artifacts, confidence_threshold=0.6):
    """
    Предсказание типа колонки
    Возвращает (тип, уверенность)
    """
    seq = artifacts['tokenizer'].texts_to_sequences([column_name])
    pad = pad_sequences(seq, maxlen=20)
    pred_proba = artifacts['model'].predict(pad, verbose=0)[0]

    max_proba = np.max(pred_proba)
    if max_proba < confidence_threshold:
        return "не определено", max_proba
    return artifacts['encoder'].classes_[np.argmax(pred_proba)], max_proba


def get_confidential_data_map(csv_path, confidence_threshold=0.6):
    """
    Анализ CSV файла и создание карты конфиденциальных данных
    """
    df = pd.read_csv(csv_path)
    artifacts = load_model_artifacts()

    confidential_types = ['inn', 'phone', 'first_name', 'last_name', 'middle_name', 'full_name', "year", "birth_date"]
    confidential_map = {}
    results = []

    for idx, col in enumerate(df.columns):
        try:
            pred_type, confidence = predict_column_type(col, artifacts, confidence_threshold)
            is_confidential = pred_type in confidential_types

            validation = {}
            if is_confidential:
                try:
                    validation = validate_column_data(df[col], pred_type)
                    # Если валидация не пройдена, но уверенность высокая - помечаем как подозрительный
                    status = "CONFIRMED" if validation.get('is_valid', False) else \
                        "SUSPICIOUS" if confidence > 0.7 else "REJECTED"
                except Exception as e:
                    validation = {
                        'is_valid': False,
                        'description': f"Validation error: {str(e)}",
                        'pass_rate': "0%",
                        'sample_data': []
                    }
                    status = "VALIDATION_ERROR"

            results.append({
                'column_name': col,
                'column_index': idx,
                'predicted_type': pred_type,
                'confidence': round(confidence, 4),
                'is_confidential': is_confidential,
                'validation': validation if is_confidential else None,
                'status': status if is_confidential else "NON_CONFIDENTIAL"
            })

            if is_confidential:
                confidential_map[idx] = {
                    'column_name': col,
                    'type': pred_type,
                    'confidence': round(confidence, 4),
                    'validation': validation,
                    'status': status
                }

        except Exception as e:
            print(f"Ошибка при обработке столбца {col}: {str(e)}")
            continue

    return confidential_map, pd.DataFrame(results)


def analyze_data(csv_path):
    """
    Полный анализ данных с валидацией
    """
    try:
        df = pd.read_csv(csv_path)
        confidential_map, columns_info = get_confidential_data_map(csv_path)
        non_conf_indices = [idx for idx in range(len(df.columns)) if idx not in confidential_map]
        corr_matrix = analyze_correlations(df, non_conf_indices)

        return {
            'confidential_data_map': confidential_map,
            'columns_info': columns_info,
            'correlation_analysis': corr_matrix,
            'non_confidential_columns': non_conf_indices
        }
    except Exception as e:
        print(e)


THRESHOLD = 0.6


def get_list_result(csv_path):
    analysis_results = analyze_data(csv_path)
    result_list = []

    for col_idx, info in analysis_results['confidential_data_map'].items():
        pass_rate_str = info['validation'].get('pass_rate', '0%')
        try:
            pass_rate = float(pass_rate_str.strip('%')) / 100
        except:
            pass_rate = 0.0

        prob = (info['confidence'] + pass_rate) / 2
        if prob > THRESHOLD:
            result_list.append([info['type'], col_idx, round(prob, 4)])

    return result_list, analysis_results['correlation_analysis']


if __name__ == "__main__":
    # Устанавливаем параметры отображения для Pandas
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    csv_path = 'Global_AI_Content_Impact_Dataset.csv'
    results, corr = get_list_result(csv_path)
    print(results)

    for item in results:
        print(*item)  # Распечатает тип, индекс, значение

    # Выводим матрицу корреляций полностью
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(corr)