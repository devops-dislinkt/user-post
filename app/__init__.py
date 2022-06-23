from typing_extensions import Literal
from app.MongoApi import MongoApi
from flask import Flask, g
from os import environ
from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient

# from flask_cors import CORS

mongo_api = MongoApi(None, None)


def create_app(env: Literal["prod", "test"] = "prod"):
    from . import routes

    # environ['FLASK_ENV'] = 'development'
    flask_app = Flask(__name__)
    # CORS(flask_app)

    flask_app.config["JSON_AS_ASCII"] = False
    flask_app.config["SECRET_KEY"] = (
        environ["FLASK_SECRET_KEY"]
        if "FLASK_SECRET_KEY" in environ
        else "my_secret_key"
    )
    flask_app.config["HOST"] = (
        environ["FLASK_DATABASE_HOST"]
        if "FLASK_DATABASE_HOST" in environ
        else "localhost"
    )
    flask_app.config["KAFKA"] = environ["KAFKA"]
    flask_app.config["KAFKA_TOPIC"] = environ["KAFKA_TOPIC"]

    DATABASE_CONNECTION_URI = (
        f"mongodb://root:password@{flask_app.config['HOST']}:27018/"
    )

    with flask_app.app_context():
        # setup connection
        # con = MongoClient('localhost', 27017)
        con = MongoClient(DATABASE_CONNECTION_URI)
        mongo_api.connection = con

        # set users collection with test database if in test envinronment.
        if env == "test":
            flask_app.config["TESTING"] = True
            mongo_api.database = con["user_post_test"]
        else:
            mongo_api.database = con["user_post"]

        flask_app.register_blueprint(routes.api, url_prefix="/api")
        flask_app.register_blueprint(routes.public_api)

    return flask_app
