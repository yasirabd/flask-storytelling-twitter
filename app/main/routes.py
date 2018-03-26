from app import current_app
from flask import render_template, url_for, session, redirect
from flask_googlemaps import Map
from flask_babel import _
from googleplaces import GooglePlaces
from app.main import bp
from app.main.forms import SearchPlaceForm, SearchTweetsForm, ChoiceObj
from app._helpers import flash_errors


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    form_splace = SearchPlaceForm()
    form_stweets = SearchTweetsForm()

    return render_template('index.html', form_splace=form_splace,
                            form_stweets=form_stweets)


@bp.route('/attractions', methods=['GET', 'POST'])
def attractions():
    selectedChoices = ChoiceObj('multi_attractions', session.get('selected'))
    form_splace = SearchPlaceForm()
    form_stweets = SearchTweetsForm(obj=selectedChoices)

    attractions = None
    list_attractions = ()
    GOOGLEMAPS_KEY = "AIzaSyCc3VpBAxqVIwkCvQC1ibFGFnqJbXDmxwE"
    google_places = GooglePlaces(GOOGLEMAPS_KEY)
    if form_splace.validate_on_submit():
        place_name = form_splace.place_name.data
        attractions = google_places.text_search(query=place_name+' tourist attractions',
                                                language='id')
        if attractions:
            la = list(list_attractions)
            for place in attractions.places:
                la.append(place.name)
            list_attractions = tuple(la)

        form_stweets.multi_attractions.choices =  [(att, att) for att in list_attractions]
        form_stweets.latitude.data = form_splace.lat.data
        form_stweets.longitude.data = form_splace.lng.data
    return render_template('index.html', form_splace=form_splace,
                            form_stweets=form_stweets)

@bp.route('/crawl', methods=['GET', 'POST'])
def crawl():
    selectedChoices = ChoiceObj('attractions', session.get('selected'))
    form_splace = SearchPlaceForm()
    form_stweets = SearchTweetsForm(obj=selectedChoices)

    if form_stweets.validate_on_submit():
        session['selected'] = form_stweets.multi_attractions.data
        return render_template('result.html', form_stweets=form_stweets, selected=session.get('selected'))

    flash_errors(form_stweets)
    return render_template('index.html', form_splace=form_splace,
                            form_stweets=form_stweets, selected=session.get('selected'))
