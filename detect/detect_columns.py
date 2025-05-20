import pandas as pd
import numpy as np
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from detect.correlation import analyze_correlations
from detect.gender import detect_gender
from detect.valid import validate_column_data  # Импорт новой функции


def load_model_artifacts(model_path='./detect/res/best_model.h5',
                         tokenizer_path='./detect/res/tokenizer.pkl',
                         encoder_path='./detect/res/label_encoder.pkl'):
    """Загрузка артефактов модели"""
    return {
        'model': load_model(model_path),
        'tokenizer': pd.read_pickle(tokenizer_path),
        'encoder': pd.read_pickle(encoder_path)
    }


def predict_column_type(column_name, artifacts, confidence_threshold=0.6):
    """Предсказание типа колонки"""
    seq = artifacts['tokenizer'].texts_to_sequences([column_name])
    pad = pad_sequences(seq, maxlen=20)
    pred_proba = artifacts['model'].predict(pad, verbose=0)[0]

    max_proba = np.max(pred_proba)
    if max_proba < confidence_threshold:
        return "не определено", max_proba
    return artifacts['encoder'].classes_[np.argmax(pred_proba)], max_proba


def get_confidential_data_map(csv_path, model, token, encoder, encoding='utf-8', confidence_threshold=0.6):

    """Анализ CSV файла и создание карты конфиденциальных данных"""
    df = pd.read_csv(csv_path, encoding=encoding)
    print(f"Обрабатываем файл по пути: {csv_path}")  # Добавьте эту строку
    print(f"Файл существует: {os.path.exists(csv_path)}")  # Проверка существования файла
    artifacts = load_model_artifacts(model, token, encoder)

    confidential_types = ['first_name', 'last_name', 'inn', 'phone', 'middle_name', 'full_name', "snils",
                          "ogrn", "kpp", "okpo", "ogrnip", "email", "birth_date", "passport_number", "passport_series",
                          "international_passport_number", "military_ticket_num", "sailor_ticket_num", "birth_certificate_num",
                          "work_book_num", "vehicle_number", "nr_credit_account", "nr_bank_contract", "nr_dep_contract",
                          "card_number", "bank_account_number", "investor_code"]
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
                    status = "CONFIRMED" if validation.get('is_valid', False) else \
                             "SUSPICIOUS" if confidence > 0.5 else "REJECTED"
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


def analyze_data(csv_path, model, token, encoder, encoding='utf-8'):
    """Полный анализ данных с валидацией"""
    try:
        df = pd.read_csv(csv_path, encoding=encoding)
        confidential_map, columns_info = get_confidential_data_map(csv_path,model, token, encoder, encoding=encoding)
        non_conf_indices = [idx for idx in range(len(df.columns)) if idx not in confidential_map]
        corr_matrix = analyze_correlations(df, non_conf_indices)

        return {
            'confidential_data_map': confidential_map,
            'columns_info': columns_info,
            'correlation_analysis': corr_matrix,
            'non_confidential_columns': non_conf_indices
        }
    except Exception as e:
        print(f"Error in analyze_data: {str(e)}")
        return {
            'confidential_data_map': {},
            'columns_info': pd.DataFrame(),
            'correlation_analysis': None,
            'non_confidential_columns': []
        }


THRESHOLD = 0.1


def get_list_result(csv_path, model_path ,token, enconder, encoding='utf-8'):

    analysis_results = analyze_data(csv_path, model_path ,token, enconder, encoding=encoding)
    #print(analysis_results)
    result_list = []

    if analysis_results and analysis_results['confidential_data_map']:
        for col_idx, info in analysis_results['confidential_data_map'].items():
            pass_rate_str = info['validation'].get('pass_rate', '0%')
            try:
                pass_rate = float(pass_rate_str.strip('%')) / 100
            except:
                pass_rate = 0.0

            prob = (info['confidence'] + pass_rate) / 2
            if prob > THRESHOLD:
                result_list.append([info['type'], col_idx, round(prob, 4)])

    return result_list, analysis_results.get('correlation_analysis', None)

def column_detect(csv_path, encoding='utf-8',model_path='./detect/res/best_model.h5',
                         tokenizer_path='./detect/res/tokenizer.pkl',
                         encoder_path='./detect/res/label_encoder.pkl'):
    import chardet

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    with open(csv_path, 'rb') as f:
        rawdata = f.read(10000)
        encoding = chardet.detect(rawdata)['encoding']
    print(f"Определена кодировка файла: {encoding}")
    results, corr = get_list_result(csv_path, model_path=model_path, token=tokenizer_path, enconder=encoder_path, encoding=encoding)

    gender_rel = detect_gender(results, csv_path)
    print(results)
    print("------")
    print(gender_rel)

    return results, corr, gender_rel



if __name__ == "__main__":


    csv_path = '../mask/fake_data.csv'
    column_detect(csv_path)
