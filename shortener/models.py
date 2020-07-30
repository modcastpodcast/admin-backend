from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ShortURL(db.Model):
    """
    Model representing a short link on the site.
    """
    short_code = db.Column(db.Text, primary_key=True)
    long_url = db.Column(db.Text, nullable=False)
    creator = db.Column(db.BigInteger, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    clicks = db.Column(db.Integer, nullable=False, default=0)


class APIKey(db.Model):
    """
    Represents a valid authentication key for the site.
    """
    key = db.Column(db.Text, primary_key=True)

    # Administrators can create and delete API keys
    is_admin = db.Column(db.Boolean, primary_key=True, default=False)