import os

from flask import jsonify
from flask_restful import abort

from data.category import Category
from data.db_session import create_session
from data.notes import Notes
from data.user import User
from globals import CATEGORY_LIST, CHECK_MAIN_LIST, MAX_LEN_CATEGORY, SEPARATOR


class NotesError(Exception):
    pass


class EmptyParamsError(NotesError):
    pass


class BigLenCategoryError(NotesError):
    pass


class NotUniqueCategoryError(NotesError):
    pass


class BadCategoryError(NotesError):
    pass


def abort_if_notes_not_found(notes_id, session=False):
    if not session:
        session = create_session()
    notes = session.query(Notes).get(notes_id)
    if not notes:
        abort(404)


def get_notes_by_id(ids, session=False):
    if not session:
        session = create_session()
    return session.query(Notes).get(ids)


def get_preview_and_text(text_address: str):
    n = text_address
    with open('notes/{}'.format(n), encoding='utf-8') as file:
        s = file.read()
    return s.split(SEPARATOR)


def get_string_list_by_data(politic=False, technology=False, health=False):
    sp = list()
    if not any([politic, technology, health]):
        raise EmptyParamsError
    if politic:
        sp.append('politic')
    if technology:
        sp.append('technology')
    if health:
        sp.append('health')
    return ','.join(sp)


def get_data_by_list(sp: list, named=False):
    if not named:
        res = [False, False, False]
        for i in sp:
            if i.name == 'politic':
                res[0] = True
            elif i.name == 'health':
                res[2] = True
            elif i.name == 'technology':
                res[1] = True
        if res:
            return res
        else:
            raise BadCategoryError
    else:
        return ','.join(map(lambda x: x.name, sp))


def get_notes_by_category_name(category_name: str, return_session=False):
    session = create_session()
    notes = session.query(Notes).join(Notes.category).filter(
        Category.name == category_name).all()
    if not return_session:
        return notes
    else:
        return notes, session


def get_response_by_notes(notes, auth=None, session=None):
    if not session:
        session = create_session()
    if not auth:
        auth = session.query(User).get(notes.author)
    d = {'notes': notes.to_dict(only=('id', 'header', 'modified_date'))}
    d['notes']['all_categories'] = get_data_by_list(notes.category, True).split(
        ',')
    try:
        d['notes']['main_category'] = get_main_cat_notes_of_string_list(
            get_data_by_list(notes.category, True))
    except BadCategoryError:
        return jsonify({'error': 'Bad categories'})
    d['notes']['politic'], d['notes']['technology'], d['notes'][
        'health'] = get_data_by_list(notes.category)
    d['notes']['author_surname'] = auth.surname
    d['notes']['author_name'] = auth.name
    d['notes']['author_id'] = auth.id
    d['notes']['date_for_sort'] = (
        notes.modified_date.year, notes.modified_date.month,
        notes.modified_date.day)
    with open(os.path.join('notes', notes.text_address), encoding='utf-8') as f:
        d['notes']['text'] = f.read()
    return jsonify(d)


def get_main_cat_notes_of_string_list(st: str):
    sp = st.split(',')
    for i in CHECK_MAIN_LIST:
        if i in sp:
            return i
    raise BadCategoryError


def check_category_string_list(sp: list):
    if not sp:
        raise EmptyParamsError
    if len(sp) > MAX_LEN_CATEGORY:
        raise BigLenCategoryError
    if len(set(sp)) != len(sp):
        raise NotUniqueCategoryError
    if set(sp) > CATEGORY_LIST:
        raise BadCategoryError
    return True


def get_category_by_name(name: str, session=False):
    if not session:
        session = create_session()
    cat = session.query(Category).filter(Category.name == name).first()
    return cat


def text_address_by_id(notes_id: int, session=False):
    if not session:
        session = create_session()
    notes = session.query(Notes).get(notes_id)
    return notes.text_address
