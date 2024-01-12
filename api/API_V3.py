import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from selenium import webdriver
from flask import Flask, request, jsonify, render_template
from scraper.AliExpressNavigator import Navigator
from scraper.AliExpressItemScraper import ItemScraper
from flask_cors import CORS
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import psycopg2
from flask_wtf.csrf import CSRFProtect
from forms import AliExpressSearchForm

# Configuration du webdriver
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

capabilities = DesiredCapabilities.CHROME
capabilities["pageLoadStrategy"] = "eager"

# Chemin du webdriver
current_directory = os.getcwd()
chrome_driver_path = os.path.join(current_directory, 'chrome-driver-docker/chromedriver')

driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options, desired_capabilities=capabilities)

# Création de l'application Flask
app = Flask(__name__)
CORS(app)
csrf = CSRFProtect(app)

# Ajout d'une clé secrète
app.config['SECRET_KEY'] = 'anitamaxwynn'
csrf.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    form = AliExpressSearchForm()
    
    if form.is_submitted():
        # Traitez les données du formulaire ici si le formulaire a été soumis
        search_filter = form.search_filter.data
        num_pages = int(form.num_pages.data)
        choice_filter = form.choice_filter.data
        plus_filter = form.plus_filter.data
        free_shipping_filter = form.free_shipping_filter.data
        four_stars_and_up_filter = form.four_stars_and_up_filter.data
        maximum = float(form.maximum.data)
        minimum = float(form.minimum.data)
        sort_criteria = form.sort_criteria.data

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
            items = navigator.getBestItems(items, 10)
            pass


        itemScraper = ItemScraper(driver)
        
        conn = psycopg2.connect(
            dbname="aliexpressdb",
            user="user",
            password="password",
            host="postgresdb" 
        )
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stores (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            reviewPercentage FLOAT,
            isChoiceStore BOOLEAN,
            isPlusStore BOOLEAN,
            isGoldStore BOOLEAN,
            followers INT,
            trustScore FLOAT,
            trustworthiness VARCHAR(255)
        )
        """)
        conn.commit()
        cursor.close()

        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id VARCHAR(255) PRIMARY KEY,
            title VARCHAR(255),
            price FLOAT,
            valuePrice FLOAT,
            shippingPrice FLOAT,
            deliveryTime INT,
            deliveryDates VARCHAR(255),
            rating FLOAT,
            reviewsNbr INT,
            sellsNbr INT,
            freeShippingAfter FLOAT,
            trustScore FLOAT,
            trustworthiness VARCHAR(255),
            isChoice BOOLEAN,
            isPlus BOOLEAN,
            store VARCHAR(255),
            FOREIGN KEY (store) REFERENCES stores(id)
        )
        """)
        conn.commit()
        cursor.close()
        
        dataFormatted = []
        for item in items:
            print(f"Scraping item : {item.get('id')}")
            detailedStore, detailedItem = itemScraper.fetchAllData(item.get('id'))
            dataFormatted.append({
                'store': detailedStore,
                'item': detailedItem
            })
            itemScraper.save_to_database(detailedStore, detailedItem, conn)
            
        conn.close()

        # Redirection de l'utilisateur vers une autre page
        return render_template('web_interface_result.html', message="Scraping completed successfully!", data=dataFormatted)

    # Si la méthode n'est pas POST, ou si la validation du formulaire échoue
    return render_template('web_interface.html', form=form)

#Endpoint pour faire les Best-of Items
# @app.route('/best-of-items', methods=['GET'])
# def get_best_items():
#     return

# #Endpoint pour faire les Best-Of Stores
# @app.route('/best-of-store', methods=['GET'])
# def get_best_stores():
#     return


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
        
    #     if result:
    #         return jsonify(result), 200
    #     else:
    #         return jsonify({'error': 'Failed to fetch data'}), 500

    # except Exception as e:
    #     return jsonify({'error': str(e)}), 500
        conn.close()

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