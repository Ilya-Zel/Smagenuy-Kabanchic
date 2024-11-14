from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Конфигурация для базы данных
app.config['SECRET_KEY'] = 'your_secret_key'  # Важно использовать секретный ключ для защиты формы
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Используем SQLite для хранения данных пользователей

# Инициализация расширений
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

# Форма регистрации
class RegistrationForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

# Форма входа
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно! Вы можете войти в систему.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()  # Находим пользователя по email
        if user and bcrypt.check_password_hash(user.password, form.password.data):  # Проверка пароля
            session['user_id'] = user.id  # Сохраняем id пользователя в сессии
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('profile'))  # Перенаправляем на страницу профиля
        else:
            flash('Неверный email или пароль', 'danger')
    return render_template('login.html', form=form)

@app.route("/profile")
def profile():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему', 'warning')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])  # Получаем пользователя из сессии
    return render_template('profile.html', user=user)

@app.route("/logout")
def logout():
    session.pop('user_id', None)  # Удаляем пользователя из сессии
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('index.html')  # Главная страница

if __name__ == "__main__":
    app.run(debug=True)
