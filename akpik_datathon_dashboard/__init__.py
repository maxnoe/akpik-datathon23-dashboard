import os

from flask import Flask
from flask_migrate import Migrate

from .config import Config
from .dashboard import dashboard
from .db import db
from .tasks import celery_init_app
from .auth import login_manager, auth
from .admin import admin


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    login_manager.init_app(app)

    
    basepath = os.environ.get('AKPIK_BASEPATH', '')
    app.register_blueprint(dashboard, url_prefix=basepath)
    app.register_blueprint(auth, url_prefix=basepath)
    app.register_blueprint(admin, url_prefix=basepath)
    db.init_app(app)
    Migrate(app, db)

    celery_init_app(app)
    return app
