import logging

from flask import Flask
from flask_login import LoginManager
from flask_restful import Api

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


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
