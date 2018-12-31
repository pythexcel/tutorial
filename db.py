from flask_pymongo import PyMongo

from flask import g


def init_db(app):
    mongo = PyMongo(app)
    print("conneceting to db ")
    print(app.config["MONGO_URI"])
    return mongo
