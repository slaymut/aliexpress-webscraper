
import urllib.parse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import re
import csv
import time
from scraper.helper import *
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

class Navigator:
  def __init__(self, driver):
    self.driver = driver
    
  # Load all the items on the page
  def loadFullPage(self):
    total_height = self.driver.execute_script("return document.body.scrollHeight")
    height_iteration = total_height / 12
    current_height = 0
    
    lazy_load_items = self.driver.find_elements_by_class_name('lazy-load')

    while len(lazy_load_items) and current_height <= total_height:
      self.driver.execute_script(f"window.scrollTo(0, {current_height});")
      
      # Check if there are lazy-load items
      lazy_load_items = self.driver.find_elements_by_class_name('lazy-load')
      if len(lazy_load_items):
        try:
          # Wait until the items on lazy load are loaded
          section_locator = (By.CLASS_NAME, 'lazy-load')
          WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(section_locator))
        except TimeoutException:
          break
        # Scroll down by one-fourth of the page height
        current_height += height_iteration
    
    lazy_load_items = self.driver.find_elements_by_class_name('lazy-load')
      
  # Gather all the data from an item
  def gatherData(self, item):
    itemFormatted = {
      'title': '',
      'id': '',
      'rating': None,
      'sells': None,
      'priceSold': 0.0,
      'priceOriginal': None,
      'shippingPrice': None,
      'isChoice': None,
      'isPlus': None,
      'trustScore': None,
      'trustworthiness': None,
      'store': None
    }
    # Get the title
    itemFormatted['title'] = item.find('h1').text.strip()
    # Get the product id
    itemFormatted['id'] = item.find('a')['href'].split('/')[-1].split('?')[0]
    
    # Get the ratings
    ratings = item.find_all('div', attrs={'class': 'multi--evalutionModal--Ktfxu90'})
    if ratings:
      stars = 0
      for rating in ratings:
        star = float(rating.find('div', attrs={'class': 'multi--progress--2E4WzbQ'})['style'].split(':')[1].strip('px;'))
        stars += star/10
      itemFormatted['rating'] = stars
    else:
      itemFormatted['rating'] = None
      
    # Get the number of sells
    sells = item.find('span', attrs={'class': 'multi--trade--Ktbl2jB'})
    if sells:
      numbers = re.findall(r'\d+', sells.text)
      if 'k' in sells.text or 'K' in sells.text:
        result *= 1000
      elif 'm' in sells.text or 'M' in sells.text:
        result *= 1000000
      result = int(''.join(numbers))
      itemFormatted['sells'] = result
    else:
      itemFormatted['sells'] = None
      
    # Get the price
    price_sold = item.find('div', attrs={'class': 'multi--price-sale--U-S0jtj'}).text.strip('€').replace(',', '.').replace(' ', '')
    itemFormatted['priceSold'] = float(price_sold)
    
    # Get the original price
    priceOriginal = item.find('div', attrs={'class': 'multi--price-original--1zEQqOK'})
    if priceOriginal.text != '':
      itemFormatted['priceOriginal'] = float(priceOriginal.text.strip('€').replace(',', '.').replace(' ', ''))
    else:
      itemFormatted['priceOriginal'] = None
    
    # Get the shipping price
    service = item.find('div', attrs={'class': 'multi--serviceContainer--3vRdzWN'})
    if service:
      serviceText = service.find('span').text
      if serviceText == 'Livraison gratuite':
        itemFormatted['shippingPrice'] = 0
      else:
        shipping_price = re.search(r'envoi:\s+([\d,]+)€', serviceText)
        if shipping_price:
          itemFormatted['shippingPrice'] = float(shipping_price.group(1).replace(',', '.'))
        else:
          itemFormatted['shippingPrice'] = None
      
      choice = service.findChild('img')
      plus = item.find('img', attrs={'src': 'https://ae01.alicdn.com/kf/Sacd4f9786c374f4ea65f91d8a33f8028W/108x64.png'})
      
      if choice:
        itemFormatted['isChoice'] = True
        itemFormatted['trustScore'] = 90
        itemFormatted['trustworthiness'] = 'Very Trustworthy. Choice Item'
      elif plus:
        itemFormatted['isPlus'] = True
        itemFormatted['trustScore'] = 80
        itemFormatted['trustworthiness'] = 'Trustworthy. Plus Item'
      else:
        itemFormatted['isChoice'] = False
        itemFormatted['isPlus'] = False
        itemFormatted['trustScore'] = calculate_trust_score_in_list(itemFormatted['priceSold'], itemFormatted['rating'], itemFormatted['sells'])
        itemFormatted['trustworthiness'] = classify_trustworthiness(itemFormatted['trustScore'])
    else:
      itemFormatted['shippingPrice'] = None
      itemFormatted['isChoice'] = False
      itemFormatted['isPlus'] = False
      itemFormatted['trustScore'] = 0
      itemFormatted['trustworthiness'] = 'Highly Untrustworthy. No Shipping Information'
      
    # Get the store name
    itemFormatted['store'] = item.find('span', attrs={'class': 'cards--store--3GyJcot'}).text.strip()
    return itemFormatted
    
  # Get the best items based on trust score to total price ratio
  def getBestItems(self, items, number_of_items=10):
    def trustToPriceRatio(item):
      total_price = item['priceSold']
      # If ShippingPrice Is Available
      if item['shippingPrice'] is not None:
        total_price += item['shippingPrice']

      # Avoid division by zero
      if total_price == 0:
        return 0
      return item['trustScore'] / total_price

    # Sort items based on trust score to total price ratio
    sorted_items = sorted(items, key=trustToPriceRatio, reverse=True)
    
    return sorted_items[:number_of_items]

  # Get the most sold items
  def getMostSelledItems(self, items, number_of_items=10):
    def sort_by_sells(item):
      return item['sells']
    
    sorted_items = sorted(items, key=sort_by_sells, reverse=True)
    
    return sorted_items[:number_of_items]

  # Get the best rated items
  def getBestRatedItems(self, items, number_of_items=10):
    def sort_by_rating(item):
      return item['rating']
    
    sorted_items = sorted(items, key=sort_by_rating, reverse=True)
    
    return sorted_items[:number_of_items]
  
  def getItemsBetweenPrices(self, items, minimum, maximum):
    def sort_by_price(item):
      total_price = item['priceSold']
      # If ShippingPrice Is Available
      if item['shippingPrice'] is not None:
        total_price += item['shippingPrice']
      return total_price
    
    sorted_items = sorted(items, key=sort_by_price)
    
    items_between_prices = []
    for item in sorted_items:
      total_price = item['priceSold']
      # If ShippingPrice Is Available
      if item['shippingPrice'] is not None:
        total_price += item['shippingPrice']
      
      if total_price >= minimum and total_price <= maximum:
        items_between_prices.append(item)
      
    return items_between_prices
   
  # Load the search results
  def loadPageResults(
    self,
    searchFilter,
    page=1,
    choiceFilter=False,
    plusFilter=False,
    freeShippingFilter=False,
    fourStarsAndUpFilter=False,
    maximum=0,
    minimum=0
  ):
    encodedSearchFilter = urllib.parse.quote(searchFilter)
    
    selectedSwitches = ''
    if plusFilter:
      selectedSwitches += 'mall:true,'
    if choiceFilter:
      selectedSwitches += 'sellPoint:choice_atm,'
    if fourStarsAndUpFilter:
      selectedSwitches += 'pop:true,'
    if freeShippingFilter:
      selectedSwitches += 'freeshipping:true,'
      
    if selectedSwitches is not '':
      selectedSwitches = selectedSwitches[:-1]
      selectedSwitches = urllib.parse.quote(selectedSwitches)
      selectedSwitches = '&selectedSwitches=' + selectedSwitches
      
    actualPage = None
    if page > 1:
      actualPage = f"page={page}&"
    else:
      actualPage = ''
      
      
    url = f"https://fr.aliexpress.com/w/wholesale-{encodedSearchFilter}.html?{actualPage}g=y&SearchText={encodedSearchFilter}{selectedSwitches}"

    # Navigate to the website
    self.driver.get(url)
    
    time.sleep(1)
    self.loadFullPage()

    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    items = soup.find(
      'div', attrs={'id': 'card-list'}
    ).findChildren(
      'div', attrs={'class': 'list--gallery--C2f2tvm search-item-card-wrapper-gallery'}, recursive=False
    )
    
    itemsFormatted = []
    for item in items:
      itemFormatted = self.gatherData(item)
      itemsFormatted.append(itemFormatted)

    return itemsFormatted