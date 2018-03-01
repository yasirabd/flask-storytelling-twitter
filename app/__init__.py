from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
from flask_babel import Babel

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)
babel = Babel(app)

from app import routes
