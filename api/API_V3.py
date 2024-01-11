import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from selenium import webdriver
from flask import Flask, request, jsonify, render_template
from scraper.AliExpressNavigator import Navigator
from scraper.AliExpressItemScraper import ItemScraper
# from pyspark.sql import SparkSession
from flask_cors import CORS
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from forms import AliExpressSearchForm  # Importation du formulaire

print(f"Chemin de recherche Python dans API_V3.py : {sys.path}")
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
# options.add_argument('--incognito')
# options.add_argument('--headless')
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument('--pageLoadStrategy=none')  # Set pageLoadStrategy to none

current_directory = os.getcwd()
parent_directory = os.path.dirname(current_directory)
chrome_driver_path = os.path.join(parent_directory, 'chrome-driver\\chromedriver.exe')

driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)

# current_directory = os.getcwd()
# chrome_driver_path = os.path.join(current_directory, 'chrome-driver-copy/chromedriver')

# driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)

app = Flask(__name__)
CORS(app)
csrf = CSRFProtect(app)

# Ajout d'une clé secrète
app.config['SECRET_KEY'] = 'anitamaxwynn'  # Remplacez 'votre_cle_secrete' par une chaîne de caractères aléatoire et sécurisée
csrf.init_app(app)  # Intégration de Flask-WTF CSRFProtect

@app.route('/', methods=['GET', 'POST'])
def home():
    form = AliExpressSearchForm()

    if form.validate_on_submit():
        # Traitez les données du formulaire ici si le formulaire a été soumis
        search_filter = form.searchFilter.data
        num_pages = int(form.numPages.data)
        choice_filter = form.choiceFilter.data
        plus_filter = form.plusFilter.data
        free_shipping_filter = form.freeShippingFilter.data
        four_stars_and_up_filter = form.fourStarsAndUpFilter.data
        maximum = float(form.maximum.data)
        minimum = float(form.minimum.data)
        sort_criteria = form.sortCriteria.data
        
        # Ajout ici de la logique pour effectuer la recherche sur AliExpress

        # Initialisation de l'objet Navigator
        navigator = Navigator(driver)

        # Chargement des résultats de la recherche pour le nombre spécifié de pages, et de paramètres
        items = []
        message = ""
        for page in range(1, num_pages + 1):
            page_items = navigator.loadPageResults(
                search_filter,
                page=page,
                choiceFilter=choice_filter,
                plusFilter=plus_filter,
                freeShippingFilter=free_shipping_filter,
                fourStarsAndUpFilter=four_stars_and_up_filter,
                maximum=maximum,
                minimum=minimum
            )
            items.extend(page_items)

            if len(page_items) < 60:
                message = f"Le scraping a été interrompu sur la page {page} sur {num_pages} demandées car nous avons atteint le maximum de pages disponibles."
                break
            else:
                message = f"Le scraping a été effectué sur les {num_pages} pages."
            
        if sort_criteria == 'best_offers':
            items = navigator.getBestItems(items, 10)

        elif sort_criteria == 'sell_highest':
            items = navigator.getMostSelledItems(items, 10)

        elif sort_criteria == 'rating_highest':
            items = navigator.getBestRatedItems(items, 10)
            
        else:
            # Aucun tri spécifié, utilisez le tri par défaut (par ordre d'apparition dans les pages)
            pass

        # Exemple de sauvegarde en JSON
        itemScraper = ItemScraper(driver)
        for item in items:
            detailedStore, detailedItem = itemScraper.fetchAllData(item.get('id'))
            itemScraper.save_to_json(detailedStore, detailedItem)

        # Utilisez les données du formulaire (search_filter, num_pages, etc.) dans votre recherche

        # Redirection de l'utilisateur vers une autre page
        return render_template('web_interface_result.html', message="Scraping completed successfully!", items=items)

    # Si la méthode n'est pas POST, ou si la validation du formulaire échoue
    return render_template('web_interface.html', form=form)



# Initialiser la session Spark
# spark = SparkSession.builder \
#     .appName("SparkHadoopAPI") \
#     .getOrCreate()

#Endpoint pour faire les Best-of Items
# @app.route('/best-of-items', methods=['GET'])
# def get_best_items():
#     return

# #Endpoint pour faire les Best-Of Stores
# @app.route('/best-of-store', methods=['GET'])
# def get_best_stores():
#     return

