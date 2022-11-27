import logging

import requests
from email_validate import validate
from flask_restful import abort
from sqlalchemy.orm import Session

from data.db_session import create_session
from data.user import User
from globals import ADDRESS, CATEGORY_LIST, SEPARATOR


def check_user(user: User, password: str) -> bool:
    if type(user) != User:
        return False
    if user.check_password(password):
        return True
    return False


def abort_if_user_not_found(user_id: int):
    new_session = create_session()
    user = new_session.query(User).get(user_id)
    if not user:
        logging.warning(f"User {user_id} not found in database")
        abort(404, message=f"User {user_id} not found in database")


class ExceptionWithUser(Exception):
    pass


class IncorrectEmailError(ExceptionWithUser):
    pass


class UserNotFoundError(ExceptionWithUser):
    pass


def get_user_by_email(email: str, session: None | Session = None) -> User:
    check = validate(email)
    if not check:
        s = "Trying to get user by incorrect email"
        logging.warning(s)
        raise IncorrectEmailError
    if not session:
        session = create_session()
    user = session.query(User).filter(User.email == email).first()
    if not user:
        logging.warning(f"There is no user with email: {email}")
        raise UserNotFoundError
    return user


def get_user_by_id(user_id, session=False):
    if not session:
        session = create_session()
    return session.query(User).get(user_id)


class EmptyPage:
    def __init__(self):
        self.header = ''
        self.preview, self.content = '', ''
        self.politic, self.technology, self.health = False, False, False
        self.author_surname = ''
        self.author_name = ''
        self.date = ''
        self.category = ''
        self.z = False


def get_themes(notes):
    result = []
    for i in CATEGORY_LIST:
        if i in notes:
            result.append(notes[i])
        else:
            result.append(False)
    return result


class MainNotes:
    def __init__(self, idi: int, all_categories=False):
        notes = requests.get(ADDRESS + f'/api/v2/notes/{idi}').json()['notes']
        self.header = notes['header']
        self.preview, self.content = notes['text'].split(SEPARATOR)
        self.politic, self.technology, self.health = get_themes(notes)
        self.author_surname = notes['author_surname']
        self.author_name = notes['author_name']
        self.author = notes['author_id']
        self.id = notes['id']
        self.date = notes['modified_date'].split()[0]
        self.main_category = notes['main_category']
        if all_categories:
            self.all_categories = notes['all_categories']
        self.z = True


def get_params_to_show_user(user, current_user, form, message=''):
    notes = []
    if user.position != 3:
        notes = user.notes
    params = {'title': user.surname + ' ' + user.name,
              'surname': form.surname.data if form.surname.data else
              user.surname,
              'name': form.name.data if form.name.data else user.name,
              'age': form.age.data if form.age.data else user.age,
              'address': form.address.data if form.address.data else
              user.address,
              'id': user.id,
              'current_id': current_user.id if current_user.is_authenticated
              else -1,
              'status': 'Автор' if user.position != 3 else 'Пользователь',
              'form': form, 'message': message, 'notes1': EmptyPage(),
              'notes2': EmptyPage()}
    if len(notes) >= 1:
        params['notes1'] = MainNotes(notes[-1].id)
    if len(notes) >= 2:
        params['notes2'] = MainNotes(notes[-2].id)

    return params
