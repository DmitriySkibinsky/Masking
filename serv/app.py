from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'smart_masking'

# Конфигурация загрузки (абсолютный путь)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'xlsx', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_uploaded_file(filepath):
    print(f"Файл {filepath} готов к обработке!")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не найден в запросе', 'error')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('Файл не выбран!', 'error')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Допустимы только .xlsx и .csv!', 'error')
            return redirect(request.url)

        try:
            # Создаём папку, если её нет
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            print(f"Файл сохранён: {filepath}")  # Отладочный вывод
            process_uploaded_file(filepath)
            flash('Файл успешно загружен!', 'success')
            return redirect(url_for('upload_file'))
        except Exception as e:
            print(f"Ошибка: {e}")
            flash(f'Ошибка загрузки: {e}', 'error')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)