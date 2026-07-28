from flask import Flask
from app.extensions import db, migrate, cors, jwt
from app.config import config_by_name


def create_app(config_name='dev'):
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name))
    
    
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    jwt.init_app(app)

    from app.api import register_blueprints
    register_blueprints(app)

    @app.get('/health')
    def health_check():
        return {'status': 'ok'}, 200

    return app