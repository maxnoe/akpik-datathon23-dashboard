from flask import Flask
from flask_migrate import Migrate

from .config import Config
from .dashboard import dashboard
from .db import db


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(dashboard)
    db.init_app(app)
    Migrate(app, db)
    return app
