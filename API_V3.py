from flask import Flask, request, jsonify
from AliExpressNavigator import Navigator
from pyspark.sql import SparkSession
import os

app = Flask(__name__)

# Initialiser la session Spark
spark = SparkSession.builder \
    .appName("SparkHadoopAPI") \
    .getOrCreate()

# ... (Définir d'autres endpoints si nécessaire)

# Nouvel endpoint pour effectuer une recherche sur AliExpress
@app.route('/search', methods=['POST'])
def search_on_aliexpress():
    try:
        # Récupérer les paramètres de la recherche depuis le corps de la demande
        search_params = request.json
        search_filter = search_params.get('searchFilter', '')
        page = search_params.get('page', 1)
        choice_filter = search_params.get('choiceFilter', False)
        plus_filter = search_params.get('plusFilter', False)
        free_shipping_filter = search_params.get('freeShippingFilter', False)
        four_stars_and_up_filter = search_params.get('fourStarsAndUpFilter', False)
        maximum = search_params.get('maximum', 0)
        minimum = search_params.get('minimum', 0)

        # Chemin vers le fichier ChromeDriver
        current_directory = os.getcwd()
        chrome_driver_path = os.path.join(current_directory, 'chrome-driver\\chromedriver.exe')

        # Initialiser l'objet Navigator
        navigator = Navigator(chrome_driver_path)

        # Charger les résultats de la recherche
        items = navigator.loadPageResults(
            search_filter,
            page=page,
            choiceFilter=choice_filter,
            plusFilter=plus_filter,
            freeShippingFilter=free_shipping_filter,
            fourStarsAndUpFilter=four_stars_and_up_filter,
            maximum=maximum,
            minimum=minimum
        )

        # Fermer le navigateur après avoir récupéré les résultats
        navigator.driver.quit()

        return jsonify({'items': items})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
