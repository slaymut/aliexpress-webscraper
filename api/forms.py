from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField

class AliExpressSearchForm(FlaskForm):
    search_filter = StringField('Filtre de recherche')
    num_pages = IntegerField('Nombre de pages')
    choice_filter = BooleanField('Filtre Produit Choice')
    plus_filter = BooleanField('Filtre Produit Plus')
    free_shipping_filter = BooleanField('Filtre Livraison Gratuite')
    four_stars_and_up_filter = BooleanField('Filtre 4 étoiles et plus')
    maximum = IntegerField('Prix minimum')
    minimum = IntegerField('Prix maximum')
    sort_criteria = StringField('Recherche spéciale')
    submit = SubmitField('Rechercher')