# Endpoint pour effectuer une recherche sur AliExpress
@app.route('/search', methods=['POST'])
def search_on_aliexpress():
    try:
        # Récupérer les paramètres de la recherche depuis le corps de la demande
        # search_params = request.json
        # search_filter = search_params.get('searchFilter', '')
        # num_pages = search_params.get('numPages', 1)  # Nouveau paramètre pour le nombre de pages
        # choice_filter = search_params.get('choiceFilter', False)
        # plus_filter = search_params.get('plusFilter', False)
        # free_shipping_filter = search_params.get('freeShippingFilter', False)
        # four_stars_and_up_filter = search_params.get('fourStarsAndUpFilter', False)
        # maximum = search_params.get('maximum', 0)
        # minimum = search_params.get('minimum', 0)
    
        # Récupérer les paramètres de la recherche depuis le formulaire web
        search_filter = request.form.get('searchFilter', '')
        num_pages = int(request.form.get('numPages', 1))  # Nouveau paramètre pour le nombre de pages
        choice_filter = request.form.get('choiceFilter', False)
        plus_filter = request.form.get('plusFilter', False)
        free_shipping_filter = request.form.get('freeShippingFilter', False)
        four_stars_and_up_filter = request.form.get('fourStarsAndUpFilter', False)
        maximum = float(request.form.get('maximum', 0))
        minimum = float(request.form.get('minimum', 0))
        sort_criteria = request.form.get('sortCriteria', 'default')

        # Initialiser l'objet Navigator
        navigator = Navigator(driver)

        # Charger les résultats de la recherche pour le nombre spécifié de pages
        message = ''
        items = []
        for page in range(1, num_pages + 1):
            page_items = navigator.loadPageResults(
                search_filter,
                page=page,
                choiceFilter=choice_filter,
                plusFilter=plus_filter,
                freeShippingFilter=free_shipping_filter,
                fourStarsAndUpFilter=four_stars_and_up_filter,
                maximum=maximum,
                minimum=minimum
            )

            # Arrêter le scraping si moins de 60 articles sont récupérés sur une page

            items.extend(page_items)
            if len(page_items) < 60:
                message = f"Le scraping a été interrompu sur la page {page} sur {num_pages} demandées car nous avons atteint le maximum de pages disponibles."
                break
            else:
                message = f"Le scraping a été effectué sur les {num_pages} pages."

        # Switch case simulé avec des conditions if-elif-else
        # sort_criteria = search_params.get('sortCriteria', 'default')

        if sort_criteria == 'best_offers':
            items = navigator.getBestItems(items, 10)

        elif sort_criteria == 'sell_highest':
            items = navigator.getMostSelledItems(items, 10)

        elif sort_criteria == 'rating_highest':
            items = navigator.getBestRatedItems(items, 10)
            
        # elif sort_criteria == '':
        #     items.sort(key=lambda x: x.get('rating', 0))
        #     # Gardez seulement les 10 premiers items
        #     items = items[:10]
            
        else:
            # Aucun tri spécifié, utilisez le tri par défaut (par ordre d'apparition dans les pages)
            # items = navigator.getBestItems(items, 10)
            pass
        
        itemScraper = ItemScraper(driver)
        for item in items:
            print("Scraping item")
            detailedStore, detailedItem = itemScraper.fetchAllData(item.get('id'))
            itemScraper.save_to_json(detailedStore, detailedItem)
        
    #     return jsonify({'message': message, 'items': items})
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 500
        return render_template('web_interface_result.html', message=message, items=items)
    except Exception as e:
        return render_template('web_interface_result.html', error=str(e))


# Endpoint pour le scraping d'un produit AliExpress
@app.route('/scrape_aliexpress_product', methods=['POST'])
def scrape_aliexpress_product():
    try:
        # Obtenez le produit ID à partir de la requête POST
        # data = request.get_json()
        # product_id = data.get('product_id')

        # Obtenez le produit ID à partir du formulaire web
        product_id = request.form.get('product_id')

        # Vérifiez si l'ID du produit est présent
        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400

        # Créez une instance du scraper
        scraper_instance = ItemScraper(driver)

        # Appel à la fonction fetchAllData du scraper
        store, item = scraper_instance.fetchAllData(product_id)
        scraper_instance.save_to_json(
            store=store,
            item=item
        )
        
        result = {
            'store': store,
            'item': item
        }

    #     if result:
    #         return jsonify(result), 200
    #     else:
    #         return jsonify({'error': 'Failed to fetch data'}), 500

    # except Exception as e:
    #     return jsonify({'error': str(e)}), 500
        if result:
            return render_template('web_interface_result.html', result=result)
        else:
            return render_template('web_interface_result.html', error='Failed to fetch data')
    except Exception as e:
        return render_template('web_interface_result.html', error=str(e))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)