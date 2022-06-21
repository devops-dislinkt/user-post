from flask import jsonify
from .routes import api


@api.app_errorhandler(KeyError)
def handle_key_error(e):
    return jsonify(f"Bad keys. Check json keys. Missing: {e} key"), 400


# # allow all origin
@api.after_app_request
def after_request(response):
    header = response.headers
    header["Access-Control-Allow-Origin"] = "*"
    header["Access-Control-Allow-Headers"] = "*"
    header["Access-Control-Allow-Methods"] = "*"
    return response
