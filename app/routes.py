from app import app
from flask import render_template, url_for, flash
from flask_googlemaps import Map
from app.forms import SearchPlaceForm, SearchTweets

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    form_splace = SearchPlaceForm()
    form_stweets = SearchTweets()
    if form_splace.validate_on_submit():
        flash(_('Wait for your result!'))
    return render_template('index.html', form_splace=form_splace, form_stweets=form_stweets)
