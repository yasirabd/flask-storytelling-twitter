from app import app
from flask import render_template, url_for, flash
from flask_googlemaps import Map
from app.forms import SearchForm

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        flash(_('Wait for your result!'))
    return render_template('index.html', form=form)
