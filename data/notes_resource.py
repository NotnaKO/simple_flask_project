import os
import random

from flask import jsonify
from flask_restful import Resource, reqparse

from algorithms.algorithms_with_notes import BadCategoryError, \
    BigLenCategoryError, EmptyParamsError, NotUniqueCategoryError, \
    abort_if_notes_not_found, check_category_string_list, \
    get_category_by_name, \
    get_response_by_notes
from algorithms.algorithms_with_user import ExceptionWithUser, check_user, \
    get_user_by_email
from algorithms.checks import check_author_by_notes_id
from data.category import Category
from data.db_session import create_session
from data.notes import Notes
from data.user import User
from globals import SEPARATOR


def get_parser() -> reqparse.RequestParser:
    parser = reqparse.RequestParser()
    parser.add_argument('author', required=True, type=str)
    parser.add_argument('header', required=True)
    parser.add_argument('category_string_list', required=True, type=str)
    parser.add_argument('preview', required=True, type=str)
    parser.add_argument('text', required=True, type=str)
    parser.add_argument('password', required=True)

    return parser


def check_sp(sp):
    try:
        check_category_string_list(sp)
    except EmptyParamsError:
        return jsonify({'error': 'Empty category'})
    except BadCategoryError:
        return jsonify({'error': 'Bad categories'})
    except BigLenCategoryError:
        return jsonify({'error': 'Big length of category'})
    except NotUniqueCategoryError:
        return jsonify({'error': 'Not unique categories'})


class NotesListResource(Resource):
    @staticmethod
    def get():
        new_session = create_session()
        notes = new_session.query(Notes).all()
        return jsonify(
            {'notes': [item.to_dict(only=('id', 'header')) for item in notes]})

    @staticmethod
    def post():
        parser = get_parser()

        args = parser.parse_args()
        new_session = create_session()
        user = get_user_by_email(args['author'], new_session)
        if not check_user(user, args['password']):
            return jsonify({'error': 'Bad user'})
        text_address = ''
        for i in range(5):
            a = args['header'] + str(user.id) + str(
                random.randint(1, 2 ** 14)) + '.txt'
            n = new_session.query(Notes).filter(Notes.text_address == a).first()
            if not n:
                text_address = a
                break
        if not text_address:
            return jsonify({'error': 'not_unique_header'})
        result = ''
        for i in text_address:
            if i.isdigit() or i.isalpha() or i == '.':
                result += i
        notes = Notes(author=user.id, header=args['header'],
                      text_address=result)
        sp = args['category_string_list'].split(',')
        for i in sp:
            cat = get_category_by_name(i.strip(), new_session)
            if cat:
                notes.category.append(cat)
            else:
                notes.category.append(Category(name=i.strip()))
        user = get_user_by_email(args['author'], new_session)
        user.notes.append(notes)
        new_session.merge(user)
        new_session.commit()
        with open(os.path.join('notes/' + result), encoding='utf-8',
                  mode='w') as text_file:
            text_file.write(args['preview'] + SEPARATOR + args['text'])
        return jsonify({'success': 'OK'})


class NotesResource(Resource):
    @staticmethod
    def get(notes_id):
        abort_if_notes_not_found(notes_id)
        new_session = create_session()
        notes = new_session.query(Notes).get(notes_id)
        auth = new_session.query(User).get(notes.author)
        return get_response_by_notes(notes, auth=auth, session=new_session)

    @staticmethod
    def delete(notes_id):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()
        new_session = create_session()
        try:
            user = get_user_by_email(args['email'], new_session)
        except ExceptionWithUser:
            return jsonify({'error': 'Bad user'})
        if not user.check_password(args['password']):
            return jsonify({'error': 'Bad password'})
        abort_if_notes_not_found(notes_id)
        notes = new_session.query(Notes).get(notes_id)
        if not check_author_by_notes_id(user, notes):
            return jsonify({'error': 'No rights'})
        os.remove(os.path.join('notes/' + notes.text_address))
        new_session.delete(notes)
        new_session.commit()
        return jsonify({'success': 'OK'})

    @staticmethod
    def put(notes_id):
        parser = get_parser()
        args = parser.parse_args()
        if not check_user(get_user_by_email(args['author']), args['password']):
            return jsonify({'error': 'Bad user'})
        abort_if_notes_not_found(notes_id)
        new_session = create_session()
        user = new_session.query(User).filter(
            User.email == args['author']).first()
        notes = new_session.query(Notes).get(notes_id)
        if not check_author_by_notes_id(user, notes):
            return jsonify({'error': 'Bad user'})
        user.notes.remove(notes)
        notes.header = args['header']
        notes.preview = args['preview']
        sp = args['category_string_list'].split(',')
        check_sp(sp)
        notes.category = []
        for i in sp:
            cat = get_category_by_name(i.strip(), new_session)
            if cat:
                notes.category.append(cat)
            else:
                notes.category.append(Category(name=i.strip()))
        user.notes.append(notes)
        new_session.merge(user)
        new_session.commit()
        with open(os.path.join('notes/' + notes.text_address), encoding='utf-8',
                  mode='w') as text_file:
            text_file.write(args['preview'] + SEPARATOR + args['text'])
        return jsonify({'success': 'OK'})
