from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, IntegerField, PasswordField, \
    StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email


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


class NotesForm(FlaskForm):
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


class EditNotesForm(NotesForm):
    submit = SubmitField('Сохранить')
