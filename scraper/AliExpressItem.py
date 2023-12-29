class AliExpressItem:
  def __init__(
    self,
    id,
    title,
    price,
    valuePrice,
    shippingPrice,
    rating,
    reviewsNbr,
    sellsNbr,
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
    self.rating = rating
    self.reviewsNbr = reviewsNbr
    self.sellsNbr = sellsNbr
    self.trustScore = trustScore
    self.trustworthiness = trustworthiness
    self.isChoice = isChoice
    self.isPlus = isPlus
    self.store = store
