import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask, current_app
from flask_bootstrap import Bootstrap
from flask_babel import Babel
from flask_googlemaps import GoogleMaps
from config import Config

bootstrap = Bootstrap()
babel = Babel()
googlemaps = GoogleMaps()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)
    
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
