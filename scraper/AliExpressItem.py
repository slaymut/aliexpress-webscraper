import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class AliExpressItem:
  def __init__(
    self,
    id,
    title,
    price,
    valuePrice,
    shippingPrice,
    deliveryTime,
    deliveryDates,
    rating,
    reviewsNbr,
    sellsNbr,
    freeShippingAfter=None,
    trustScore=0, 
    trustworthiness=None,
    isChoice=None,
    isPlus=None, 
    store=None
  ):
    self.id = id
    self.title = title
    self.price = price
    self.valuePrice = valuePrice
    self.shippingPrice = shippingPrice
    self.deliveryTime = deliveryTime
    self.deliveryDates = deliveryDates
    self.rating = rating
    self.reviewsNbr = reviewsNbr
    self.sellsNbr = sellsNbr
    self.freeShippingAfter = freeShippingAfter
    self.trustScore = trustScore
    self.trustworthiness = trustworthiness
    self.isChoice = isChoice
    self.isPlus = isPlus
    self.store = store
