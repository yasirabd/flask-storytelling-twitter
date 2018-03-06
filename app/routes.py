from app import app
from flask import render_template
from flask_googlemaps import Map

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')
