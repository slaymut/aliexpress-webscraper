import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import urllib.parse
from helper import calculate_trust_score_in_list, classify_trustworthiness

class Navigator:
  def __init__(self, driver_path):
    self.driver_path = driver_path
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    
    driver = webdriver.Chrome(self.driver_path, options=options)
    self.driver = driver
    
  def loadAllItems(self):
    total_height = self.driver.execute_script("return document.body.scrollHeight")
    height_iteration = total_height / 12
    current_height = 0

    while current_height <= float(total_height):
      self.driver.execute_script(f"window.scrollTo(0, {current_height});")
      
      # Check if there are lazy-load items
      lazy_load_items = self.driver.find_elements_by_class_name('lazy-load')
      if lazy_load_items:
        # Wait until the items on lazy load are loaded
        section_locator = (By.CLASS_NAME, 'lazy-load')
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(section_locator))
      
      # Scroll down by one-fourth of the page height
      current_height += height_iteration
      
  def gatherData(self, item):
    itemFormatted = {}
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
    itemFormatted['priceSold'] = float(item.find('div', attrs={'class': 'multi--price-sale--U-S0jtj'}).text.strip('€').replace(',', '.'))
    
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
  
  # # Find Similarities between items and return a list of items
  # def findSimilarities(self, items):

  def loadSearchResults(self, searchFilter, page=1, choiceFilter=False, plusFilter=False):
    encodedSearchFilter = urllib.parse.quote(searchFilter)
    selectedSwitches = ''
    if plusFilter:
      selectedSwitches += 'mall%3Atrue%2C'
    if choiceFilter:
      selectedSwitches += 'sellPoint%3Achoice_atm%2C'
      
    url = f"https://fr.aliexpress.com/w/wholesale-{encodedSearchFilter}.html?page={page}&selectedSwitches={selectedSwitches}"

    # Navigate to the website
    self.driver.get(url)
    
    self.loadAllItems()

    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    items = soup.find('div', attrs={'id': 'card-list'}).findChildren('div', attrs={'class': 'list--gallery--C2f2tvm search-item-card-wrapper-gallery'}, recursive=False)
    
    itemsFormatted = []
    for item in items:
      itemFormatted = self.gatherData(item)
      print(itemFormatted['trustworthiness'])
      itemsFormatted.append(itemFormatted)
      
    # self.findSimilarities(itemsFormatted)
      
    print(f"Found {len(items)} elements")
    
    self.driver.close()
    
navigator = Navigator('C:\\Users\\slaymut\\Documents\\Web Scraper Aliexpress\\aliexpress-webscraper\\chrome-driver\\chromedriver.exe')
navigator.loadSearchResults('meow meow')