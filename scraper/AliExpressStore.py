class AliExpressStore:
  def __init__(self, name, reviewPercentage, followers, trustScore, trustworthiness, isChoice, isPlus, isChoiceStore):
    self.name = name
    self.reviewPercentage = reviewPercentage
    self.followers = followers
    self.trustScore = trustScore
    self.trustworthiness = trustworthiness
    self.isChoice = isChoice
    self.isChoiceStore = isChoiceStore