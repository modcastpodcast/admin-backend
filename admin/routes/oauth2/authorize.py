import secrets
import urllib.parse
from os import environ

from starlette.responses import RedirectResponse

from admin.route import Route

API_BASE = "https://discord.com/api/v7"

CLIENT_ID = environ.get("CLIENT_ID")

if uri := environ.get("OAUTH2_REDIRECT_URI"):
    REDIRECT_URI = uri
else:
    REDIRECT_URI = "https://modpod.live/oauth2/callback"

class OAuth2Authorize(Route):
    """
    Route for handling the creation of the OAuth2 redirect to Discord.
    """
    name = "authorize"
    path = "/authorize"

    async def get(self, request):
        token = secrets.token_hex(32)
        request.session["token"] = token

        frag = urllib.parse.urlencode({
            "client_id": CLIENT_ID,
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "state": token,
            "prompt": "none",
            "scope": "identify"
        })

        return RedirectResponse(
            f"{API_BASE}/oauth2/authorize?{frag}"
        )