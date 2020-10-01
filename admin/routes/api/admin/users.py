import secrets

from starlette.background import BackgroundTask
from asyncpg.exceptions import UniqueViolationError
from starlette.responses import JSONResponse

from admin.audit_logs import send_audit_log, AuditColour
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
            user_data = user.__dict__["__values__"]

            user_data["creator"] = str(user_data["creator"])

            response.append(user_data)

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

        task = BackgroundTask(
            send_audit_log,
            title="New user added",
            body=f"Added by <@{request.state.api_key.creator}>",
            inline_fields={
                "User": f"<@{data['creator']}>",
                "Administrator": data["is_admin"]
            },
            colour=AuditColour.SUCCESS
        )

        return JSONResponse({
            "status": "success",
            "new_key": new_key.key
        }, background=task)
