import datetime
from flask import Flask, jsonify, abort, request

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_current_user, verify_jwt_in_request,
    jwt_optional
)
from passlib.hash import pbkdf2_sha256

from functools import wraps

import uuid

from flask_pymongo import PyMongo

from bson.objectid import ObjectId


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/todo"
mongo = PyMongo(app)

app.config['JWT_SECRET_KEY'] = 'xxxxxxxxxxxxxx'  # Change this!
jwt = JWTManager(app)


tasks = []

users = []


@app.route('/register', methods=['POST'])
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


# Create a function that will be called whenever create_access_token
# is used. It will take whatever object is passed into the
# create_access_token method, and lets us define what custom claims
# should be added to the access token.

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user["id"]


@app.route('/login', methods=['POST'])
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


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    global users
    users = [user for user in users if user["id"] == identity]
    if len(users) > 0:
        if users[0]["username"] == "manish":
            users[0]["role"] = "admin"
        else:
            users[0]["role"] = "normal"
        return users[0]
    return {}

# Protect a view with jwt_required, which requires a valid access token
# in the request to access.


@app.route('/profile', methods=['GET'])
@jwt_required
def profile():
    # Access the identity of the current user with get_current_user
    current_user = get_current_user()
    return jsonify(logged_in_as=current_user), 200


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_current_user()
        if user["username"] == "manish":
            return fn(*args, **kwargs)

        return jsonify(msg='Admins only!'), 403
    return wrapper


@app.route("/admin_only")
@jwt_required
@admin_required
def admin_only():
    return ""


@app.route('/todo', methods=["GET"])
@app.route('/todo/<string:direction>', methods=["GET"])
@jwt_optional
def todo(direction=None):
    # direction is optional
    current_user = get_current_user()
    if direction == "ASC":
        direction = 1
    else:
        direction = -1

    if direction is not None:
        if current_user is not None and "id" in current_user:
            if current_user["role"] == "normal":
                ret = mongo.db.tasks.find(
                    {"user": current_user["id"]}).sort("due", direction)
        else:
            ret = mongo.db.tasks.find({"user": ""}).sort(
                "due", direction).limit(5)
    else:
        if current_user is not None and "id" in current_user:
            ret = mongo.db.tasks.find(
                {"user": current_user["id"]})
        else:
            ret = mongo.db.tasks.find({"user": ""}).limit(5)

    tasks = []
    for doc in ret:
        doc["_id"] = str(doc["_id"])
        tasks.append(doc)
    return jsonify(tasks)


@app.route('/todo', methods=["POST"])
@jwt_optional
def add_todo():
    if not request.json:
        abort(500)

    title = request.json.get("title", None)
    desc = request.json.get("description", "")

    due = request.json.get("due", None)

    if due is not None:
        due = datetime.datetime.strptime(due, "%d-%m-%Y")
    else:
        due = datetime.datetime.now()

    current_user = get_current_user()

    user_id = ""
    if current_user is not None and "id" in current_user:
        user_id = current_user["id"]

    # use insert_one to do insert operations
    ret = mongo.db.tasks.insert_one({
        "title": title,
        "description": desc,
        "done": False,
        "due": due,
        "user":  user_id
    }).inserted_id

    # fetch the inserted id and convert it to string before sending it in response
    return jsonify(str(ret))


@app.route("/todo/<string:id>", methods=['PUT'])
@jwt_optional
def update_todo(id):

    if not request.json:
        abort(500)

    title = request.json.get("title", None)
    desc = request.json.get("description", "")

    if title is None:
        return jsonify(message="Invalid Request"), 500

    update_json = {}
    if title is not None:
        update_json["title"] = title

    if desc is not None:
        update_json["description"] = desc

    # match with Object ID
    ret = mongo.db.tasks.update({
        "_id": ObjectId(id)
    }, {
        "$set": update_json
    }, upsert=False)

    return jsonify(ret)


@app.route("/todo/<string:id>", methods=["DELETE"])
def delete_todo(id):

    ret = mongo.db.tasks.remove({
        "_id" : ObjectId(id)
    })

    return jsonify(ret)


def mark(task, status, task_id):
    if task_id == task["id"]:
        task["done"] = status

    return task


@app.route("/todo/mark/<int:task_id>/<int:status>", methods=["PUT"])
@jwt_required
@admin_required
def mark_task(task_id, status):

    global tasks
    if status == 1:
        status = True
    else:
        status = False

    tasks = [mark(task, status, task_id) for task in tasks]

    return jsonify(tasks)
