from selenium import webdriver
from bs4 import BeautifulSoup

class WebScraper:
  def __init__(self, driver_path):
    self.driver_path = driver_path
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    
    driver = webdriver.Chrome(self.driver_path, options=options)
    self.driver = driver

  def fetchItem(self, url, tag_name, class_name=None, attrs=None):
    # Navigate to the website
    self.driver.get(url)

    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    # Find the element by tag name and class name
    element = soup.find(tag_name, class_=class_name, attrs=attrs)

    # Print the text content of the element
    if element:
      return element
    else:
      print(f"No element found with tag name '{tag_name}'")
    
  def fetchMainElements(self, product_id):
    url = f"https://fr.aliexpress.com/item/{product_id}.html"
    title = self.fetchItem(url, 'h1', attrs={'data-pl': 'product-title'})
    currentPrice = self.fetchItem(url, 'div', class_name="product-price-current")
    
    print(f"Title: {title.text}")
    print(f"Current Price: {currentPrice.text}")

# # Usage example
scraper = WebScraper('C:\\Users\\slaymut\\Documents\\Web Scraper Aliexpress\\aliexpress-webscraper\\chrome-driver\\chromedriver.exe')
scraper.fetchMainElements("1005006132071310")


