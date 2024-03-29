import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from selenium import webdriver
from flask import Flask, request, jsonify, render_template
from scraper.AliExpressNavigator import Navigator
from scraper.AliExpressItemScraper import ItemScraper
from flask_cors import CORS
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from flask_wtf.csrf import CSRFProtect
from forms import AliExpressSearchForm
import psycopg2

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
    
    if form.is_submitted():
        # Traitez les données du formulaire ici si le formulaire a été soumis
        search_filter = form.search_filter.data
        
        # Vérifie si le filtre de recherche est vide
        if not search_filter:
            return render_template('web_interface.html', form=form, error="Veuillez entrer un filtre de recherche.")
        
        num_pages = int(form.num_pages.data) if form.num_pages.data else 1
        choice_filter = form.choice_filter.data
        plus_filter = form.plus_filter.data
        free_shipping_filter = form.free_shipping_filter.data
        four_stars_and_up_filter = form.four_stars_and_up_filter.data
        # maximum = float(form.maximum.data)
        # minimum = float(form.minimum.data)
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
                fourStarsAndUpFilter=four_stars_and_up_filter
            )
            items.extend(page_items)

            if len(page_items) < 60:
                message = f"Le scraping a été interrompu sur la page {page} sur {num_pages} demandées car nous avons atteint le maximum de pages disponibles."
                break
            else:
                message = f"Le scraping a été effectué sur les {num_pages} pages."
        
        if len(items) == 0:
            return render_template('web_interface.html', form=form, error="Aucun résultat n'a été trouvé pour votre recherche.")
        
        if sort_criteria == 'best_offers':
            items = navigator.getBestItems(items, 10)
            type = f"Nous avons scrapé pour vous les 10 meilleures offres selon la fiabilité !"

        elif sort_criteria == 'sell_highest':
            items = navigator.getMostSelledItems(items, 10)
            type = f"Nous avons scrapé pour vous les 10 produits les plus vendus !"
            
        elif sort_criteria == 'rating_highest':
            items = navigator.getBestRatedItems(items, 10)
            type = f"Nous avons scrapé pour vous les 10 produits les mieux notés !"
            
        else:
            # Aucun tri spécifié, utilisez le tri par défaut (par ordre d'apparition dans les pages)
            items = navigator.getBestItems(items, 10)
            type = f"Nous avons scrapé pour vous les 10 meilleures offres selon la fiabilité !"
            pass

        itemScraper = ItemScraper(driver)
        
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
        return render_template('web_interface_result.html', type=type, message=message, allData=dataFormatted)

    # Si la méthode n'est pas POST, ou si la validation du formulaire échoue
    return render_template('web_interface.html', form=form)

# Endpoint for retrieving the best rated stores
@app.route('/best-rated-stores', methods=['GET'])
def get_best_stores():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        dbname="aliexpressdb",
        user="user",
        password="password",
        host="postgresdb" 
    )
    
    # Create a cursor object to execute SQL queries
    cur = conn.cursor()
    
    # Execute the SQL query to retrieve the best rated stores
    cur.execute("SELECT * FROM stores ORDER BY trustScore DESC LIMIT 10")
    
    # Fetch all the rows returned by the query
    rows = cur.fetchall()
    
    # Get the column names from the cursor description
    column_names = [desc[0] for desc in cur.description]
    
    # Create a list of dictionaries where each dictionary represents a row with column names as keys
    data = [dict(zip(column_names, row)) for row in rows]
    
    if len(data) == 0:
        return render_template('web_interface_result_stores.html', 
                           type="Aucun magasin n'a été trouvé pour l'instant..", 
                           allData=data)
    
    # Close the cursor and the database connection
    cur.close()
    conn.close()
    
    # Return the retrieved stores as JSON response
    return render_template('web_interface_result_stores.html', 
                           type="Voici les magasins les plus fiables et meilleurs notés", 
                           allData=data)

# Endpoint for retrieving items with the best trustScore to price ratio
@app.route('/best-trustscore-items', methods=['GET'])
def get_best_trustscore_items():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        dbname="aliexpressdb",
        user="user",
        password="password",
        host="postgresdb" 
    )
    
    # Create a cursor object to execute SQL queries
    cur = conn.cursor()
    
    # Execute the SQL query to retrieve items with the best trustScore to price ratio
    cur.execute("SELECT * FROM items ORDER BY trustScore/price DESC LIMIT 10")
    
    # Fetch all the rows returned by the query
    rows = cur.fetchall()
    
        # Get the column names from the cursor description
    column_names = [desc[0] for desc in cur.description]
    
    # Create a list of dictionaries where each dictionary represents a row with column names as keys
    data = [dict(zip(column_names, row)) for row in rows]
    
    if len(data) == 0:
        return render_template('web_interface_result_items.html', 
                           type="Aucun article n'a été trouvé pour l'instant..", 
                           allData=data)
    
    # Close the cursor and the database connection
    cur.close()
    conn.close()
    
    # Return the retrieved items as JSON response
    return render_template('web_interface_result_items.html', 
                           type="Voici les articles avec le meilleur rapport trustScore/prix parmis les meilleurs items sauvegardés!", 
                           allData=data)

# Endpoint pour le scraping d'un produit AliExpress
@app.route('/scrape_aliexpress_product', methods=['POST'])
def scrape_aliexpress_product():
    try:
        product_id = request.form.get('product_id')

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
            host="postgresdb"
        )
        scraper_instance.save_to_database(store, item, conn)
        
        result = {
            'store': store,
            'item': item
        }
        
        conn.close()

        if result:
            return render_template('web_interface_result.html', result=result)
        else:
            return render_template('web_interface_result.html', error='Failed to fetch data')
    except Exception as e:
        return render_template('web_interface_result.html', error=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)