import sys
import os

# Ajouter le chemin du dossier parent au chemin de recherche des modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import csv
from selenium import webdriver
from bs4 import BeautifulSoup
from scraper.helper import *
from scraper.AliExpressItem import AliExpressItem
from scraper.AliExpressStore import AliExpressStore
import re

class ItemScraper:
  def __init__(self, driver_path):
    self.driver_path = driver_path
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    
    driver = webdriver.Chrome(self.driver_path, options=options)
    self.driver = driver
    self.processed_products = set()

  def fetchElement(self, soup: BeautifulSoup, tag_name, attrs=None):
    element = soup.find(tag_name, attrs=attrs)

    if element:
      return element
    else:
      print(f"No element found with tag name '{tag_name}'")
      
  def fetchElements(self, soup: BeautifulSoup, tag_name, attrs=None):
    element = soup.find_all(tag_name, attrs=attrs)

    if element:
      return element
    else:
      print(f"No element found with tag name '{tag_name}'")
      
  # Check if the product is a choice labeled product
  def isChoice(self, soup: BeautifulSoup):
    element = soup.find('img', attrs={'src': 'https://ae01.alicdn.com/kf/Sc944611b328f4e8bbc748456dcf64531R/254x64.png_.webp'})
    
    if element:
      return True
    else:
      return False
    
  # Check if the store is a choice labeled store
  def isChoiceStore(self, soup: BeautifulSoup):
    element = soup.find('img', attrs={'src': 'https://ae01.alicdn.com/kf/S1a258e22376e4cef8dc8bfd3fa9c3c5ep/276x96.png_.webp', 'class': 'store-header--choiceTag--PwLr9jt'})
    
    if element:
      return True
    else:
      return False
  
  # Check if the store is a plus labeled store
  def isPlusStore(self, soup: BeautifulSoup):
    element = soup.find('img', attrs={'src': 'https://ae01.alicdn.com/kf/Sacd4f9786c374f4ea65f91d8a33f8028W/108x64.png_.webp'})
    
    if element:
      return True
    else:
      return False
  
  # Check if the store is a gold labeled store
  def isGoldStore(self, soup: BeautifulSoup):
    element = soup.find('img', attrs={'src': 'https://ae01.alicdn.com/kf/H625437a088584b54aaa0e263fd316eff9/176x60.png_.webp'})
    
    if element:
      return True
    else:
      return False
    
  # Check if the product is a plus labeled product
  def isPlus(self, soup: BeautifulSoup):
    element = soup.find('img', attrs={'src': 'https://ae01.alicdn.com/kf/Sefceb8990ff84649b50ce15d2bc46122H/128x64.png_.webp'})
    
    if element:
      return True
    else:
      return False
  
  # Check if the store is a legit store
  def checkStoreLegitimacy(self, store: AliExpressStore):
    if store.isChoiceStore:
      store.trustScore = 90
      store.trustworthiness = 'Highly Trustworthy. Recommended By AliExpress as a Choice Store.'
    else:
      percentage = store.reviewPercentage
      followers = store.followers
      
      trust_score = calculate_trust_score_store(followers, percentage)
      trustworthiness = classify_trustworthiness(trust_score)
      
      store.trustScore = trust_score
      if store.isPlusStore or store.isGoldStore:
        store.trustScore += 5 if store.trustScore < 95 else 0
      store.trustworthiness = trustworthiness
      
    print("Store Trust Score: ", store.trustScore)
    print("Store Trustworthiness: ", store.trustworthiness)
      
  # Check if the product is a legit product
  def checkProductLegitimacy(self, item: AliExpressItem):
    if item.isChoice:
      item.trustScore = 90
      item.trustworthiness = 'Highly Trustworthy. Recommended By AliExpress as a Choice Product.'
    elif item.isPlus:
      item.trustScore = 90
      item.trustworthiness = 'Highly Trustworthy. Recommended By AliExpress as a Plus Product.'
    else:
      rating = item.rating
      reviews_nbr = item.reviewsNbr
      number_of_sells = item.sellsNbr
      price = item.price
      
      trust_score = calculate_trust_score_product(rating, reviews_nbr, number_of_sells, price)
      trustworthiness = classify_trustworthiness(trust_score)
      
      item.trustScore = trust_score
      item.trustworthiness = trustworthiness
      
    print("Product Trust Score: ", item.trustScore)
    print("Product Trustworthiness: ", item.trustworthiness)
      
  # Fetch the store data
  def fetchStoreData(self, soup: BeautifulSoup):
    try:
      isChoiceStore = self.isChoiceStore(soup)
      isPlusStore = self.isPlusStore(soup)
      isGoldStore = self.isGoldStore(soup)
      
      storeName = self.fetchElement(soup, 'a', attrs={'data-pl': 'store-name'})
      feedbackElem = self.fetchElement(
        soup, 'div', attrs={'class': 'store-header--text--yxM1iTQ'}
      )
      
      feedback = None
      percentage = None
      followers = None
      
      if feedbackElem:
        feedback = feedbackElem.findChildren("strong", recursive=False)
        percentage = float(feedback[0].text.strip('%'))
        followers = format_follower_count(feedback[1].text)
      
      store = AliExpressStore(
        storeName.text,
        percentage,
        isChoiceStore,
        isPlusStore,
        isGoldStore,
        followers
      )
      
      self.checkStoreLegitimacy(store)
      if store:  # Assurez-vous que l'objet store a été correctement extrait
        print("Données du magasin extraites avec succès.")
        return store
      else:
        print("Échec de l'extraction des données du magasin.")
        return None
    except Exception as e:
      print(f"Erreur lors de l'extraction des données du magasin : {e}")
      return None
    
  # Fetch the shipping data for classic labeled products
  def fetchShippingDataClassic(self, soup: BeautifulSoup, item: AliExpressItem):
    shippingPrice = self.fetchElement(soup, 'div', attrs={'class': 'dynamic-shipping-line dynamic-shipping-titleLayout'})
    shippingDeliveryInfos = self.fetchElements(soup, 'div', attrs={'class': 'dynamic-shipping-line dynamic-shipping-contentLayout'})
    
    # Extract shipping price
    shipping_price_match = re.search(r'Livraison:\s+([\d,]+)€', shippingPrice.text)
    if shipping_price_match:
      shipping_price = shipping_price_match.group(1)
      item.shippingPrice = float(shipping_price.replace(',', '.'))
    else:
      item.shippingPrice = 0
    
    for info in shippingDeliveryInfos:
      # Extract delivery time
      delivery_time_match = re.search(r'Livraison en (\d+) jours', info.text)
      if delivery_time_match:
        delivery_time = delivery_time_match.group(1)
        item.deliveryTime = int(delivery_time)
      
      # Extract delivery date
      if "livraison le" in info.text or "livrée d'ici le" in info.text or "entre le" in info.text:
        result = info.text.split("le", 1)[-1].strip()
        item.deliveryDates.append(result)
    
    print(f"Shipping Price: {item.shippingPrice}")
    print(f"Delivery Time: {item.deliveryTime}")
    print(f"Delivery Date: {item.deliveryDates}")
        
    
  # Fetch the shipping data for choice labeled products
  def fetchShippingDataChoice(self, soup: BeautifulSoup, item: AliExpressItem):
    shippings = self.fetchElements(soup, 'div', attrs={'class': 'dynamic-shipping-line dynamic-shipping-contentLayout'})
    
    for shipping in shippings:
      # Extract shipping price
      shipping_price_match = re.search(r'Livraison:\s+([\d,]+)€', shipping.text)
      
      if shipping_price_match:
        shipping_price = shipping_price_match.group(1)
        item.shippingPrice = float(shipping_price.replace(',', '.'))
        
        # Extract free shipping information
        free_shipping_match = re.search(r'ou gratuite dès ([\d,]+)€', shipping.text)
        if free_shipping_match:
          free_shipping_threshold = free_shipping_match.group(1)
          item.freeShippingAfter = float(free_shipping_threshold.replace(',', '.'))
        else:
          item.freeShippingAfter = None
      else:
        item.shippingPrice = 0

      # Extract delivery time
      delivery_time_match = re.search(r'Livré en (\d+) jours', shipping.text)
      if delivery_time_match:
        delivery_time = delivery_time_match.group(1)
        item.deliveryTime = int(delivery_time)
        item.deliveryDates.append(shipping.text.split("le", 1)[-1].strip())
    
    print(f"Shipping Price: {item.shippingPrice}")
    print(f"Delivery Time: {item.deliveryTime}")
    print(f"Delivery Date: {item.deliveryDates}")
    print(f"Free Shipping Threshold: {item.freeShippingAfter}")
    
  # Fetch the product data
  def fetchItemData(self, soup: BeautifulSoup, product_id):
    try:
      title = self.fetchElement(soup, 'h1', attrs={'data-pl': 'product-title'})
      
      itemValue = self.fetchElement(soup, 'span', attrs={'class': 'price--originalText--Zsc6sMv'})
      itemPrice = self.fetchElement(soup, 'div', attrs={'class': 'product-price-current'})
      likes = self.fetchElement(soup, 'span', attrs={'class': 'share-and-wish--wishText--g_o_zG7'})
      
      # Extract Product Review
      productReview = self.fetchElement(soup, 'div', attrs={'data-pl': 'product-reviewer'})

      rating = 0
      reviewNumber = 0
      sellsNumber = 0

      if productReview:
        rating_element = productReview.findChild("strong", recursive=False)
        if rating_element:
          rating = rating_element.text.strip()

        reviewNumber_element = productReview.findChild("a", recursive=False)
        if reviewNumber_element:
          reviewNumber = reviewNumber_element.text.split(' ')[0].strip()

        sellsNumber_elements = productReview.findChildren("span", recursive=False)
        if len(sellsNumber_elements):
          numbers = re.findall(r'\d+', sellsNumber_elements[-1].text)
          sellsNumber = int(''.join(numbers))
      
      isChoice = self.isChoice(soup)
      isPlus = self.isPlus(soup)
      
      # print(f"Title: {title.text}")
      # print(f"Discount Price: {itemPrice.text}")
      # print(f"Real Price: {itemValue.text}")
      # print(f"Likes: {likes.text}")
      # print(f"Rating: {rating}")
      # print(f"Reviews: {reviewNumber}")
      # print(f"Sells: {sellsNumber}")
      
      item = AliExpressItem(
        id=product_id,
        title=title.text,
        price=float(itemPrice.text.strip('€').replace(',', '.')),
        valuePrice=float(itemValue.text.strip('€').replace(',', '.')),
        shippingPrice=0,
        deliveryTime=0,
        deliveryDates=[],
        rating=float(rating),
        reviewsNbr=int(reviewNumber),
        sellsNbr=sellsNumber,
        isChoice=isChoice,
        isPlus=isPlus
      )
      
      if isChoice:
        self.fetchShippingDataChoice(soup, item)
      else:
        self.fetchShippingDataClassic(soup, item)
        
      self.checkProductLegitimacy(item)
      if item:  # Assurez-vous que l'objet item a été correctement extrait
        print("Données de l'article extraites avec succès.")
        return item
      else:
        print("Échec de l'extraction des données de l'article.")
        return None      
    except Exception as e:
      print(f"Erreur lors de l'extraction des données du produit : {e}")
      return None  
  
  def save_to_csv(self, item, store, filename="aliexpress_data.csv"):
    # Vérifiez si le produit a déjà été traité
    if item.id in self.processed_products:
      print(f"Produit {item.id} déjà traité. Saut du traitement.")
      return

       # Ajout de l'ID du produit à l'ensemble des produits traités
    self.processed_products.add(item.id)

    try:
      # Ajoutez des valeurs par défaut pour les champs manquants
      item_id = item.id if item is not None else "Inconnu"
      store_trust_score = store.trustScore if store is not None else "Inconnu"
      # ... (autres champs) ...
      file_exists = os.path.isfile(filename)
      with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if not file_exists:
          writer.writerow(['Product ID', 'Store Trust Score', 'Store Trustworthiness', 'Shipping Price', 'Delivery Time', 'Delivery Dates', 'Product Trustworthiness'])

        writer.writerow([
          item.id, 
          store.trustScore, 
          store.trustworthiness, 
          item.shippingPrice, 
          item.deliveryTime, 
          '; '.join(item.deliveryDates), 
          item.trustworthiness
        ])
        print("Données enregistrées dans le fichier CSV.")
    except Exception as e:
      print(f"Erreur lors de l'enregistrement dans le fichier CSV : {e}")
    

  def fetchAllData(self, product_id,filename="aliexpress_data.csv"):
    url = f"https://fr.aliexpress.com/item/{product_id}.html"
    
    # Navigate to the website
    self.driver.get(url)
    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    print(f"Extraction des données pour le produit {product_id}...")
    
    
    store = self.fetchStoreData(soup)
    item = self.fetchItemData(soup, product_id)
    
    if store and item:
      print(f"Store and item data fetched successfully for product {product_id}. Saving to CSV...")
      self.save_to_csv(item, store, filename)
    else:
       print(f"Failed to fetch store or item data for product {product_id}. Data not saved to CSV.")
    print("Extraction process completed.")
  
     # Vérifiez si store et item ne sont pas None avant de sauvegarder
    if store is not None and item is not None:
        # Enregistrez les données dans un fichier CSV
        self.save_to_csv(item, store, filename)
    else:
        print(f"Failed to fetch data for product ID {product_id}")
