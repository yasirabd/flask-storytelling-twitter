from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired
from flask_babel import _, lazy_gettext as _l

class SearchForm(FlaskForm):
    range_location = StringField(_l('Range location'), validators=[DataRequired()])
    days_before = StringField(_l('Days before'), validators=[DataRequired()])
    latitude = StringField(_l('Latitude'), validators=[DataRequired()])
    longitude = StringField(_l('Longitude'), validators=[DataRequired()])
    search = SubmitField(_l('Search'))
