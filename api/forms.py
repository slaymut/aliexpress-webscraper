from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField

class AliExpressSearchForm(FlaskForm):
    search_filter = StringField('Search Filter')
    num_pages = IntegerField('Number of Pages')
    choice_filter = BooleanField('Choice Filter')
    plus_filter = BooleanField('Plus Filter')
    free_shipping_filter = BooleanField('Free Shipping Filter')
    four_stars_and_up_filter = BooleanField('Four Stars and Up Filter')
    maximum = IntegerField('Maximum Price')
    minimum = IntegerField('Minimum Price')
    sort_criteria = StringField('Sort Criteria')
    submit = SubmitField('Search')
