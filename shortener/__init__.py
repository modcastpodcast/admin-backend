import secrets
from os import environ

from crawlerdetect import CrawlerDetect
from flask import Flask, redirect, request
from flask_cors import CORS
from werkzeug.exceptions import NotFound

from shortener.blueprints.api import api
from shortener.blueprints.oauth2 import oauth2
from shortener.models import db, ShortURL


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = secrets.token_hex(64)
CORS(app, resources={
    r"/api/*": {"origins": "https://admin.modpod.live"}
})

db.init_app(app)

app.register_blueprint(api, url_prefix="/api")
app.register_blueprint(oauth2, url_prefix="/oauth2")

crawler = CrawlerDetect()


@app.route("/")
def index():
    return redirect("https://modcast.network/")


@app.route("/<string:code>")
def short_redirect(code):
    if link := ShortURL.query.filter_by(short_code=code).first():
        if not crawler.isCrawler(request.headers.get("User-Agent")):
            link.clicks += 1
            db.session.commit()
        return redirect(link.long_url)
    else:
        return NotFound("The requested short code could not be found")
