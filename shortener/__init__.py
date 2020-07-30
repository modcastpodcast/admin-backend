from os import environ

from flask import Flask, redirect
from werkzeug.exceptions import NotFound

from shortener.blueprints.api import api
from shortener.models import db, ShortURL


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)

app.register_blueprint(api, url_prefix="/api")


@app.route("/")
def index():
    return redirect("https://modcast.network/")


@app.route("/<string:code>")
def short_redirect(code):
    if link := ShortURL.query.filter_by(short_code=code).first():
        link.clicks += 1
        db.session.commit()
        return redirect(link.long_url)
    else:
        return NotFound("The requested short code could not be found")
