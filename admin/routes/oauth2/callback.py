from os import environ

import httpx
from starlette.background import BackgroundTask
from starlette.responses import RedirectResponse, PlainTextResponse

from admin.audit_logs import send_audit_log, AuditColour
from admin.route import Route
from admin.models import APIKey

API_BASE = "https://discord.com/api/v7"

ADMIN_FRONTEND = environ.get("LINK_SHORTENER_ADMIN")

CLIENT_ID = environ.get("CLIENT_ID")
CLIENT_SECRET = environ.get("CLIENT_SECRET")

if uri := environ.get("OAUTH2_REDIRECT_URI"):
    REDIRECT_URI = uri
else:
    REDIRECT_URI = "https://modpod.live/oauth2/callback"

class OAuth2Callback(Route):
    """
    Use the returned access code from Discord to authorize the user.
    """
    name = "callback"
    path = "/callback"

    async def get(self, request):
        if request.session["token"] != request.query_params["state"]:
            return PlainTextResponse("Invalid OAuth2 state returned", 400)

        del request.session["token"]

        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": request.query_params["code"],
            "redirect_uri": REDIRECT_URI,
            "scope": "identify"
        }

        async with httpx.AsyncClient() as client:
            access_token_resp = await client.post(f"{API_BASE}/oauth2/token", data=data, headers={
                "Content-Type": "application/x-www-form-urlencoded"
            })

            access_token_resp.raise_for_status()

            token = access_token_resp.json()["access_token"]

            user_data_resp = await client.get(f"{API_BASE}/users/@me", headers={
                "Authorization": f"Bearer {token}"
            })

        user_data_resp.raise_for_status()

        user_data = user_data_resp.json()

        user_api_key = await APIKey.query.where(APIKey.creator == int(user_data["id"])).gino.first()

        if user_api_key:
            task = BackgroundTask(
                send_audit_log,
                title="Successful authentication",
                body=f"Authentication from <@{user_data['id']}>",
                colour=AuditColour.SUCCESS
            )
            return RedirectResponse(f"{ADMIN_FRONTEND}#/authorize/{user_api_key.key}", background=task)
        else:
            task = BackgroundTask(
                send_audit_log,
                title="Failed authentication",
                body=f"Authentication from <@{user_data['id']}>",
                colour=AuditColour.ERROR
            )
            raise PlainTextResponse(
                "While you have authenticated with Discord, your account has not yet been approved by the administrator."
                " Please get in touch with the Modcast tech team to approve your access to the application.",
                403
            )
