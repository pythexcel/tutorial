from flask_pymongo import PyMongo

def init_db(app):
    app.config["MONGO_URI"] = "mongodb://localhost:27017/todo"
    mongo = PyMongo(app)
    return mongo
