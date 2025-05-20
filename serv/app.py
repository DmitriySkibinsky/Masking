from flask import Flask, render_template, request, redirect, url_for, flash
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

            result = asyncio.run(process_uploaded_file(filepath, mode))

            if result:
                flash(f'Файл успешно обработан в режиме {mode}!', 'success')
            else:
                flash('Ошибка при обработке файла', 'error')

            return redirect(url_for('upload_file'))
        except Exception as e:
            print(f"Ошибка: {e}")
            flash(f'Ошибка загрузки: {e}', 'error')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)