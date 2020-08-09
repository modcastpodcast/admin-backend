from starlette.responses import JSONResponse

from admin.route import Route
from admin.utils import is_authorized

class MeAPI(Route):
    """
    Route for returning information about the currently authenticated user.
    """
    name = "me"
    path = "/me"

    @is_authorized
    async def get(self, request):
        key_data = request.state.api_key.__dict__["__values__"]
        key_data["creator"] = str(key_data["creator"])

        return JSONResponse(key_data)