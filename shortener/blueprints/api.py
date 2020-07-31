from functools import wraps

from flask import Blueprint, g, jsonify, request
from sqlalchemy.exc import IntegrityError

from shortener.models import db, APIKey, ShortURL

api = Blueprint('api', __name__)


def is_authorized(f):
    @wraps(f)
    def check_auth(*args, **kwargs):
        if auth := request.headers.get("Authorization"):
            if key := APIKey.query.filter_by(key=auth).first():
                g.api_key = key
                return f(*args, **kwargs)
            else:
                return jsonify({
                    "status": "error",
                    "message": "Invalid authorization passed"
                }), 403
        else:
            return jsonify({
                "status": "error",
                "message": "No authorization passed"
            }), 400

    return check_auth


def is_json(f):
    @wraps(f)
    def check_auth(*args, **kwargs):
        if content_type := request.headers.get("Content-Type"):
            if content_type.lower() == "application/json":
                return f(*args, **kwargs)
            else:
                return jsonify({
                    "status": "error",
                    "message": "Invalid content type"
                }), 400
        else:
            return jsonify({
                "status": "error",
                "message": "Set a content type of JSON to interact with the API"
            }), 400

    return check_auth


@api.route("/create", methods=["POST"])
@is_authorized
@is_json
def create():
    """
    Create a new short URL.
    :return:
    """
    data = request.get_json()

    if not g.api_key.creator:
        new_url = ShortURL(
            short_code=data["short_code"],
            long_url=data["long_url"],
            creator=data["creator"]
        )
    else:
        new_url = ShortURL(
            short_code=data["short_code"],
            long_url=data["long_url"],
            creator=g.api_key.creator
        )

    db.session.add(new_url)

    try:
        db.session.commit()
    except IntegrityError:
        return jsonify({
            "status": "error",
            "message": "Short code exists"
        }), 400

    return jsonify({
        "status": "success",
        "message": "Short code added"
    })


@api.route("/delete", methods=["DELETE"])
@is_authorized
@is_json
def delete():
    """
    Delete a short URL.
    :return:
    """
    data = request.get_json()
    if short_url := ShortURL.query.filter_by(short_code=data["short_code"]).first():
        db.session.delete(short_url)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Short code removed"
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Short code does not exist"
        })