from app import current_app as app
from flask import render_template, url_for, session, redirect, make_response
from flask_googlemaps import Map
from flask_babel import _
from googleplaces import GooglePlaces
import pandas as pd
import time
from io import BytesIO
from app.main import bp
from app.main.forms import SearchPlaceForm, SearchTweetsForm, ChoiceObj
from ..modules.crawler import TwitterCrawler
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

    attractions, attractions_next_page, attractions_next_page2 = None, None, None
    list_attractions = ()
    GOOGLEMAPS_KEY = "AIzaSyCc3VpBAxqVIwkCvQC1ibFGFnqJbXDmxwE"
    google_places = GooglePlaces(GOOGLEMAPS_KEY)
    if form_splace.validate_on_submit():
        place_name = form_splace.place_name.data
        attractions = google_places.text_search(query=place_name+' tourist attractions',
                                                language='id')
        # if have more than 20
        if attractions.has_next_page_token:
            time.sleep(2)
            attractions_next_page = google_places.text_search(pagetoken=attractions.next_page_token)

            # if more have than 40
            if attractions_next_page.has_next_page_token:
                time.sleep(2)
                attractions_next_page2 = google_places.text_search(pagetoken=attractions_next_page.next_page_token)

        if attractions:
            la = list(list_attractions)
            for place in attractions.places:
                la.append(place.name)
            if attractions_next_page:
                for place in attractions_next_page.places:
                    la.append(place.name)
            if attractions_next_page2:
                for place in attractions_next_page2.places:
                    la.append(place.name)
            list_attractions = tuple(la)

        form_stweets.multi_attractions.choices =  [(att, att) for att in list_attractions]
        form_stweets.latitude.data = form_splace.lat.data
        form_stweets.longitude.data = form_splace.lng.data
        form_stweets.place.data = place_name
    return render_template('index.html', form_splace=form_splace,
                            form_stweets=form_stweets)


@bp.route('/crawl', methods=['GET', 'POST'])
def crawl():
    selectedChoices = ChoiceObj('attractions', session.get('selected'))
    form_splace = SearchPlaceForm()
    form_stweets = SearchTweetsForm(obj=selectedChoices)

    twitter_crawler = TwitterCrawler(app)

    if form_stweets.validate_on_submit():
        session['selected'] = form_stweets.multi_attractions.data
        attractions = session.get('selected')
        days_before = form_stweets.days_before.data
        latitude = form_stweets.latitude.data
        longitude = form_stweets.longitude.data
        max_range = form_stweets.range_dist.data
        place_name = form_stweets.place.data

        df_attractions = twitter_crawler.fetch_tweets_from_attractions(attractions, int(days_before), float(latitude),
                                                                       float(longitude), int(max_range), place_name)
        response = make_response(df_attractions.to_csv(index=False, columns=['user_id', 'username', 'created_at', 'latitude', 'longitude', 'text']))
        response.headers["Content-Disposition"] = "attachment; filename=export.csv"
        response.mimetype='text/csv'

        # return response
        return render_template('result.html', form_stweets=form_stweets, selected=session.get('selected'), place=place_name)

    flash_errors(form_stweets)
    return render_template('index.html', form_splace=form_splace,
                            form_stweets=form_stweets, selected=session.get('selected'))
