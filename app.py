from flask import Flask
from flask_restful import Api
from flask_login import LoginManager
from data.db_session import global_init
from globals import ADDRESS
from data import users_resource, news_resource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'some_secret_key'
global_init('db/news_db.db')
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)


# TODO: add resource to api


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
