from flask import Flask
from app.extensions import db, migrate
from app.config import config_by_name
from app import models


def create_app(config_name='dev'):
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name))
    
    db.init_app(app)
    migrate.init_app(app, db)

    @app.get('/health')
    def health_check():
        return {'status': 'ok'}, 200

    return app