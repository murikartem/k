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

@app.route('/authorization/', methods=['POST', 'GET'])
def authorization_page():
    login = request.form['username']
    password = request.form['password']
    cursor.execute('SELECT username, password FROM users')
    data = cursor.fetchall()
    print(login)
    print(data)
    if login in data and password in data:
        flash('Авторизация прошла успешно', 'success')
        session['login'] = True
        session['username'] = login
        session.permanent = False
        app.permanent_session_lifetime = timedelta(minutes=1)
        session.modified = True
        return redirect(url_for('main_page'))
    else:
        flash('Авторизация прошла неуспешно', 'danger')
        return redirect(url_for('login_page'))

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

app.run(debug=True)