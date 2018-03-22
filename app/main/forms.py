from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import ValidationError, DataRequired
from flask_babel import _, lazy_gettext as _l


class SearchPlaceForm(FlaskForm):
    place = StringField(_l('Place'), validators=[DataRequired()])
    place_name = HiddenField(_l('Place name'), validators=[DataRequired()])
    lat = HiddenField(_l('Latitude'), validators=[DataRequired()])
    lng = HiddenField(_l('Longitude'), validators=[DataRequired()])
    search_place = SubmitField(_l('Search'))


class SearchTweets(FlaskForm):
    latitude = HiddenField(_l('Latitude'), validators=[DataRequired()])
    longitude = HiddenField(_l('Longitude'), validators=[DataRequired()])
    range_dist = StringField(_l('Range distance'), validators=[DataRequired()])
    days_before = StringField(_l('Days before'), validators=[DataRequired()])
    search_tweets = SubmitField(_l('Search'))
