from flask import Flask
from flask_pymongo import PyMongo

mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py', silent=True)

    mongo.init_app(app)

    from . import jwt
    jwt = jwt.init_jwt(app)

    print("hello py called")

    app.config["users"] = []

    from . import auth
    app.register_blueprint(auth.bp)

    from . import todo
    app.register_blueprint(todo.bp)

    return app
