from collections import defaultdict
from functools import wraps
from os import environ
from secrets import token_hex

import httpx
from flask import Blueprint, g, jsonify, request
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from shortener.models import db, APIKey, ShortURL

DISCORD_API_TOKEN = environ.get("BOT_TOKEN")

api = Blueprint('api', __name__)

RATELIMITS = defaultdict(dict)

USER_CACHE = {}

DISCORD_API_BASE = "https://discord.com/api/v7"

class RateLimitException(Exception):
    pass


def upstream_get_user(user_id):
    if RATELIMITS["users"].get("remaining") == 0:
        raise RateLimitException(RATELIMITS["users"]["reset_after"])

    user = httpx.get(f"{DISCORD_API_BASE}/users/{user_id}", headers={
        "Authorization": f"Bot {DISCORD_API_TOKEN}"
    })

    RATELIMITS["users"]["reset_after"] = user.headers["x-ratelimit-reset-after"]
    RATELIMITS["users"]["remaining"] = user.headers["x-ratelimit-remaining"]

    if user.status_code == 429:
        # R A T E L I M I T S !
        raise RateLimitException(RATELIMITS["users"]["reset_after"])
    else:
        user_data = user.json()
        USER_CACHE[user_data["id"]] = user_data
        return user_data, user.status_code

def get_user(user_id):
    if user := USER_CACHE.get(str(user_id)):
        return user, 200
    else:
        return upstream_get_user(user_id)

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

def is_admin(f):
    @wraps(f)
    def check_admin(*args, **kwargs):
        if g.api_key.is_admin:
            return f(*args, **kwargs)
        else:
            return jsonify({
                "status": "error",
                "message": "You are not an administrator"
            }), 403

    return check_admin


def is_json(f):
    @wraps(f)
    def check_json(*args, **kwargs):
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

    return check_json

def discord_ratelimited(f):
    @wraps(f)
    def check_ratelimit(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except RateLimitException as e:
            return jsonify({
                "status": "ratelimit",
                "retry_after": e.args[0]
            }), 429

    return check_ratelimit


@api.route("/create", methods=["POST"])
@is_authorized
@is_json
def create():
    """
    Create a new short URL.
    :return:
    """
    data = request.get_json()

    if not g.api_key.creator or (g.api_key.is_admin and data.get("creator")):
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

@api.route("/links/all")
@is_authorized
def all_links():
    """
    Return all short URLs and relevant data.
    :return:
    """
    links = ShortURL.query.order_by(ShortURL.creation_date.desc()).all()

    links_json = []

    for link in links:
        data = link.__dict__

        data.pop("_sa_instance_state")

        data["creator"] = str(data["creator"])

        data["creation_date"] = data["creation_date"].timestamp()

        links_json.append(data)

    return jsonify(links_json)

@api.route("/links/mine")
@is_authorized
def my_links():
    """
    Return all short URLs and relevant data owned by the current authorized user.
    :return:
    """
    links = ShortURL.query.order_by(ShortURL.creation_date.desc()).filter_by(creator=g.api_key.creator).all()

    links_json = []

    for link in links:
        data = link.__dict__

        data.pop("_sa_instance_state")

        data["creator"] = str(data["creator"])

        data["creation_date"] = data["creation_date"].timestamp()

        links_json.append(data)

    return jsonify(links_json)

@api.route("/me")
@is_authorized
def get_current_user():
    """
    Return token information on the current user.
    """
    user = g.api_key.__dict__

    user.pop("_sa_instance_state")

    user["creator"] = str(user["creator"])

    return jsonify(user)

@api.route("/user/<int:user_id>")
@is_authorized
@discord_ratelimited
def get_user_by_id(user_id):
    """
    Fetch another user by ID from the Discord API.
    """
    try:
        user_id = int(user_id)
        return get_user(user_id)
    except ValueError:
        raise BadRequest()

@api.route("/admin/users")
@is_authorized
@is_admin
def get_all_users():
    keys = APIKey.query.filter(APIKey.creator.isnot(None)).all()

    keys_json = []

    for key in keys:
        data = key.__dict__

        data.pop("_sa_instance_state")

        data["creator"] = str(data["creator"])

        keys_json.append(data)

    return jsonify(keys_json)

@api.route("/admin/tokens")
@is_authorized
@is_admin
def get_all_tokens():
    keys = APIKey.query.filter(APIKey.creator.is_(None)).all()

    keys_json = []

    for key in keys:
        data = key.__dict__

        data.pop("_sa_instance_state")

        data.pop("creator")

        keys_json.append(data)

    return jsonify(keys_json)

@api.route("/admin/create_user", methods=["POST"])
@is_authorized
@is_admin
@is_json
def create_user():
    data = request.get_json()

    try:
        get_user(int(data["creator"]))
    except:
        return jsonify({
            "status": "failure",
            "message": "Invalid user specified, Discord upstream returned error"
        })

    new_key = APIKey(
        key=token_hex(32),
        is_admin=data["is_admin"],
        creator=int(data["creator"])
    )

    db.session.add(new_key)
    db.session.commit()

    return jsonify({
        "status": "success",
        "new_key": new_key.key
    })