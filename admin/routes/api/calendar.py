from starlette.responses import JSONResponse

from admin.route import Route
from admin.utils import is_authorized


class CalendarRoute(Route):
    """
    Route for fetching, creating, updating and deleting calendar events.
    """
    name = "calendar"
    path = "/calendar"

    @is_authorized
    async def get(self, request):
        return JSONResponse({"status": "ok"})
