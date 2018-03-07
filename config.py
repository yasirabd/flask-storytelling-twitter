import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'whatever-you-think'
    TEMPLATES_AUTO_RELOAD = True
    GOOGLEMAPS_KEY = "AIzaSyCc3VpBAxqVIwkCvQC1ibFGFnqJbXDmxwE"
