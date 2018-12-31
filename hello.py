from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py', silent=True)

    from . import db
    mongo = db.init_db(app)

    from . import jwt
    jwt = jwt.init_jwt(app)

    print("hello py called")

    app.config["users"] = []

    from . import auth
    app.register_blueprint(auth.bp)

    from . import todo
    app.register_blueprint(todo.bp)

    return app
