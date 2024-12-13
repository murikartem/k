from flask import Flask, render_template, request, url_for, redirect
import sqlite3


app = Flask(__name__)

con = sqlite3.connect('datab.db', check_same_thread=False)
cursor = con.cursor()


@app.route('/add/', methods=['POST', 'GET'])
def add_page():
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
    username = request.form['username']
    password = request.form['password']
    cursor.execute('SELECT username,passwords FROM users')
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
        return redirect(url_for('login_page'))

app.run(debug=True)