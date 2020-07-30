from flask_migrate import Migrate

from shortener import app, db

migrate = Migrate(app, db)
