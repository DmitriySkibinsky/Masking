from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'smart_masking'

# Конфигурация загрузки
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Проверка расширения файла
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    try:
        if request.method == 'POST':
            # Проверяем, есть ли файл в запросе
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)

            file = request.files['file']

            # Если пользователь не выбрал файл
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            try:
                # Если файл разрешен и корректен
                if file and allowed_file(file.filename):
                    # Создаем папку для загрузок, если ее нет
                    if not os.path.exists(app.config['UPLOAD_FOLDER']):
                        os.makedirs(app.config['UPLOAD_FOLDER'])

                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    flash('File successfully uploaded')
                    return redirect(url_for('upload_file'))
            except Exception as e:
                print(e)
        return render_template('index.html')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    app.run(debug=True)