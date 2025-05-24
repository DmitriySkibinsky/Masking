import time
import glob
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename
import shutil
import asyncio

from mask import router

# Определяем путь к папке uploads относительно текущего файла
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

# Очищаем папку uploads ДО создания Flask-приложения
if os.path.exists(UPLOAD_FOLDER):
    shutil.rmtree(UPLOAD_FOLDER)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
print(f"Папка {UPLOAD_FOLDER} успешно очищена.")

# Создаем Flask-приложение
app = Flask(__name__)
app.secret_key = 'smart_masking'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'xlsx', 'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Очищаем папку при старте приложения (работает и для `flask run`)
if os.path.exists(UPLOAD_FOLDER):
    shutil.rmtree(UPLOAD_FOLDER)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
print(f"Папка {UPLOAD_FOLDER} успешно очищена.")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


async def process_uploaded_file(filepath, mode):
    """Обработка файла в зависимости от выбранного режима"""
    try:
        await router(filepath, mode)
        return True
    except Exception as e:
        print(f"Ошибка обработки: {e}")
        return False

def get_all_files():
    """Возвращает список всех файлов в папке uploads"""
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
            files.append(filename)
    return files

def clear_upload_folder():
    """Очищает папку uploads при старте приложения"""
    if os.path.exists(UPLOAD_FOLDER):
        try:
            shutil.rmtree(UPLOAD_FOLDER)
            print(f"Папка {UPLOAD_FOLDER} успешно очищена.")
        except Exception as e:
            print(f"Ошибка при очистке папки {UPLOAD_FOLDER}: {e}")
    else:
        print(f"Папка {UPLOAD_FOLDER} не существует, создание новой.")

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/files')
def list_files():
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(filepath):
            files.append({
                'name': filename,
                'url': url_for('download_file', filename=filename),
                'size': os.path.getsize(filepath),
                'modified': os.path.getmtime(filepath)
            })
    return jsonify(files)
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не найден в запросе', 'error')
            return redirect(request.url)

        file = request.files['file']
        mode = request.form.get('mode', 'no')

        if file.filename == '':
            flash('Файл не выбран!', 'error')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Допустимы только .xlsx и .csv!', 'error')
            return redirect(request.url)

        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Запускаем обработку файла
            success = asyncio.run(process_uploaded_file(filepath, mode))

            if not success:
                flash('Ошибка при обработке файла', 'error')
                return redirect(request.url)

            # Определяем имя обработанного файла
            processed_filename = f"fake_{filename}" if mode == "fake" else filename
            processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)

            # Ждем появления файла (макс 5 секунд)
            for _ in range(10):
                if os.path.exists(processed_filepath):
                    return render_template('result.html',
                                           original_filename=filename,
                                           processed_filename=processed_filename,
                                           all_files=get_all_files())  # Добавляем список всех файлов
                time.sleep(0.5)

            flash('Файл не был создан после обработки', 'error')
            return redirect(request.url)

        except Exception as e:
            print(f"Ошибка: {e}")
            flash(f'Ошибка загрузки: {e}', 'error')
            return redirect(request.url)

    return render_template('index.html')


@app.route('/check_file/<filename>')
def check_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    exists = os.path.exists(filepath)
    return jsonify({
        'exists': exists,
        'files': get_all_files()  # Возвращаем также список всех файлов
    })


@app.route('/download/<filename>')
def download_file(filename):
    # Проверяем, что файл начинается с fake_ (главное условие)
    if not filename.startswith('fake'):
        return "Доступны только файлы с префиксом 'fake_'", 403

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return "Файл не найден", 404

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)