from string import ascii_letters, printable

from email_validate import validate
from flask import jsonify

from algorithms.algorithms_with_user import UserNotFoundError, get_user_by_email
from data.user import User


class PasswordError(Exception):
    pass


class EmailError(Exception):
    pass


class LengthError(PasswordError):
    pass


class LetterError(PasswordError, EmailError):
    pass


class DigitError(PasswordError):
    pass


class SequenceError(PasswordError):
    pass


class LanguageError(PasswordError):
    pass


class EnglishError(EmailError):
    pass


class OthersLettersError(EmailError):
    pass


class SimilarUserError(EmailError):
    pass


class NotEqualError(PasswordError):
    pass


class AgeError(Exception):
    pass


class ValueAgeError(AgeError):
    pass


class AgeRangeError(AgeError):
    pass


class ValidationError(EmailError):
    pass


def hard_check_password(password: str) -> bool:
    numbers = set('1234567890')
    alphabet = "qwertyuiop+asdfghjkl;'+zxcvbnm,./".split('+')
    password_set = set(password)
    if len(password) < 8:
        raise LengthError
    if password.islower() or password.isupper():
        raise LetterError
    if not password_set.issubset(set(printable)) or not all(
            [password_set & set(ascii_letters), password_set & numbers]):
        raise LanguageError
    if not (password_set | numbers):
        raise DigitError
    for j in alphabet:
        for i in range(0, len(password) - 2, 1):
            if (password[i] + password[i + 1] + password[i + 2]).lower() in j:
                raise SequenceError
    return True


def age_check(age):
    try:
        age = int(age)
    except ValueError or TypeError:
        raise ValueAgeError
    if age < 6 or age > 110:
        raise AgeRangeError


def check_email(email: str):
    check = validate(email, check_blacklist=False, check_smtp=False)
    if not check:
        raise ValidationError
    try:
        get_user_by_email(email)
    except UserNotFoundError:
        pass
    else:
        raise SimilarUserError


def decode_password_check(password):
    try:
        check = hard_check_password(password)
        if not check:
            raise PasswordError
        else:
            return True
    except PasswordError as e:
        if isinstance(e, LetterError):
            return jsonify({'error': 'PasswordLetterError'})
        elif isinstance(e, LengthError):
            return jsonify({'error': 'LengthError'})
        elif isinstance(e, LanguageError):
            return jsonify({'error': 'LanguageError'})
        elif isinstance(e, DigitError):
            return jsonify({'error': 'DigitError'})
        elif isinstance(e, SequenceError):
            return jsonify({'error': 'SequenceError'})


def full_decode_errors(args):
    p = decode_password_check(args['password'])
    if p is not True:
        return p
    # age check
    try:
        age_check(args['age'])
    except ValueAgeError:
        return jsonify({'error': 'ValueAgeError'})
    except AgeRangeError:
        return jsonify({'error': 'AgeRangeError'})
    # email check
    try:
        check_email(args['email'])
    except LetterError:
        return jsonify({'error': 'EmailLetterError'})
    except EnglishError:
        return jsonify({'error': 'EnglishError'})
    except OthersLettersError:
        return jsonify({'error': 'OthersLettersError'})
    except SimilarUserError:
        return jsonify({'error': 'SimilarUserError'})
    except ValidationError:
        return jsonify({"error": "ValidationError"})
    return True


def some_decode_errors(args):
    a = full_decode_errors(args)
    if a is True:
        return a
    elif a.json['error'] == 'SimilarUserError':
        return True
    else:
        return a


class BadOldPasswordError(PasswordError):
    pass


def make_new_password(old, new, again, user):
    if new != again:
        raise NotEqualError
    if user.check_password(old):
        p = decode_password_check(new)
        return p
    else:
        raise BadOldPasswordError


def check_author_by_notes_id(author: User, notes) -> bool:
    if not isinstance(author, User):
        return False
    if notes not in author.notes:
        return False
    return True
