from datetime import datetime

from icalendar import Calendar, Event, vDate

from admin.models import CalendarEvent, RepeatConfiguration

FREQUENCIES = {
    RepeatConfiguration.ONCE: None,
    RepeatConfiguration.WEEKLY: {"FREQ": "WEEKLY", "INTERVAL": "1"},
    RepeatConfiguration.FORTNIGHTLY: {"FREQ": "WEEKLY", "INTERVAL": "2"},
    RepeatConfiguration.MONTHLY: {"FREQ": "WEEKLY", "INTERVAL": "1"}
}


async def generate_ical():
    calendar_events = await CalendarEvent.query.order_by(
        CalendarEvent.first_date
    ).gino.all()

    calendar = Calendar()

    calendar.add("prodid", "-//Modcast Podcast//ModPod Admin 1.0//EN")
    calendar.add("version", "2.0")

    calendar.add("name", "Modcast Podcast")
    calendar.add("x-wr-calname", "Modcast Podcast")

    for event in calendar_events:
        ev = Event()

        ev.add("summary", event.title)
        ev.add("uid", event.id)

        ev.add("dtstart", vDate(event.first_date))

        end = datetime.combine(event.first_date, datetime.max.time())
        ev.add("dtstamp", end)

        if rrule := FREQUENCIES.get(event.repeat_configuration):
            ev.add("rrule", rrule)

        calendar.add_component(ev)

    return calendar.to_ical()
