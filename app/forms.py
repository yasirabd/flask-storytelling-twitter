from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired
from flask_babel import _, lazy_gettext as _l

class SearchForm(FlaskForm):
    place = StringField(_l('Place'), validators=[DataRequired()])
    range_distance = StringField(_l('Range distance'), validators=[DataRequired()])
    days_before = StringField(_l('Days before'), validators=[DataRequired()])
    search = SubmitField(_l('Search'))
