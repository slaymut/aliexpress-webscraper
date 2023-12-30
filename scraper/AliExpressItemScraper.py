from selenium import webdriver
from bs4 import BeautifulSoup
from helper import *
from AliExpressItem import AliExpressItem
from AliExpressStore import AliExpressStore
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
    element = soup.find('img', attrs={'src': 'https://ae01.alicdn.com/kf/S1a258e22376e4cef8dc8bfd3fa9c3c5ep/276x96.png_.webp'})
    
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
    elif store.isPlusStore:
      store.trustScore = 90
      store.trustworthiness = 'Highly Trustworthy. Recommended By AliExpress as a Plus Store.'
    elif store.isGoldStore:
      store.trustScore = 90
      store.trustworthiness = 'Highly Trustworthy. Recommended By AliExpress as a Plus Store.'
    else:
      percentage = store.reviewPercentage
      followers = store.followers
      
      trust_score = calculate_trust_score_store(followers, percentage)
      trustworthiness = classify_trustworthiness(trust_score)
      store.trustScore = trust_score
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
      
    print("Trust Score: ", item.trustScore)
    print("Trustworthiness: ", item.trustworthiness)
      
  # Fetch the store data
  def fetchStoreData(self, soup: BeautifulSoup):
    isChoiceStore = self.isChoiceStore(soup)
    isPlusStore = self.isPlusStore(soup)
    isGoldStore = self.isGoldStore(soup)
    
    storeName = self.fetchElement(soup, 'a', attrs={'data-pl': 'store-name'})
    feedback = self.fetchElement(
      soup, 'div', attrs={'class': 'store-header--text--yxM1iTQ'}
    ).findChildren("strong", recursive=False)

    percentage = float(feedback[0].text.strip('%'))
    followers_text = feedback[1].text
    followers = format_follower_count(followers_text)
    
    store = AliExpressStore(
      storeName.text,
      percentage,
      isChoiceStore,
      isPlusStore,
      isGoldStore,
      followers
    )
    
    self.checkStoreLegitimacy(store)
    
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
    title = self.fetchElement(soup, 'h1', attrs={'data-pl': 'product-title'})
    
    itemValue = self.fetchElement(soup, 'span', attrs={'class': 'price--originalText--Zsc6sMv'})
    itemPrice = self.fetchElement(soup, 'div', attrs={'class': 'product-price-current'})
    likes = self.fetchElement(soup, 'span', attrs={'class': 'share-and-wish--wishText--g_o_zG7'})
    
    productReview = self.fetchElement(soup, 'div', attrs={'data-pl': 'product-reviewer'})
    
    rating = productReview.findChild("strong", recursive=False)
    if rating:
      rating = rating.text.strip()
    else:
      rating = 0
    
    reviewNumber = productReview.findChild("a", recursive=False)
    if reviewNumber:
      reviewNumber = reviewNumber.text.split(' ')[0].strip()
    else:
      reviewNumber = 0
      
    sellsNumber = productReview.findChildren("span", recursive=False)
    if len(sellsNumber):
      numbers = re.findall(r'\d+', sellsNumber[len(sellsNumber)-1].text)
      sellsNumber = int(''.join(numbers))
    else:
      sellsNumber = 0
    
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
  
  def fetchAllData(self, product_id):
    url = f"https://fr.aliexpress.com/item/{product_id}.html"
    
    # Navigate to the website
    self.driver.get(url)
    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
    
    self.fetchStoreData(soup)
    self.fetchItemData(soup, product_id)

# Usage example
scraper = ItemScraper('C:\\Users\\slaymut\\Documents\\Web Scraper Aliexpress\\aliexpress-webscraper\\chrome-driver\\chromedriver.exe')
scraper.fetchAllData("1005004838183959")
