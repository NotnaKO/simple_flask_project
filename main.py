import logging

from flask import Flask
from flask_login import LoginManager
from flask_restful import Api
from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, IntegerField, PasswordField, \
    StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email

from data import notes_resource, users_resource
from data.db_session import global_init

logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'some_secret_key'
global_init('db/notes_db.db')
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)

api.add_resource(users_resource.UserListResource, '/api/v2/users')
api.add_resource(notes_resource.NotesListResource, '/api/v2/notes')
api.add_resource(users_resource.UserResource, '/api/v2/users/<int:user_id>')
api.add_resource(notes_resource.NotesResource, '/api/v2/notes/<int:notes_id>')


class RegisterForm(FlaskForm):
    email = EmailField('Email(Логин)', validators=[Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль',
                                   validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class NewsForm(FlaskForm):
    author = StringField('Ваше логин')
    header = StringField('Заголовок новости', validators=[DataRequired()])
    politic = BooleanField('Политика')
    technology = BooleanField('Технологии')
    health = BooleanField('Здоровье')
    preview = TextAreaField('Описание новости', validators=[DataRequired()])
    text = TextAreaField('Текст новости', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class LoginForm(FlaskForm):
    email = EmailField('Логин', validators=[])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class UserForm(RegisterForm):
    new_password = PasswordField('Новый пароль')
    email = EmailField('Email')
    submit = submit2 = SubmitField('Сохранить')
    old_password = PasswordField('Старый пароль')
    password = PasswordField('Ваш пароль')
    password_again = PasswordField('Повторите пароль')


class DeleteForm(FlaskForm):
    email = EmailField('Логин', validators=[])
    password = PasswordField('Пароль', validators=[DataRequired()])
    accept = BooleanField('Да', validators=[DataRequired()])
    submit = SubmitField('Удалить')


class Page:
    def __init__(self, i: int):
        self.id = i


class EditNewsForm(NewsForm):
    submit = SubmitField('Сохранить')


if __name__ == '__main__':
    app.run()
