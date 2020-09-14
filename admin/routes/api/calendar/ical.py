from starlette.responses import Response

from admin.calendar import generate_ical
from admin.route import Route
from admin.models import APIKey


class ICalRoute(Route):
    """
    Route for returning an iCal representation of the calendar.
    """
    name = "ical"
    path = "/"

    async def get(self, request):
        authorized = False
        if token := request.query_params.get("token"):
            if await APIKey.get(token):
                authorized = True

        if not authorized:
            return Response("Invalid token passed", status_code=403)

        ical = await generate_ical()

        return Response(ical, 200, {
            "Content-Type": "text/calendar"
        })
