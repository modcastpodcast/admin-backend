import secrets
import urllib.parse
from os import environ

import httpx
from flask import Blueprint, jsonify, redirect, request, session
from werkzeug.exceptions import BadRequest, Unauthorized

from shortener.models import db, APIKey, ShortURL

oauth2 = Blueprint('oauth2', __name__)

API_BASE = "https://discord.com/api/v7"

ADMIN_FRONTEND = environ.get("LINK_SHORTENER_ADMIN")

CLIENT_ID = environ.get("CLIENT_ID")
CLIENT_SECRET = environ.get("CLIENT_SECRET")

if uri := environ.get("OAUTH2_REDIRECT_URI"):
    REDIRECT_URI = uri
else:
    REDIRECT_URI = "https://modpod.live/oauth2/callback"


@oauth2.route("/authorize")
def generate_authorize_url():
    token = secrets.token_hex(32)
    session["token"] = token

    frag = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "state": token,
        "prompt": "none",
        "scope": "identify"
    })

    return redirect(
        f"{API_BASE}/oauth2/authorize?{frag}"
    )


@oauth2.route("/callback")
def oauth2_callback():
    if session.get("token", "a") != request.args["state"]:
        raise BadRequest("Invalid OAuth2 state returned")

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": request.args["code"],
        "redirect_uri": REDIRECT_URI,
        "scope": "identify"
    }

    access_token_resp = httpx.post(f"{API_BASE}/oauth2/token", data=data, headers={
        "Content-Type": "application/x-www-form-urlencoded"
    })

    access_token_resp.raise_for_status()

    token = access_token_resp.json()["access_token"]

    user_data_resp = httpx.get(f"{API_BASE}/users/@me", headers={
        "Authorization": f"Bearer {token}"
    })

    user_data_resp.raise_for_status()

    user_data = user_data_resp.json()

    if user_api_key := APIKey.query.filter_by(creator=int(user_data["id"])).first():
        return jsonify({
            "key": user_api_key.key,
            "is_admin": user_api_key.is_admin,
            "creator": user_api_key.creator
        })
    else:
        raise Unauthorized(
            "While you have authenticated with Discord, your account has not yet been approved by the administrator."
            " Please get in touch with the Modcast tech team to approve your access to the application."
        )