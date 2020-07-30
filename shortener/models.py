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
