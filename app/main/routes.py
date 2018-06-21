from app import db
from flask import current_app
from flask import render_template, url_for, session, redirect, make_response, jsonify, request
from flask_googlemaps import Map
from flask_babel import _
from googleplaces import GooglePlaces
import pandas as pd
import time
from datetime import datetime
from io import BytesIO
from app.main import bp
from app.main.forms import SearchPlaceForm, SearchTweetsForm, ChoiceObj
from app.models import Crawler, Tweet, Preprocess
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

            # if have more than 40
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


@bp.route('/process', methods=['GET', 'POST'])
def process():
    selectedChoices = ChoiceObj('attractions', session.get('selected'))
    form_splace = SearchPlaceForm()
    form_stweets = SearchTweetsForm(obj=selectedChoices)
    input_crawling = {}

    if form_stweets.validate_on_submit():
        session['selected'] = form_stweets.multi_attractions.data
        place_name = form_stweets.place.data
        latitude = form_stweets.latitude.data
        longitude = form_stweets.longitude.data
        attractions = session.get('selected')
        range_dist = form_stweets.range_dist.data
        days_before = form_stweets.days_before.data

        input_crawling = {'place_name': place_name,
                          'latitude': latitude,
                          'longitude': longitude,
                          'attractions': attractions,
                          'range_dist': range_dist,
                          'days_before': days_before}

    return render_template('process.html', form_stweets=form_stweets, input_crawling=input_crawling)


@bp.route('/process/crawl', methods=['GET', 'POST'])
def crawl():
    place_name = request.form.get('place_name')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    attractions = request.form.getlist('attractions[]')
    range_dist = request.form.get('range_dist')
    days_before = request.form.get('days_before')


    twitter_crawler = TwitterCrawler(current_app)
    df_attractions = twitter_crawler.fetch_tweets_from_attractions(attractions, int(days_before), float(latitude),
                                                                   float(longitude), int(range_dist), place_name)

    # insert into crawler table
    crawler = Crawler()
    crawler.timestamp = datetime.utcnow()
    db.session.add(crawler)
    db.session.commit()

    # insert into tweet table
    for _, row in df_attractions.iterrows():
        tweet = Tweet()
        tweet.user_id = row['user_id']
        tweet.username = row['username']
        tweet.created = row['created_at']
        tweet.text = row['text']
        tweet.latitude = row['latitude']
        tweet.longitude = row['longitude']
        tweet.crawler_id = crawler.id
        db.session.add(tweet)
        db.session.commit()

    return jsonify(status_crawling="success")

@bp.route('/process/preprocess', methods=['GET', 'POST'])
def preprocess():
    return jsonify(status_preprocessing="success")
