from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
from flask_babel import Babel
from flask_googlemaps import GoogleMaps

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)
babel = Babel(app)
googlemaps = GoogleMaps(app)

from app import routes, errors
