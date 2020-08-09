from functools import wraps

from starlette.responses import JSONResponse

from admin.models import APIKey


class RateLimitException(Exception):
    pass


def is_authorized(f):
    @wraps(f)
    async def check_auth(self, request):
        if auth := request.headers.get("Authorization"):
            key = await APIKey.get(auth)
            if key:
                request.state.api_key = key
                return await f(self, request)
            else:
                return JSONResponse({
                    "status": "error",
                    "message": "Invalid authorization passed"
                }, status_code=403)
        else:
            return JSONResponse({
                "status": "error",
                "message": "No authorization passed"
            }, status_code=403)

    return check_auth


def is_admin(f):
    @wraps(f)
    async def check_admin(self, request):
        if request.state.api_key.is_admin:
            return await f(self, request)
        else:
            return JSONResponse({
                "status": "error",
                "message": "You are not an administrator"
            }, status_code=403)

    return check_admin


def is_json(f):
    @wraps(f)
    async def check_json(self, request):
        if content_type := request.headers.get("Content-Type"):
            if content_type.lower() == "application/json":
                return await f(self, request)
            else:
                return JSONResponse({
                    "status": "error",
                    "message": "Invalid content type"
                }, status_code=400)
        else:
            return JSONResponse({
                "status": "error",
                "message": "Set a content type of JSON to interact with the API"
            }, status_code=400)

    return check_json


def discord_ratelimited(f):
    @wraps(f)
    async def check_ratelimit(self, request):
        try:
            return await f(self, request)
        except RateLimitException as e:
            return JSONResponse({
                "status": "ratelimit",
                "retry_after": e.args[0]
            }, status_code=429)

    return check_ratelimit
