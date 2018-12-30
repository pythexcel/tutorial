from flask_pymongo import PyMongo

from flask import g, current_app

def init_db(app):
    app.config["MONGO_URI"] = "mongodb://localhost:27017/todo"

def get_db():
    if "mongo" in g:
        return g.mongo
    else:
        mongo = PyMongo(current_app)
        g.mongo = mongo
        return mongo

