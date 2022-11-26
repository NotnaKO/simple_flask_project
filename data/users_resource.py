import logging

from flask_restful import Resource, abort
from flask import jsonify
from flask_restful import reqparse

from algorithms.algorithms_with_user import get_user_by_email, ExceptionWithUser
from algorithms.algorithms_with_user import get_user_by_id
from algorithms.checks import BadOldPasswordError, make_new_password, some_decode_errors
from algorithms.checks import NotEqualError
from data.notes import Notes
from db_session import create_session
from user import User


def abort_if_user_not_found(user_id: int):
    new_session = create_session()
    user = new_session.query(User).get(user_id)
    if not user:
        logging.warning(f"User {user_id} not found in database")
        abort(404, message=f"User {user_id} not found in database")


class UserResource(Resource):
    """User Resource in API class"""

    @staticmethod
    def get(user_id: int):
        abort_if_user_not_found(user_id)
        new_session = create_session()
        user = new_session.query(User).get(user_id)
        return jsonify(({'user': user.to_dict(
            only=('id', 'surname', 'name', 'age', 'position', 'email', 'address'))}))

    @staticmethod
    def delete(user_id: int):
        args_parser = reqparse.RequestParser()
        args_parser.add_argument('email', required=True)
        args_parser.add_argument('password', required=True)
        args = args_parser.parse_args()
        try:
            user = get_user_by_email(args['email'])
        except ExceptionWithUser:
            return jsonify({'error': 'Bad user email or password'})
        if not user.check_password(args['password']):
            logging.warning(f"Request to user with email {user.email} with incorrect password")
            return jsonify({'error': 'Bad user email or password'})
        abort_if_user_not_found(user_id)
        new_session = create_session()
        user = new_session.query(User).get(user_id)
        new_session.delete(user)
        new_session.commit()
        return jsonify({'success': 'OK'})

    @staticmethod
    def put(user_id: int):
        parser.add_argument('password')
        parser.add_argument('position', required=True)
        parser.add_argument('old_password')
        parser.add_argument('password_again')
        parser.add_argument('new_password')
        args = parser.parse_args()
        if get_user_by_email(args['email']) != get_user_by_id(user_id):
            return jsonify({'error': 'Bad user id'})
        if args['password']:
            er = some_decode_errors(args)
            if er is not True:
                return er
            user = get_user_by_email(args['email'])
            news = user.news
            if not user.check_password(args['password']):
                return jsonify({'error': 'Bad password'})
            if 'success' in UserResource.delete(user_id).json:
                new_session = create_session()
                user = User(surname=args['surname'], name=args['name'], age=args['age'],
                            email=args['email'], address=args['address'],
                            position=args['position'], id=user_id)
                new_session.add(user)
                user.set_password(args['password'])
                for n in news:
                    news = new_session.query(Notes).get(n.id)
                    user.news.append(news)
                new_session.merge(user)
                new_session.commit()
                if not any([args['old_password'], args['new_password'], args['password_again']]):
                    return jsonify({'success': 'OK'})
        if args['old_password'] and args['new_password'] and args['password_again']:
            try:
                a = make_new_password(args['old_password'], args['new_password'],
                                      args['password_again'],
                                      user=get_user_by_email(args['email']))
                if a is not True:
                    return a
            except BadOldPasswordError:
                return jsonify({'error': 'Bad old password'})
            except NotEqualError:
                return jsonify({'error': 'Not equal new and again'})
            new_session = create_session()
            user = get_user_by_id(user_id)
            user.set_password(args['new_password'])
            new_session.merge(user)
            new_session.commit()
            return jsonify({'success': 'OK'})
        if (any([args['old_password'], args['new_password'], args['password_again']]) and args[
            'password']) and not all(
                [args['old_password'], args['new_password'], args['password_again']]):
            return jsonify({'error': 'Not all new password'})
        return jsonify({'error': 'Empty passwords'})


class UserListResource(Resource):
    pass


parser = reqparse.RequestParser()
parser.add_argument('surname', required=True)
parser.add_argument('name', required=True)
parser.add_argument('age', required=True, type=int)
parser.add_argument('email', required=True)
parser.add_argument('address', required=True)
