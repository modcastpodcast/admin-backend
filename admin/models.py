from os import environ

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
