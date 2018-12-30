from flask import (
    Blueprint , request, abort, jsonify
)

import uuid

from passlib.hash import pbkdf2_sha256


bp = Blueprint('auth', __name__, url_prefix='/auth')

users = []

@bp.route('/register', methods=['POST'])
def register():
    if not request.json:
        abort(500)

    username = request.json.get("username", None)
    password = request.json.get("password", None)
    name = request.json.get("name", None)

    if username is None or password is None or name is None:
        abort(500)

    global users

    users = [user for user in users if user["username"] == username]

    if len(users) > 0:
        return jsonify("username already exists!"), 500

    id = uuid.uuid4().hex
    hash = pbkdf2_sha256.hash(password)

    users.append({
        "id": id,
        "username": username,
        "password": hash,
        "name": name
    })

    return jsonify(id)
