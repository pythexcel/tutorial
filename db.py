from flask_pymongo import PyMongo


def init_db():
    print("mongo init ")
    mongo = PyMongo()
    return mongo


def init_app(app, mongo):
    print(app.config["MONGO_URI"])
    mongo.init_app(app)
