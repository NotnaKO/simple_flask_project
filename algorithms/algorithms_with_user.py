import logging

from sqlalchemy.orm import Session
from data.users_resource import abort_if_user_not_found
from data.db_session import create_session
from data.user import User
from email_validate import validate


def check_user(user: User, password: str) -> bool:
    if type(user) != User:
        return False
    if user.check_password(password):
        return True
    return False


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
