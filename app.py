from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Задайте секретный ключ для использования сессий
db = SQLAlchemy(app)

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Создание базы данных
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    # Отображаем главную страницу с профилем пользователя, если он вошел
    user_email = session.get('user_email')
    return render_template('main.html', user_email=user_email)

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/reviews')
def reviews():
    return render_template('reviews.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_email'] = user.email  # Сохраняем электронную почту пользователя в сессии
            return redirect(url_for('home'))  # Перенаправляем на главную страницу
        else:
            return "Неверные учетные данные"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_email', None)  # Удаляем электронную почту пользователя из сессии
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
