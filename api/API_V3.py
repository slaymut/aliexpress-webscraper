import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request, jsonify
from scraper.AliExpressNavigator import Navigator
from scraper.AliExpressItemScraper import ItemScraper
from pyspark.sql import SparkSession

print(f"Chemin de recherche Python dans API_V3.py : {sys.path}")

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Bienvenue sur notre Projet BIG DATA !'

# Initialiser la session Spark
# spark = SparkSession.builder \
#     .appName("SparkHadoopAPI") \
#     .getOrCreate()

# Endpoint pour effectuer une recherche sur AliExpress
@app.route('/search', methods=['POST'])
def search_on_aliexpress():
    try:
        # Récupérer les paramètres de la recherche depuis le corps de la demande
        current_directory = os.getcwd()
        parent_directory = os.path.dirname(current_directory)
        chrome_driver_path = os.path.join(parent_directory, 'chrome-driver\\chromedriver.exe')
        
        search_params = request.json
        search_filter = search_params.get('searchFilter', '')
        num_pages = search_params.get('numPages', 1)  # Nouveau paramètre pour le nombre de pages
        choice_filter = search_params.get('choiceFilter', False)
        plus_filter = search_params.get('plusFilter', False)
        free_shipping_filter = search_params.get('freeShippingFilter', False)
        four_stars_and_up_filter = search_params.get('fourStarsAndUpFilter', False)
        maximum = search_params.get('maximum', 0)
        minimum = search_params.get('minimum', 0)

        # Initialiser l'objet Navigator
        navigator = Navigator(chrome_driver_path)

        # Charger les résultats de la recherche pour le nombre spécifié de pages
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
            items.extend(page_items)

        # Fermer le navigateur après avoir récupéré les résultats
        navigator.driver.quit()

        return jsonify(items)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint pour le scraping d'un produit AliExpress
@app.route('/scrape_aliexpress_product', methods=['POST'])
def scrape_aliexpress_product():
    try:
        # Récupérer les paramètres de la recherche depuis le corps de la demande
        current_directory = os.getcwd()
        parent_directory = os.path.dirname(current_directory)
        chrome_driver_path = os.path.join(parent_directory, 'chrome-driver\\chromedriver.exe')

        # Obtenez le produit ID à partir de la requête POST
        data = request.get_json()
        product_id = data.get('product_id')

        # Vérifiez si l'ID du produit est présent
        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400

        # Créez une instance du scraper
        scraper_instance = ItemScraper(chrome_driver_path)

        # Appel à la fonction fetchAllData du scraper
        result = scraper_instance.fetchAllData(product_id)

        # Fermez le navigateur après avoir terminé le scraping
        scraper_instance.driver.quit()

        if result:
            return jsonify({'success': 'Scraping completed successfully', 'data': result}), 200
        else:
            return jsonify({'error': 'Failed to fetch data'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)