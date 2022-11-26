import logging

from flask import Flask
from flask_restful import Api
from flask_login import LoginManager
from data.db_session import global_init
from globals import ADDRESS
from data import users_resource, notes_resource

logging.basicConfig(level=logging.INFO, filemode='a', filename='py_log.log')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'some_secret_key'
global_init('db/news_db.db')
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)

api.add_resource(users_resource.UserListResource, '/api/v2/users')
api.add_resource(news_resource.NewsListResource, '/api/v2/news')
api.add_resource(users_resource.UserResource, '/api/v2/users/<int:user_id>')
api.add_resource(news_resource.NewsResource, '/api/v2/news/<int:news_id>')


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
