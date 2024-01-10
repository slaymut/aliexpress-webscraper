import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class AliExpressItem:
  def __init__(
    self,
    id,
    title,
    price,
    shippingPrice,
    valuePrice=-1,
    deliveryTime=0,
    deliveryDates=[],
    rating=0,
    reviewsNbr=0,
    sellsNbr=0,
    freeShippingAfter=-1,
    trustScore=0, 
    trustworthiness='Highly Unworthy',
    isChoice=None,
    isPlus=None, 
    store=-1
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

  def to_dict(self):
    return {
      'id': self.id,
      'title': self.title,
      'price': self.price,
      'valuePrice': self.valuePrice,
      'shippingPrice': self.shippingPrice,
      'deliveryTime': self.deliveryTime,
      'deliveryDates': self.deliveryDates,
      'rating': self.rating,
      'reviewsNbr': self.reviewsNbr,
      'sellsNbr': self.sellsNbr,
      'freeShippingAfter': self.freeShippingAfter,
      'trustScore': self.trustScore,
      'trustworthiness': self.trustworthiness,
      'isChoice': self.isChoice,
      'isPlus': self.isPlus,
      'store': self.store
    }