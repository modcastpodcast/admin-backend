from enum import Enum

from datetime import datetime
from gino import Gino

db = Gino()


class ShortURL(db.Model):
    """
    Model representing a short link on the site.
    """
    __tablename__ = "short_urls"

    short_code = db.Column(db.Text, primary_key=True)
    long_url = db.Column(db.Text, nullable=False)
    creator = db.Column(db.BigInteger, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text, default="")
    clicks = db.Column(db.Integer, nullable=False, default=0)


class APIKey(db.Model):
    """
    Represents a valid authentication key for the site.
    """
    __tablename__ = "api_keys"

    key = db.Column(db.Text, primary_key=True)

    # Administrators can create and delete API keys
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    # Optionally API keys can be registered to users for the frontend portal
    # If an API key does not have a creator attached then the key is valid for any user
    creator = db.Column(db.BigInteger, nullable=True, unique=True)


class RepeatConfiguration(Enum):
    ONCE = 'once'
    WEEKLY = 'weekly'
    FORTNIGHTLY = 'fortnightly'
    MONTHLY = 'monthly'


class CalendarEvent(db.Model):
    """
    Represents a recurring event within the Modcast calendar.
    """
    __tablename__ = "events"

    id = db.Column(db.String, primary_key=True)

    title = db.Column(db.Text, nullable=False)

    first_date = db.Column(db.Date, nullable=False)

    repeat_configuration = db.Column(
        db.Enum(RepeatConfiguration),
        nullable=False,
        default=RepeatConfiguration.ONCE
    )

    creator = db.Column(db.BigInteger, nullable=False)

    def to_dict(self) -> dict:
        """
        Serialize the DB model to a dictionary.
        """
        return {
            "id": self.id,
            "title": self.title,
            "first_date": self.first_date.isoformat(),
            "repeat_configuration": self.repeat_configuration.value,
            "creator": str(self.creator)
        }


class CalendarEventAssignments(db.Model):
    """
    Represents a user being assigned to a task.
    """
    __tablename__ = "assignments"

    event_id = db.Column(db.String, db.ForeignKey("events.id"))
    user_id = db.Column(db.BigInteger, db.ForeignKey("api_keys.creator"))
