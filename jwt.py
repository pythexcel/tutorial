from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_current_user, verify_jwt_in_request,
    jwt_optional
)

from flask import jsonify

from functools import wraps


def init_jwt(app):
    jwt = JWTManager(app)
    # Create a function that will be called whenever create_access_token
    # is used. It will take whatever object is passed into the
    # create_access_token method, and lets us define what custom claims
    # should be added to the access token.

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user["id"]

    @jwt.user_loader_callback_loader
    def user_loader_callback(identity):
        users = app.config["users"]
        users = [user for user in users if user["id"] == identity]
        if len(users) > 0:
            if users[0]["username"] == "manish":
                users[0]["role"] = "admin"
            else:
                users[0]["role"] = "normal"
            return users[0]
        return {}

    return jwt


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_current_user()
        if user["username"] == "manish":
            return fn(*args, **kwargs)

        return jsonify(msg='Admins only!'), 403
    return wrapper
