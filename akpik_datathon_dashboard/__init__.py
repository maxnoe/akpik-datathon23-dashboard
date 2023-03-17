import os

from flask import Flask
from flask_migrate import Migrate

from .config import Config
from .dashboard import dashboard
from .db import db
from .tasks import celery_init_app


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    
    basepath = os.environ.get('AKPIK_BASEPATH', '')
    app.register_blueprint(dashboard, url_prefix=basepath)
    db.init_app(app)
    Migrate(app, db)

    celery_init_app(app)
    return app
