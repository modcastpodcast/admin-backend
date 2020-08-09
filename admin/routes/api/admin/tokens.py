from starlette.responses import JSONResponse

from admin.route import Route
from admin.models import APIKey
from admin.utils import is_admin, is_authorized, is_json


class AdminUserRoute(Route):
    """
    Route for fetching and creating new users.
    """
    name = "all_tokens"
    path = "/tokens"

    @is_authorized
    @is_admin
    async def get(self, request):
        users = await APIKey.query.where(
            APIKey.creator.is_(None)
        ).order_by(
            APIKey.is_admin.desc()
        ).gino.all()

        response = []

        for user in users:
            response.append(user.__dict__["__values__"])

        return JSONResponse(response)
