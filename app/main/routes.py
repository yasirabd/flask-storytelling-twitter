from app import current_app
from flask import render_template, url_for, flash
from flask_googlemaps import Map
from flask_babel import _
from googleplaces import GooglePlaces
from app.main import bp
from app.main.forms import SearchPlaceForm, SearchTweets


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    form_splace = SearchPlaceForm()
    form_stweets = SearchTweets()
    attractions = None
    GOOGLEMAPS_KEY = "AIzaSyCc3VpBAxqVIwkCvQC1ibFGFnqJbXDmxwE"
    google_places = GooglePlaces(GOOGLEMAPS_KEY)
    if form_splace.validate_on_submit():
        place_name = form_splace.place_name.data
        attractions = google_places.text_search(query=place_name+' tourist attractions',
                                                language='id')
    return render_template('index.html', form_splace=form_splace,
                            form_stweets=form_stweets, attractions=attractions)
