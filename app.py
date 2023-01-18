import logging

import requests
from flask import Flask, jsonify, redirect, render_template
from flask_login import LoginManager, current_user, login_required, \
    login_user, \
    logout_user
from flask_restful import Api, abort

from algorithms.algorithms_with_notes import EmptyParamsError, \
    get_data_by_list, \
    get_notes_by_category_name, get_notes_by_id, get_preview_and_text, \
    get_response_by_notes, get_string_list_by_data
from algorithms.algorithms_with_user import EmptyPage, ExceptionWithUser, \
    MainNotes, get_params_to_show_user, get_user_by_email, get_user_by_id
from data import notes_resource, users_resource
from data.db_session import global_init
from globals import ADDRESS, CATEGORY_LIST
from web_forms import DeleteForm, EditNotesForm, LoginForm, NotesForm, Page, \
    RegisterForm, UserForm

logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                    encoding='utf-8', format="%(levelname)s %(message)s")
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


@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)


@app.route('/notes/edit_notes/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_notes(note_id):
    ed_notes_form = EditNotesForm()
    if ed_notes_form.validate_on_submit():
        try:
            category_str_list = get_string_list_by_data(
                ed_notes_form.politic.data, ed_notes_form.technology.data,
                ed_notes_form.health.data)
        except EmptyParamsError:
            return render_template('add_notes.html',
                                   title='Редактирование новости',
                                   form=ed_notes_form,
                                   current_user=current_user,
                                   action_header='Редактирование новости',
                                   message="Пожалуйста, выберете категорию "
                                           "новости.")
        resp = requests.put(ADDRESS + f'/api/v2/notes/{note_id}',
                            json={'password': ed_notes_form.password.data,
                                  'author': current_user.email,
                                  'preview': ed_notes_form.preview.data,
                                  'category_string_list': category_str_list,
                                  'text': ed_notes_form.text.data,
                                  'header': ed_notes_form.header.data})
        resp_js = resp.json()
        if 'success' in resp_js:
            return redirect('/notes')
        elif resp_js['error'] == 'Bad user':
            ed_notes_form.password.errors = [
                'Неверный пароль. Попробуйте ещё раз.']
        elif resp_js['error'] == 'not unique header':
            ed_notes_form.header.errors = [
                'Уже есть много статей с таким заголовком, пожалуйста '
                'выберите другой.']
        elif resp_js['error'] == 'EmptyPage category':
            return render_template('add_notes.html',
                                   title='Редактирование новости',
                                   form=ed_notes_form,
                                   action_header='Редактирование новости',
                                   message='Пожалуйста, выберете хотя бы одну '
                                           'категорию своей новости.')
        else:
            return render_template('add_notes.html',
                                   title='Редактирование новости',
                                   form=ed_notes_form,
                                   action_header='Редактирование новости',
                                   message='Произошла непредвиденная ошибка, '
                                           'пожалуйста попробуйте позже.')
    notes = get_notes_by_id(note_id)
    if notes.user == current_user or current_user.position == 1:
        ed_notes_form.header.data = notes.header
        ed_notes_form.politic.data, ed_notes_form.technology.data, \
        ed_notes_form.health.data = get_data_by_list(
            notes.category)
        ed_notes_form.preview.data, ed_notes_form.text.data = \
            get_preview_and_text(
            notes.text_address)
    else:
        abort(404)
    return render_template('add_notes.html', title='Редактирование новости',
                           action_header='Редактирование новости',
                           form=ed_notes_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        try:
            user = get_user_by_email(login_form.email.data)
        except ExceptionWithUser:
            login_form.email.errors = ['Не найден такой пользователь']
            return render_template('login.html', title='Вход', form=login_form)
        if user and user.check_password(login_form.password.data):
            login_user(user, remember=login_form.remember_me.data)
            return redirect("/")
        login_form.password.errors = ["Неправильный логин или пароль"]
        return render_template('login.html', form=login_form)
    return render_template('login.html', title='Вход', form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    reg_form = RegisterForm()
    if reg_form.validate_on_submit():
        # password  similar check
        if reg_form.password.data != reg_form.password_again.data:
            reg_form.password.errors = ["Пароли не совпадают"]
            return render_template('register.html', title='Регистрация',
                                   form=reg_form)
        resp = requests.post(ADDRESS + '/api/v2/users',
                             json={'name': reg_form.name.data,
                                   'surname': reg_form.surname.data,
                                   'age': reg_form.age.data,
                                   'address': reg_form.address.data,
                                   'email': reg_form.email.data,
                                   'password': reg_form.password.data})
        if 'success' in resp.json():
            return redirect('/login')
        else:
            resp_js = resp.json()
            er = True
            match resp_js['error']:
                case 'EmailLetterError':
                    reg_form.email.errors = [
                        'Email может состоять из английских букв, цифр и '
                        'других '
                        'символов']
                case 'EnglishError':
                    reg_form.email.errors = [
                        'Email может состоять из английских букв, цифр и '
                        'других '
                        'символов']
                case 'OthersLettersError':
                    reg_form.email.errors = [
                        'Email должен содержать другие символы']
                case 'SimilarUserError':
                    reg_form.email.errors = ["Такой пользователь уже есть"]
                case 'PasswordLetterError':
                    reg_form.password.errors = [
                        'В пароле должны присутствовать строчные и прописные '
                        'буквы.']
                case 'LengthError':
                    reg_form.password.errors = [
                        'В пароле должно быть 8 и больше символов.']
                case 'LanguageError':
                    reg_form.password.errors = [
                        'В пароле должны быть только буквы английского языка, '
                        'цифры и другие символы.']
                case 'DigitError':
                    reg_form.password.errors = ['В пароле должны быть цифры.']
                case 'SequenceError':
                    reg_form.password.errors = [
                        'В пароле не должно быть трёх символов, идущих подряд '
                        'на '
                        'клавиатуре.']
                case 'AgeRangeError':
                    reg_form.age.errors = [
                        'Возраст должен быть натуральным числом от 6 до 110']
                case 'ValueAgeError':
                    reg_form.age.errors = [
                        'Возраст должен быть натуральным числом от 6 до 110']
                case _:
                    er = False
            if er:
                return render_template('register.html', title='Регистрация',
                                       form=reg_form)
            else:
                return render_template('register.html', title='Регистрация',
                                       form=reg_form,
                                       message='Произошла ошибка. Проверьте '
                                               'данные ещё раз.')
    return render_template('register.html', title='Регистрация', form=reg_form)


@app.route('/users/<int:user_id>', methods=['GET', 'POST'])
def show_users_data(user_id):
    user_form = UserForm()
    if user_form.validate_on_submit():
        user = get_user_by_id(user_id)
        resp = requests.put(ADDRESS + f'/api/v2/users/{user_id}',
                            json={'name': user_form.name.data,
                                  'surname': user_form.surname.data,
                                  'age': user_form.age.data,
                                  'address': user_form.address.data,
                                  'email': user.email,
                                  'password': user_form.password.data,
                                  'new_password': user_form.new_password.data,
                                  'old_password': user_form.old_password.data,
                                  'password_again':
                                      user_form.password_again.data,
                                  'position': user.position})
        if 'success' in resp.json():
            user = get_user_by_id(user_id)
            params = get_params_to_show_user(user, current_user, user_form)
            if user_form.password.data and not all(
                    [user_form.old_password.data, user_form.new_password.data,
                     user_form.password_again]):
                return render_template('show_users.html',
                                       success_load_data=True, **params)
            if all([user_form.old_password.data, user_form.new_password.data,
                    user_form.password_again]) and not user_form.password.data:
                return render_template('show_users.html',
                                       success_set_password=True, **params)
            if all([user_form.old_password.data, user_form.new_password.data,
                    user_form.password_again]) and user_form.password.data:
                return render_template('show_users.html',
                                       success_set_password=True,
                                       success_load_data=True, **params)
        else:
            user = get_user_by_id(user_id)
            resp_js = resp.json()
            er = True
            match resp_js["error"]:

                case 'EmailLetterError':
                    user_form.email.errors = [
                        'Email может состоять из английских букв, цифр и '
                        'других '
                        'символов']
                case 'EnglishError':
                    user_form.email.errors = [
                        'Email должен содержать английские буквы']
                case 'OthersLettersError':
                    user_form.email.errors = [
                        'Email должен содержать другие символы']
                case 'SimilarUserError':
                    user_form.email.errors = ["Такой пользователь уже есть"]
                case 'PasswordLetterError':
                    if user_form.password.data:
                        user_form.password.errors = [
                            'В пароле должны присутствовать строчные и '
                            'прописные '
                            'буквы.']
                    if user_form.new_password.data:
                        user_form.new_password.errors = [
                            'В пароле должны присутствовать строчные и '
                            'прописные '
                            'буквы.']
                case 'LengthError':
                    if user_form.password.data:
                        user_form.password.errors = [
                            'В пароле должно быть 8 и больше символов.']
                    if user_form.new_password.data:
                        user_form.new_password.errors = [
                            'В пароле должно быть 8 и больше символов.']
                case 'LanguageError':
                    if user_form.password.data:
                        user_form.password.errors = [
                            'В пароле должны быть только буквы английского '
                            'языка, '
                            'цифры и другие символы.']
                    if user_form.new_password.data:
                        user_form.new_password.errors = [
                            'В пароле должны быть только буквы английского '
                            'языка, '
                            'цифры и другие символы.']
                case 'DigitError':
                    if user_form.password.data:
                        user_form.password.errors = [
                            'В пароле должны быть цифры.']
                    if user_form.new_password.data:
                        user_form.new_password.errors = [
                            'В пароле должны быть цифры.']
                case 'SequenceError':
                    if user_form.password.data:
                        user_form.password.errors = [
                            'В пароле не должно быть трёх символов, идущих '
                            'подряд '
                            'на клавиатуре.']
                    if user_form.new_password.data:
                        user_form.new_password.errors = [
                            'В пароле не должно быть трёх символов, идущих '
                            'подряд '
                            'на клавиатуре.']
                case 'AgeRangeError':
                    user_form.age.errors = [
                        'Возраст должен быть натуральным числом от 6 до 110.']
                case 'ValueAgeError':
                    user_form.age.errors = [
                        'Возраст должен быть натуральным числом от 6 до 110.']
                case 'Bad user':
                    user_form.password.errors = [
                        'Ошибка пользователя. Попробуйте выйти и зайти снова.']
                case 'Bad password':
                    user_form.password.errors = [
                        'Ошибка пользователя. Пожалуйста, введите правильный '
                        'пароль.']
                case 'Not equal new and again':
                    user_form.password_again.errors = ['Пароли не совпадают']
                case 'Bad old password':
                    user_form.old_password.errors = [
                        'Ошибка пользователя. Пожалуйста, введите правильный '
                        'пароль.']
                case 'Not all new password':
                    user_form.old_password.errors = [
                        'Пожалуйста, заполните все поля паролей перед сменой.']
                case 'Empty passwords':
                    user_form.password.errors = [
                        'Пожалуйста, заполните это поле, если хотите изменить '
                        'свои данные']
                    user_form.old_password.errors = [
                        'Пожалуйста, заполните это поле, если сменить пароль']
                case _:
                    er = False
            params = get_params_to_show_user(user, current_user, user_form)
            if er:
                return render_template('show_users.html', **params)
            else:
                return render_template('show_users.html', **params,
                                       message='Произошла ошибка. Проверьте '
                                               'данные ещё раз.')
    else:
        user = get_user_by_id(user_id)
        params = get_params_to_show_user(user, current_user, user_form)
        if not current_user.is_authenticated and (
                user.position != 2 and user.position != 1):
            abort(404)
        if current_user.is_authenticated:
            if not (user.position == 2 or (
                    user.position == 3 and user.id == current_user.id) or (
                            current_user.position == 1)):
                abort(404)
        return render_template('show_users.html', **params)


@app.route('/notes/notes_by_author/<int:user_id>/page/<int:number>')
def show_notes_by_author(user_id, number):
    user = get_user_by_id(user_id)
    if user.position == 3:
        abort(404)
    else:
        return notes_page(notes_resp=jsonify({
            'notes': [item.to_dict(only=('id', 'header')) for item in
                      user.notes]}), by_author=True, number=number)


@login_required
@app.route('/notes/add_notes', methods=['GET', 'POST'])
def add_notes():
    notes_form = NotesForm()
    if notes_form.validate_on_submit():
        try:
            cat_str_list = get_string_list_by_data(notes_form.politic.data,
                                                   notes_form.technology.data,
                                                   notes_form.health.data)
        except EmptyParamsError:
            return render_template('add_notes.html', title='Добавление новости',
                                   form=notes_form, current_user=current_user,
                                   action_header='Добавление новости',
                                   message="Пожалуйста, выберете категорию "
                                           "новости.")
        if current_user.is_authenticated:
            resp = requests.post(ADDRESS + '/api/v2/notes',
                                 json={'author': current_user.email,
                                       'header': notes_form.header.data,
                                       'category_string_list': cat_str_list,
                                       'preview': notes_form.preview.data,
                                       'text': notes_form.text.data,
                                       'password':
                                           notes_form.password.data}).json()
            user = current_user
        else:
            resp = requests.post(ADDRESS + '/api/v2/notes',
                                 json={'author': notes_form.author.data,
                                       'header': notes_form.header.data,
                                       'category_string_list': cat_str_list,
                                       'preview': notes_form.preview.data,
                                       'text': notes_form.text.data,
                                       'password':
                                           notes_form.password.data}).json()
            user = get_user_by_email(notes_form.author.data)
        if 'success' in resp and user.position == 3:
            p = requests.put(ADDRESS + '/api/v2/users/{}'.format(user.id),
                             json={'id': user.id, 'name': user.name,
                                   'surname': user.surname, 'email': user.email,
                                   'position': 2, 'age': user.age,
                                   'address': user.address,
                                   'password': notes_form.password.data})
            if 'success' in p.json():
                return redirect('/notes')
        elif 'error' in resp:
            if resp['error'] == 'not_unique_header':
                notes_form.header.errors = [
                    'Пожалуйста, выберете другой заголовок. Этот уже занят.']
            elif resp['error'] == 'Bad user':
                notes_form.password.errors = ['Неверный пароль.']
        elif 'success' in resp and user.position != 3:
            return redirect('/notes')
        else:
            return render_template('add_notes.html', title='Добавление новости',
                                   form=notes_form, current_user=current_user,
                                   action_header='Добавление новости',
                                   message='Произошла непредвиденная ошибка, '
                                           'пожалуйста попробуйте позже.')
    return render_template('add_notes.html', title='Добавление новости',
                           action_header='Добавление новости', form=notes_form,
                           current_user=current_user)


@app.route('/notes/category/<category>/<int:number>')
def show_category_notes_page(category: str, number):
    if category not in CATEGORY_LIST:
        abort(404)
    translate = {'politic': "Политика", 'technology': "Технологии",
                 'health': "Здоровье"}
    notes_and_session = get_notes_by_category_name(category,
                                                   return_session=True)
    notes_resp = {'notes': []}
    for i in notes_and_session[0]:
        el = get_response_by_notes(i, session=notes_and_session[1]).json
        notes_resp['notes'].append(el['notes'])
    notes_resp['notes'].sort(key=lambda x: x['date_for_sort'])
    return notes_page(number=number, notes_resp=jsonify(notes_resp),
                      by_category=True, title=translate[category])


@app.route('/notes/<int:number>')
def show_notes(number):
    notes = MainNotes(number, all_categories=True)
    return render_template('show_notes.html', notes=notes, title='Новости')


@app.route('/notes/delete_notes/<int:notes_id>', methods=['GET', 'POST'])
@login_required
def delete(notes_id):
    delete_form = DeleteForm()
    if delete_form.validate_on_submit():
        s = f'/api/v2/notes/{notes_id}'
        resp_js = requests.delete(ADDRESS + s,
                                  json={'email': delete_form.email.data,
                                        'password':
                                            delete_form.password.data}).json()
        if resp_js.get('error', False):
            if resp_js['error'] == 'Bad user' or resp_js[
                'error'] == 'Bad password':
                delete_form.password.errors = ['Неверный логин или пароль']
                notes = get_notes_by_id(notes_id)
                return render_template('delete_notes.html', form=delete_form,
                                       notes_header=notes.header,
                                       title="Удаление")
            elif resp_js['error'] == 'No rights':
                abort(403)
        else:
            return redirect('/')
    else:
        notes = get_notes_by_id(notes_id)
        return render_template('delete_notes.html', form=delete_form,
                               notes_header=notes.header, title='Удаление')


@app.route('/notes/page/<int:number>')
def notes_page(number=0, notes_resp=None, by_author=False, title='Главная',
               by_category=False):
    def abort_if_page_not_found():
        abort(404)

    if notes_resp is None:
        notes = requests.get(ADDRESS + '/api/v2/notes').json()['notes']
    else:
        notes = notes_resp.json['notes']
    max_notes = len(notes)
    if max_notes == 0:
        abort_if_page_not_found()
    sp = []
    for i in range(max_notes - number * 6 - 1,
                   max_notes - number * 6 - 7 if max_notes - number * 6 - 7
                                                 >= 0 else -1,
                   -1):
        if 0 <= i < max_notes:
            sp.append(MainNotes(notes[i]['id']))
        else:
            break
    if not sp:
        abort_if_page_not_found()
    params = {'main_notes': sp[0],
              'notes2': sp[1] if len(sp) > 1 else EmptyPage(),
              'notes3': sp[2] if len(sp) > 2 else EmptyPage(),
              'notes4': sp[3] if len(sp) > 3 else EmptyPage(),
              'notes5': sp[4] if len(sp) > 4 else EmptyPage(),
              'notes6': sp[5] if len(sp) > 5 else EmptyPage(),
              'page': Page(number),
              'max_page_id': max_notes // 6 - 1 if max_notes % 6 == 0 else
              max_notes // 6,
              'by_author': by_author, 'by_category': by_category,
              'title': title}
    return render_template('notes_page.html', **params)


@app.route('/notes')
def f():
    return redirect('/')


@app.route('/')
def main():
    return notes_page()


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run()
