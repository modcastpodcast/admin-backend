from starlette.responses import JSONResponse

from admin.route import Route
from admin.utils import is_authorized, discord_ratelimited
from admin.discord_api import get_user

class UserInformation(Route):
    """
    Route for returning the Discord information on a user.
    """
    name = "user"
    path = "/{user_id:int}"

    @is_authorized
    @discord_ratelimited
    async def get(self, request):
        user_data, response_code = await get_user(request.path_params["user_id"])

        return JSONResponse(user_data, response_code)
