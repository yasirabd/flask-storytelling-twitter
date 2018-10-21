from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectMultipleField, widgets, SelectField, FloatField
from wtforms.validators import ValidationError, DataRequired, InputRequired
from flask_babel import _, lazy_gettext as _l


RANGES = [('70', '70'), ('90', '90'), ('110', '110'), ('130', '130')]
DAYS = [('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11')]

class SearchPlaceForm(FlaskForm):
    place = StringField(_l('Place'), validators=[DataRequired()])
    place_name = HiddenField(_l('Place name'), validators=[DataRequired()])
    lat = HiddenField(_l('Latitude'), validators=[DataRequired()])
    lng = HiddenField(_l('Longitude'), validators=[DataRequired()])
    search_place = SubmitField(_l('Get Attractions'))


class ChoiceObj(object):
    def __init__(self, name, choices):
        # this is needed so that BaseForm.process will accept the object for the named form,
        # and eventually it will end up in SelectMultipleField.process_data and get assigned
        # to .data
        setattr(self, name, choices)


class SelectMultipleAttractions(SelectMultipleField):
    def pre_validate(self, form):
        # Prevent "not a valid choice" error
        pass

    widget = widgets.TableWidget()
    option_widget = widgets.CheckboxInput()


class SearchTweetsForm(FlaskForm):
    place = HiddenField(_l('Place'), validators=[DataRequired()])
    latitude = HiddenField(_l('Latitude'), validators=[DataRequired()])
    longitude = HiddenField(_l('Longitude'), validators=[DataRequired()])
    multi_attractions = SelectMultipleAttractions('Attractions', choices=[], validators=[InputRequired()])
    range_dist = SelectField(_l('Range distances (Km)'), choices=RANGES, validators=[DataRequired()])
    days_before = SelectField(_l('Days before (days)'), choices=DAYS, validators=[DataRequired()])
    submit = SubmitField(_l('Crawl Tweets'))
