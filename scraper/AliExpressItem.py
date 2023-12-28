class AliExpressItem:
  def __init__(
    self,
    title,
    price,
    valuePrice,
    rating,
    reviewsNbr,
    sellsNbr,
    trustScore=None, 
    trustworthiness=None,
    isChoice=None,
    isPlus=None, 
    store=None
  ):
    self.title = title
    self.price = price
    self.valuePrice = valuePrice
    self.rating = rating
    self.reviewsNbr = reviewsNbr
    self.sellsNbr = sellsNbr
    self.trustScore = trustScore
    self.trustworthiness = trustworthiness
    self.isChoice = isChoice
    self.isPlus = isPlus
    self.store = store
