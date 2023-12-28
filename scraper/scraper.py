from selenium import webdriver
from bs4 import BeautifulSoup
from helper import *
from AliExpressItem import AliExpressItem

class WebScraper:
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
    
  # Check if the product is a plus labeled product
  def isPlus(self, soup: BeautifulSoup):
    element = soup.find('img', attrs={'src': 'https://ae01.alicdn.com/kf/Sefceb8990ff84649b50ce15d2bc46122H/128x64.png_.webp'})
    
    if element:
      return True
    else:
      return False
  
  # Check if the store is a legit store
  def checkStoreLegitimacy(self, soup: BeautifulSoup):
    isChoiceStore = self.isChoiceStore(soup)
    
    if isChoiceStore:
      return print('Highly Trustworthy. Recommended By AliExpress as a Choice Store.')
    else:
      storeName = self.fetchElement(soup, 'a', attrs={'data-pl': 'store-name'})
      feedback = self.fetchElement(
        soup, 'div', attrs={'class': 'store-header--text--yxM1iTQ'}
      ).findChildren("strong", recursive=False)

      percentage = float(feedback[0].text.strip('%'))
      followers_text = feedback[1].text
      followers = format_follower_count(followers_text)
      
      trust_score = calculate_trust_score_store(followers, percentage)
      trustworthiness = classify_trustworthiness(trust_score)
      
      print("Store Name: ", storeName.text)
      print("Percentage: ", percentage)
      print("Followers: ", followers)
      
      print("Trust Score: ", trust_score)
      print("Trustworthiness: ", trustworthiness)
      
  def checkProductLegitimacy(self, soup: BeautifulSoup, item: AliExpressItem):
    if item.isChoice:
      return print('Highly Trustworthy. Recommended By AliExpress as a Choice Product.')
    elif item.isPlus:
      return print('Highly Trustworthy. Recommended By AliExpress as a Plus Product.')
    else:
      rating = item.rating
      reviews_nbr = item.reviewsNbr
      number_of_sells = item.sellsNbr
      price = item.price
      
      trust_score = calculate_trust_score_product(rating, reviews_nbr, number_of_sells, price)
      trustworthiness = classify_trustworthiness(trust_score)
      
      item.trustScore = trust_score
      item.trustworthiness = trustworthiness
      
      print("Rating: ", rating)
      print("Reviews: ", reviews_nbr)
      print("Sells: ", number_of_sells)
      print("Price: ", price)
      
      print("Trust Score: ", trust_score)
      print("Trustworthiness: ", trustworthiness)
    
  # Fetch the product data
  def fetchItemData(self, product_id):
    url = f"https://fr.aliexpress.com/item/{product_id}.html"
    
    # Navigate to the website
    self.driver.get(url)
    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    title = self.fetchElement(soup, 'h1', attrs={'data-pl': 'product-title'})
    
    itemValue = self.fetchElement(soup, 'span', attrs={'class': 'price--originalText--Zsc6sMv'})
    itemPrice = self.fetchElement(soup, 'div', attrs={'class': 'product-price-current'})
    likes = self.fetchElement(soup, 'span', attrs={'class': 'share-and-wish--wishText--g_o_zG7'})
    
    productReview = self.fetchElement(soup, 'div', attrs={'data-pl': 'product-reviewer'})
    
    rating = productReview.findChild("strong", recursive=False).text.strip()
    reviewNumber = productReview.findChild("a", recursive=False).text.split(' ')[0].strip()
    sellsNumber = productReview.findChildren("span", recursive=False)[1].text.split(' ')[0]
    
    
    # shipping = self.fetchElement(soup, 'div', attrs={'class': 'dynamic-shipping-line dynamic-shipping-titleLayout'})
    shippings = self.fetchElements(soup, 'div', attrs={'class': 'dynamic-shipping-line dynamic-shipping-contentLayout'})
    
    isChoice = self.isChoice(soup)
    isPlus = self.isPlus(soup)
    
    print(f"Title: {title.text}")
    print(f"Discount Price: {itemPrice.text}")
    print(f"Real Price: {itemValue.text}")
    print(f"Likes: {likes.text}")
    print(f"Rating: {rating}")
    print(f"Reviews: {reviewNumber}")
    print(f"Sells: {sellsNumber}")
    
    item = AliExpressItem(
      product_id,
      title.text,
      float(itemPrice.text.strip('€').replace(',', '.')),
      float(itemValue.text.strip('€').replace(',', '.')),
      0,
      float(rating),
      int(reviewNumber),
      int(sellsNumber),
      isChoice,
      isPlus
    )
    
    # print(f"Shipping: {shipping.text}")
    for shipping in shippings:
      print(f"Shipping: {shipping.text}")
    
    # self.checkStoreLegitimacy(soup)

# Usage example
scraper = WebScraper('C:\\Users\\slaymut\\Documents\\Web Scraper Aliexpress\\aliexpress-webscraper\\chrome-driver\\chromedriver.exe')
scraper.fetchItemData("1005004953358516")
