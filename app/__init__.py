import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask, current_app
from flask_bootstrap import Bootstrap
from flask_babel import Babel
from flask_googlemaps import GoogleMaps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate
from config import Config


naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()
bootstrap = Bootstrap()
babel = Babel()
googlemaps = GoogleMaps()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # Config.init_app(app)

    db.init_app(app)
    with app.app_context():
        if db.engine.url.drivername == 'sqlite':
            migrate.init_app(app, db, render_as_batch=True)
        else:
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
