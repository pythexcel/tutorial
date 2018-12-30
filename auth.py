from flask import (
    Blueprint , request, abort, jsonify
)

import uuid

from passlib.hash import pbkdf2_sha256

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_current_user, verify_jwt_in_request,
    jwt_optional
)

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

@bp.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 500

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 500
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 500

    global users
    users = [user for user in users if user["username"] == username]

    if len(users) == 0:
        return jsonify("username failed!"), 400

    user = users[0]

    if not pbkdf2_sha256.verify(password, user["password"]):
        return jsonify("password failed!"), 400

    access_token = create_access_token(identity=user)
    return jsonify(access_token=access_token), 200

# Protect a view with jwt_required, which requires a valid access token
# in the request to access.


@bp.route('/profile', methods=['GET'])
@jwt_required
def profile():
    # Access the identity of the current user with get_current_user
    current_user = get_current_user()
    return jsonify(logged_in_as=current_user), 200
