import secrets

from asyncpg.exceptions import UniqueViolationError
from starlette.responses import JSONResponse

from admin.discord_api import get_user
from admin.route import Route
from admin.models import APIKey
from admin.utils import is_admin, is_authorized, is_json


class AdminUserRoute(Route):
    """
    Route for fetching and creating new users.
    """
    name = "all_users"
    path = "/users"

    @is_authorized
    @is_admin
    async def get(self, request):
        users = await APIKey.query.where(
            APIKey.creator.isnot(None)
        ).order_by(
            APIKey.is_admin.desc()
        ).gino.all()

        response = []

        for user in users:
            response.append(user.__dict__["__values__"])

        return JSONResponse(response)

    @is_authorized
    @is_admin
    @is_json
    async def post(self, request):
        data = await request.json()

        try:
            get_user(int(data["creator"]))
        except KeyError:
            return JSONResponse({
                "status": "error",
                "message": "Invalid user specified, upstream returned 404"
            }, status_code=404)

        new_key = APIKey(
            key=secrets.token_hex(32),
            is_admin=data["is_admin"],
            creator=int(data["creator"])
        )

        try:
            await new_key.create()
        except UniqueViolationError:
            return JSONResponse({
                "status": "error",
                "message": "Users can only have one API key per Discord ID"
            }, status_code=400)

        return JSONResponse({
            "status": "success",
            "new_key": new_key.key
        })
