from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from starlette.responses import JSONResponse

from admin.models import CalendarEvent, RepeatConfiguration
from admin.route import Route
from admin.utils import is_authorized

ITERATE_COUNT = 100

DAYS = {
    RepeatConfiguration.WEEKLY: 7,
    RepeatConfiguration.FORTNIGHTLY: 14
}

class CalendarRoute(Route):
    """
    Route for fetching, creating, updating and deleting calendar events.
    """
    name = "calendar"
    path = "/calendar"

    @is_authorized
    async def get(self, request):
        to_fetch = int(request.query_params.get("limit", 50))

        if to_fetch > 50:
            to_fetch = 50
        
        returned_events = []

        calendar_events = await CalendarEvent.query.order_by(
            CalendarEvent.first_date
        ).gino.all()

        for event in calendar_events:
            event_dict = event.to_dict()

            if event.repeat_configuration is RepeatConfiguration.ONCE:
                event_dict["date"] = event.first_date
                returned_events.append(event_dict)
                continue

            if event.repeat_configuration in DAYS.keys():
                for i in range(ITERATE_COUNT):
                    event_dict = event.to_dict()
                    event_dict["date"] = event.first_date + timedelta(
                        days=DAYS[event.repeat_configuration] * i
                    )
                    returned_events.append(event_dict)
                continue

            for i in range(ITERATE_COUNT):
                event_dict = event.to_dict()
                event_dict["date"] = event.first_date + relativedelta(
                    months=i
                )
                returned_events.append(event_dict)

        returned_events = list(
            filter(
                lambda event: event["date"] >= date.today(), returned_events
            )
        )

        returned_events = list(sorted(returned_events, key=lambda event: event["date"]))

        returned_events = returned_events[:to_fetch]

        for event in returned_events:
            event["date"] = event["date"].isoformat()

        return JSONResponse(returned_events)
