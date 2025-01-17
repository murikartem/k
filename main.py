from cachelib import FileSystemCache
from flask import Flask, render_template, request, url_for, redirect, flash, session
import sqlite3
from flask_session import Session
from datetime import timedelta

app = Flask(__name__)
app.secret_key = '1234'
app.config['SESSION_TYPE'] = 'cachelib'
app.config['SESSION_CACHELIB'] = FileSystemCache(cache_dir='flask_session', threshold=500)
Session(app)



con = sqlite3.connect('datab.db', check_same_thread=False)
cursor = con.cursor()


@app.route('/add/', methods=['POST', 'GET'])
def add_page():
    if 'login' not in session:
        flash('Необходимо авторизоваться', 'danger')
        return redirect(url_for('page_login'))
    return render_template('1.html')

@app.route('/upload/', methods=['POST'])
def upload_post():
    image = request.files.get('image')
    print(image.filename)
    print(image.name)
    print(image.content_type)
    image.save(f'static/uploads/{image.filename}')
    title = request.form['title']
    desc = request.form['description']
    cursor.execute(
        'insert into posts (title, file_name, desc) values (?, ?,  ?)',
        (title, image.filename, desc))
    con.commit()
    return redirect(url_for('main_page'))

@app.route('/', methods=['POST', 'GET'])
def main_page():
    cursor.execute('select * from posts')
    data = cursor.fetchall()
    return render_template('2.html', data=data)

@app.route('/login/', methods=['POST', 'GET'])
def login_page():
    return render_template('login.html')


@app.route('/authorization/', methods=['POST'])
def authorization():
    login = request.form['username']
    password = request.form['password']
    cursor.execute('select username, password from users where username=(?)', (login,))
    data = cursor.fetchall()
    if not data:
        flash('Неверный логин', 'danger')
        return redirect(url_for('page_login'))
    if password == data[0][1]:
        session['login'] = True  # флаг успешной авторизации
        session['username'] = login  # запоминаем имя пользователя который авторизовался
        session.permanent = True  # время сессии, если False, то сессия до перезапуска браузера
        # если True, то настраиваем время сессии (по умолчанию 31 день)
        app.permanent_session_lifetime = timedelta(minutes=1000)
        session.modified = True  # отвечает за передачу измененных переменных сессии от запроса к запросу

        flash('Вы успешно авторизовались', 'success')
        return redirect(url_for('main_page'))
    flash('Неверный пароль', 'danger')
    return redirect(url_for('page_login'))



@app.route('/register/', methods=['POST', 'GET'])
def register_page():
    return render_template('register.html')

@app.route('/save_register/', methods =['POST', 'GET'])
def save_page():
    if request.method == 'POST':
        last_name = request.form['last_name']
        name = request.form['name']
        gender = request.form['gender']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        patronymic = request.form['patronymic']
        cursor.execute('insert into users (name, last_name, gender, email, username, password, patronymic) values (?, ?, ?, ? ,? , ?, ?)', (name, last_name, gender, email, username, password, patronymic))
        con.commit()
        flash('Регистрация прошла успешно','success')
        return redirect(url_for('login_page'))

@app.route('/logout/')
def logout():
    session.clear()
    flash('Вы вышли из профиля', 'danger')
    return redirect(url_for('main_page'))

@app.route('/save_post/', methods=['POST'])
def save_post():
    file = request.files.get('image')
    title = request.form['title']
    description = request.form['description']
    url = f'static/uploads/{file.filename}'
    file.save(url)
    cursor.execute('insert into posts (title,text, image) values (?,?,?)', (title, description, url))
    con.commit()

    flash('Пост добавлен', 'success')
    return redirect(url_for('main_page'))

app.run(port = 2000, debug=True)