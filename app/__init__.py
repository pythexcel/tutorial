from flask import Flask
from flask_pymongo import PyMongo

from . import token
mongo = PyMongo()
jwt = token.create_jwt()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    print(app.instance_path)
    app.config.from_pyfile('config.py', silent=True)

    mongo.init_app(app)

    
    token.init_jwt(jwt, app)

    print("hello py called")

    app.config["users"] = []

    from app.api import auth
    app.register_blueprint(auth.bp)

    from app.api import todo
    app.register_blueprint(todo.bp)

    return app
