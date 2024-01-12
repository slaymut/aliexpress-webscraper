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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ItemScraper:
  def __init__(self, driver):
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
  def checkStoreLegitimacy(self, store):
    if store['isChoiceStore']:
      store['trustScore'] = 90
      store['trustworthiness'] = 'Très fiable. Recommandé par AliExpress en tant que magasin de choix.'
    else:
      percentage = store['reviewPercentage']
      followers = store['followers']
      
      trust_score = calculate_trust_score_store(followers, percentage)
      trustworthiness = classify_trustworthiness(trust_score)
      
      store['trustScore'] = trust_score
      if store['isPlusStore'] or store['isGoldStore']:
        store['trustScore'] += 5 if store['trustScore'] < 95 else 0
      store['trustworthiness'] = trustworthiness
      
    # print("Store Trust Score: ", store['trustScore'])
    # print("Store Trustworthiness: ", store['trustworthiness'])
      
  # Check if the product is a legit product
  def checkProductLegitimacy(self, item):
    if item['isChoice']:
      item['trustScore'] = 90
      item['trustworthiness'] = 'Très fiable. Recommandé par AliExpress en tant que produit de choix.'
    else:
      rating = item['rating']
      reviews_nbr = item['reviewsNbr']
      number_of_sells = item['sellsNbr']
      price = item['price']
      
      trust_score = calculate_trust_score_product(rating, reviews_nbr, number_of_sells, price)
      trustworthiness = classify_trustworthiness(trust_score)
      
      item['trustScore'] = trust_score
      item['trustworthiness'] = trustworthiness
      if item['isPlus']:
        item['trustScore'] += 15 if item['trustScore'] < 85 else 0
      
    # print("Score de confiance du produit: ", item['trustScore'])
    # print("Fiabilité du produit: ", item['trustworthiness'])
      
  # Fetch the store data
  def fetchStoreData(self, soup: BeautifulSoup):
    try:
      isChoiceStore = self.isChoiceStore(soup)
      isPlusStore = self.isPlusStore(soup)
      isGoldStore = self.isGoldStore(soup)
      
      storeName = self.fetchElement(soup, 'a', attrs={'data-pl': 'store-name'})
      storeId = storeName['href'].split('store/')[1]
      feedbackElem = self.fetchElement(
        soup, 'div', attrs={'class': 'store-header--text--yxM1iTQ'}
      )
      
      feedback = None
      percentage = 0
      followers = 0
      
      if feedbackElem:
        feedback = feedbackElem.findChildren("strong", recursive=False)
        percentage = float(feedback[0].text.strip('%'))
        followers = format_follower_count(feedback[1].text)
      
      store = {
        'id': storeId,
        'name': storeName.text,
        'reviewPercentage': percentage,
        'isChoiceStore': isChoiceStore,
        'isPlusStore': isPlusStore,
        'isGoldStore': isGoldStore,
        'followers': followers,
        'trustScore': 0,
        'trustworthiness': 'Très peu fiable'
      }
      
      self.checkStoreLegitimacy(store)
      return store
    except Exception as e:
      print(f"Erreur lors de l'extraction des données du magasin : {e}")
      return None
    
  # Fetch the shipping data for classic labeled products
  def fetchShippingDataClassic(self, soup: BeautifulSoup, item):
    shippingPrice = self.fetchElement(soup, 'div', attrs={'class': 'dynamic-shipping-line dynamic-shipping-titleLayout'})
    shippingDeliveryInfos = self.fetchElements(soup, 'div', attrs={'class': 'dynamic-shipping-line dynamic-shipping-contentLayout'})
    
    if shippingPrice:
      # Extract shipping price
      shipping_price_match = re.search(r'Livraison:\s+([\d,]+)€', shippingPrice.text)
      if shipping_price_match:
        shipping_price = shipping_price_match.group(1)
        item['shippingPrice']  = float(shipping_price.replace(',', '.'))
      else:
        item['shippingPrice']  = None
    
    if shippingDeliveryInfos:
      for info in shippingDeliveryInfos:
        # Extract delivery time
        delivery_time_match = re.search(r'Livraison en (\d+) jours', info.text)
        if delivery_time_match:
          delivery_time = delivery_time_match.group(1)
          item['deliveryTime'] = int(delivery_time)
        
        # Extract delivery date
        if "livraison le" in info.text or "livrée d'ici le" in info.text or "entre le" in info.text:
          result = info.text.split("le", 1)[-1].strip()
          item['deliveryDates'].append(result)
    
    # print(f"Shipping Price: {item['shippingPrice']}")
    # print(f"Delivery Time: {item['deliveryTime']}")
    # print(f"Delivery Date: {item['deliveryDates']}")
        
    
  # Fetch the shipping data for choice labeled products
  def fetchShippingDataChoice(self, soup: BeautifulSoup, item):
    shippings = self.fetchElements(soup, 'div', attrs={'class': 'dynamic-shipping-line dynamic-shipping-contentLayout'})
    
    if shippings:
      for shipping in shippings:
        # Extract shipping price
        shipping_price_match = re.search(r'Livraison:\s+([\d,]+)€', shipping.text)
        
        if shipping_price_match:
          shipping_price = shipping_price_match.group(1)
          item['shippingPrice'] = float(shipping_price.replace(',', '.'))
          
          # Extract free shipping information
          free_shipping_match = re.search(r'ou gratuite dès ([\d,]+)€', shipping.text)
          if free_shipping_match:
            free_shipping_threshold = free_shipping_match.group(1)
            item['freeShippingAfter'] = float(free_shipping_threshold.replace(',', '.'))
          else:
            item['freeShippingAfter'] = None
        else:
          item['shippingPrice']  = None

        # Extract delivery time
        delivery_time_match = re.search(r'Livré en (\d+) jours', shipping.text)
        if delivery_time_match:
          delivery_time = delivery_time_match.group(1)
          item['deliveryTime'] = int(delivery_time)
          item['deliveryDates'].append(shipping.text.split("le", 1)[-1].strip())
    
    # print(f"Shipping Price: {item['shippingPrice']}")
    # print(f"Delivery Time: {item['deliveryTime']}")
    # print(f"Delivery Date: {item['deliveryDates']}")
    # print(f"Free Shipping Threshold: {item['freeShippingAfter']}")
    
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
      
      item = {
        'id': product_id,
        'title': title.text,
        'price': float(itemPrice.text.replace(' ', '').strip('€').replace(',', '.')),
        'valuePrice': float(itemValue.text.replace(' ', '').strip('€').replace(',', '.')),
        'shippingPrice': 0,
        'deliveryTime': 0,
        'deliveryDates': [],
        'rating': float(rating),
        'reviewsNbr': int(reviewNumber),
        'sellsNbr': sellsNumber,
        'isChoice': isChoice,
        'isPlus': isPlus
      }
      
      if isChoice:
        self.fetchShippingDataChoice(soup, item)
      else:
        self.fetchShippingDataClassic(soup, item)
        
      self.checkProductLegitimacy(item)
      return item
    except Exception as e:
      print(f"Erreur lors de l'extraction des données du produit : {e}")
      return None  
      
  def save_to_database(self, store, item, conn):
    try:
      aliexpressStore = AliExpressStore(
        id=store['id'],
        name=store['name'],
        reviewPercentage=store['reviewPercentage'],
        isChoiceStore=store['isChoiceStore'],
        isPlusStore=store['isPlusStore'],
        isGoldStore=store['isGoldStore'],
        followers=store['followers'],
        trustScore=store['trustScore'],
        trustworthiness=store['trustworthiness']
      )

      # Insert the AliExpressStore object into the database
      cursor = conn.cursor()
      cursor.execute("""
        INSERT INTO stores (id, name, reviewPercentage, isChoiceStore, isPlusStore, isGoldStore, followers, trustScore, trustworthiness)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
      """, (
        aliexpressStore.id,
        aliexpressStore.name,
        aliexpressStore.reviewPercentage,
        aliexpressStore.isChoiceStore,
        aliexpressStore.isPlusStore,
        aliexpressStore.isGoldStore,
        aliexpressStore.followers,
        aliexpressStore.trustScore,
        aliexpressStore.trustworthiness
      ))
      conn.commit()
      cursor.close()
      
      aliexpressItem = AliExpressItem(
        id=item['id'],
        title=item['title'],
        price=item['price'],
        valuePrice=item['valuePrice'] if 'valuePrice' in item else None,
        shippingPrice=item['shippingPrice'] if 'shippingPrice' in item else None,
        deliveryTime=item['deliveryTime'] if 'deliveryTime' in item else None,
        deliveryDates=item['deliveryDates'] if 'deliveryDates' in item else None,
        rating=item['rating'] if 'rating' in item else None,
        reviewsNbr=item['reviewsNbr'] if 'reviewsNbr' in item else None,
        sellsNbr=item['sellsNbr'] if 'sellsNbr' in item else None,
        freeShippingAfter=item['freeShippingAfter'] if 'freeShippingAfter' in item else None,
        trustScore=item['trustScore'],
        trustworthiness=item['trustworthiness'],
        isChoice=item['isChoice'],
        isPlus=item['isPlus'],
        store=aliexpressStore.id
      )

      # Insert the AliExpressItem object into the database
      cursor = conn.cursor()
      cursor.execute("""
        INSERT INTO items (id, title, price, valuePrice, shippingPrice, deliveryTime, deliveryDates, rating, reviewsNbr, sellsNbr, freeShippingAfter, trustScore, trustworthiness, isChoice, isPlus, store)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
      """, (
        aliexpressItem.id,
        aliexpressItem.title,
        aliexpressItem.price,
        aliexpressItem.valuePrice,
        aliexpressItem.shippingPrice,
        aliexpressItem.deliveryTime,
        aliexpressItem.deliveryDates,
        aliexpressItem.rating,
        aliexpressItem.reviewsNbr,
        aliexpressItem.sellsNbr,
        aliexpressItem.freeShippingAfter,
        aliexpressItem.trustScore,
        aliexpressItem.trustworthiness,
        aliexpressItem.isChoice,
        aliexpressItem.isPlus,
        aliexpressItem.store
      ))
      conn.commit()
      cursor.close()
      print("Item & store saved to database.")
    except Exception as e:
      print(f"Error: Item & store not saved to database.: {e}")
    

  def fetchAllData(self, product_id):
    url = f"https://fr.aliexpress.com/item/{product_id}.html"
    
    # Navigate to the website
    self.driver.get(url)
    
    wait = WebDriverWait(self.driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pdp-body-top-right")))
    
    print("meow")
    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
    
    store = self.fetchStoreData(soup)
    item = self.fetchItemData(soup, product_id)
    
    if store and item:
      return store, item
    else:
      print(f"Failed to fetch store or item data for product {product_id}. Data not saved to CSV.")