import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from selenium import webdriver
from flask import Flask, request, jsonify
from scraper.AliExpressNavigator import Navigator
from scraper.AliExpressItemScraper import ItemScraper
from flask_cors import CORS
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import psycopg2

print(f"Chemin de recherche Python dans API_V3.py : {sys.path}")
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Set the page load strategy to 'eager' or 'none'
capabilities = DesiredCapabilities.CHROME
capabilities["pageLoadStrategy"] = "eager"  # or "none"

# current_directory = os.getcwd()
# parent_directory = os.path.dirname(current_directory)
# chrome_driver_path = os.path.join(parent_directory, 'chrome-driver\\chromedriver.exe')

# driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options, desired_capabilities=capabilities)

current_directory = os.getcwd()
chrome_driver_path = os.path.join(current_directory, 'chrome-driver-docker/chromedriver')

driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options, desired_capabilities=capabilities)

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return 'Bienvenue sur notre Projet BIG DATA !'

# Initialiser la session Spark
# spark = SparkSession.builder \
#     .appName("SparkHadoopAPI") \
#     .getOrCreate()

@app.route('/test', methods=['GET'])
def test():
    conn = psycopg2.connect(
        dbname="aliexpressdb",
        user="user",
        password="password",
        host="postgresdb"  # This is the service name defined in docker-compose.yml
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stores")
    records = cursor.fetchall()
    cursor.close()
    conn.close()
        
    return jsonify(records)

#Endpoint pour faire les Best-of Items
@app.route('/best-of-items', methods=['GET'])
def get_best_items():
    return

#Endpoint pour faire les Best-Of Stores
@app.route('/best-of-store', methods=['GET'])
def get_best_stores():
    return

# Endpoint pour effectuer une recherche sur AliExpress
@app.route('/search', methods=['POST'])
def search_on_aliexpress():
    try:
        # Récupérer les paramètres de la recherche depuis le corps de la demande
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
        sort_criteria = search_params.get('sortCriteria', 'default')

        if sort_criteria == 'best_offers':
            items = navigator.getBestItems(items, 10)

        elif sort_criteria == 'sell_highest':
            items = navigator.getMostSelledItems(items, 10)
            
        elif sort_criteria == 'rating_highest':
            items = navigator.getBestRatedItems(items, 10)
            
        else:
            # Aucun tri spécifié, utilisez le tri par défaut (par ordre d'apparition dans les pages)
            items = navigator.getBestItems(items, 10)
            pass
        
        itemScraper = ItemScraper(driver)
        # Create the stores table
        conn = psycopg2.connect(
            dbname="aliexpressdb",
            user="user",
            password="password",
            host="postgresdb"  # This is the service name defined in docker-compose.yml
        )
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stores (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            review_percentage FLOAT,
            is_choice_store BOOLEAN,
            is_plus_store BOOLEAN,
            is_gold_store BOOLEAN,
            followers INT,
            trust_score FLOAT,
            trustworthiness VARCHAR(255)
        )
        """)
        conn.commit()
        cursor.close()

        # Create the items table
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id VARCHAR(255) PRIMARY KEY,
            title VARCHAR(255),
            price FLOAT,
            value_price FLOAT,
            shipping_price FLOAT,
            delivery_time INT,
            delivery_dates VARCHAR(255),
            rating FLOAT,
            reviews_nbr INT,
            sells_nbr INT,
            free_shipping_after FLOAT,
            trust_score FLOAT,
            trustworthiness VARCHAR(255),
            is_choice BOOLEAN,
            is_plus BOOLEAN,
            store_id VARCHAR(255),
            FOREIGN KEY (store_id) REFERENCES stores(id)
        )
        """)
        conn.commit()
        cursor.close()
        
        for item in items:
            print(f"Scraping item : {item.get('id')}")
            detailedStore, detailedItem = itemScraper.fetchAllData(item.get('id'))
            itemScraper.save_to_database(detailedStore, detailedItem, conn)
        
        conn.close()
        return jsonify({'message': message, 'items': items})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint pour le scraping d'un produit AliExpress
@app.route('/scrape_aliexpress_product', methods=['POST'])
def scrape_aliexpress_product():
    try:
        # Obtenez le produit ID à partir de la requête POST
        data = request.get_json()
        product_id = data.get('product_id')

        # Vérifiez si l'ID du produit est présent
        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400

        # Créez une instance du scraper
        scraper_instance = ItemScraper(driver)

        # Appel à la fonction fetchAllData du scraper
        store, item = scraper_instance.fetchAllData(product_id)
        conn = psycopg2.connect(
            dbname="aliexpressdb",
            user="user",
            password="password",
            host="postgresdb"  # This is the service name defined in docker-compose.yml
        )
        scraper_instance.save_to_database(store, item, conn)
        
        result = {
            'store': store,
            'item': item
        }
        
        conn.close()

        if result:
            return jsonify(result), 200
        else:
            return jsonify({'error': 'Failed to fetch data'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)