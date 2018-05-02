import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask, current_app
from flask_bootstrap import Bootstrap
from flask_babel import Babel
from flask_googlemaps import GoogleMaps
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
babel = Babel()
googlemaps = GoogleMaps()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # Config.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    babel.init_app(app)
    googlemaps.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
                os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/storytelling.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Storytelling twitter startup')

    return app


from app import models
