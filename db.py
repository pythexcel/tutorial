from flask_pymongo import PyMongo

from flask import g


def init_db(app):
    app.config["MONGO_URI"] = "mongodb://localhost:27017/todo"
    mongo = PyMongo(app)
    print("conneceting to db")
    return mongo
